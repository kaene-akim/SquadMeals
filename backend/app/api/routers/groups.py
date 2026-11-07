from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_group_member
from app.core.database import get_db
from app.models import Group, GroupJoinRequest, GroupMember, GroupMessage, User
from app.schemas.common import GroupCreate, GroupDetailOut, GroupOut, MemberOut, MessageCreate, MessageOut
from app.services.geo import haversine_km

router = APIRouter(prefix="/groups", tags=["groups"])


def _group_out(g: Group, member_count: int, distance_km: float | None = None) -> GroupOut:
    return GroupOut(
        id=g.id,
        name=g.name,
        description=g.description,
        area_label=g.area_label,
        latitude=g.latitude,
        longitude=g.longitude,
        join_mode=g.join_mode,
        created_by=g.created_by,
        member_count=member_count,
        distance_km=distance_km,
    )


@router.post("", response_model=GroupOut)
def create_group(payload: GroupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    g = Group(**payload.model_dump(), created_by=current_user.id)
    db.add(g)
    db.flush()
    db.add(GroupMember(group_id=g.id, user_id=current_user.id, role="admin"))
    db.commit()
    db.refresh(g)
    return _group_out(g, 1)


@router.get("", response_model=list[GroupOut])
def list_groups(
    scope: str = "discover",  # discover|mine
    radius_km: float = 15.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if scope == "mine":
        gids = select(GroupMember.group_id).where(GroupMember.user_id == current_user.id)
        groups = db.scalars(select(Group).where(Group.id.in_(gids))).all()
        result = []
        for g in groups:
            count = db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == g.id)) or 0
            result.append(_group_out(g, count))
        return result

    groups = db.scalars(select(Group)).all()
    result = []
    for g in groups:
        distance = None
        if current_user.latitude and current_user.longitude and g.latitude and g.longitude:
            distance = haversine_km(current_user.latitude, current_user.longitude, g.latitude, g.longitude)
            if distance > radius_km:
                continue
            distance = round(distance, 2)
        elif scope == "discover":
            # include groups without coords but deprioritize
            distance = None
        count = db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == g.id)) or 0
        result.append(_group_out(g, count, distance))
    result.sort(key=lambda x: (x.distance_km is None, x.distance_km or 9999, x.name))
    return result


@router.get("/{group_id}", response_model=GroupDetailOut)
def get_group(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    count = db.scalar(select(func.count()).select_from(GroupMember).where(GroupMember.group_id == g.id)) or 0
    membership = db.scalar(select(GroupMember).where(GroupMember.group_id == g.id, GroupMember.user_id == current_user.id))
    req = db.scalar(select(GroupJoinRequest).where(GroupJoinRequest.group_id == g.id, GroupJoinRequest.user_id == current_user.id))
    distance = None
    if current_user.latitude and current_user.longitude and g.latitude and g.longitude:
        distance = round(haversine_km(current_user.latitude, current_user.longitude, g.latitude, g.longitude), 2)
    return GroupDetailOut(
        **_group_out(g, count, distance).model_dump(),
        is_member=membership is not None,
        my_role=membership.role if membership else None,
        join_request_status=req.status if req else None,
    )


@router.post("/{group_id}/join")
def join_group(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    g = db.get(Group, group_id)
    if not g:
        raise HTTPException(status_code=404, detail="Group not found")
    existing = db.scalar(select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id))
    if existing:
        return {"status": "already_member"}
    if g.join_mode == "invite":
        raise HTTPException(status_code=403, detail="This group requires an invitation")
    req = db.scalar(select(GroupJoinRequest).where(GroupJoinRequest.group_id == group_id, GroupJoinRequest.user_id == current_user.id))
    if req:
        req.status = "pending"
    else:
        db.add(GroupJoinRequest(group_id=group_id, user_id=current_user.id, status="pending"))
    db.commit()
    return {"status": "requested"}


@router.post("/{group_id}/requests/{user_id}/approve")
def approve_request(group_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = require_group_member(group_id, db, current_user)
    if membership.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    req = db.scalar(select(GroupJoinRequest).where(GroupJoinRequest.group_id == group_id, GroupJoinRequest.user_id == user_id))
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.status = "approved"
    if not db.scalar(select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)):
        db.add(GroupMember(group_id=group_id, user_id=user_id, role="member"))
    db.commit()
    return {"status": "approved"}


@router.post("/{group_id}/invite/{user_id}")
def invite_user(group_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = require_group_member(group_id, db, current_user)
    if membership.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    if not db.get(User, user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if db.scalar(select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == user_id)):
        return {"status": "already_member"}
    db.add(GroupMember(group_id=group_id, user_id=user_id, role="member"))
    db.commit()
    return {"status": "invited"}


@router.get("/{group_id}/requests")
def list_requests(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    membership = require_group_member(group_id, db, current_user)
    if membership.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    reqs = db.scalars(select(GroupJoinRequest).where(GroupJoinRequest.group_id == group_id, GroupJoinRequest.status == "pending")).all()
    result = []
    for r in reqs:
        u = db.get(User, r.user_id)
        if u:
            result.append({"user_id": u.id, "name": u.name, "location_label": u.location_label, "created_at": r.created_at})
    return result


@router.get("/{group_id}/members", response_model=list[MemberOut])
def members(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    rows = db.query(GroupMember, User).join(User, User.id == GroupMember.user_id).filter(GroupMember.group_id == group_id).all()
    return [MemberOut(id=m.id, user_id=u.id, name=u.name, profile_picture=u.profile_picture, role=m.role, joined_at=m.joined_at) for m, u in rows]


@router.get("/{group_id}/messages", response_model=list[MessageOut])
def get_messages(group_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    rows = db.query(GroupMessage, User).join(User, User.id == GroupMessage.user_id).filter(GroupMessage.group_id == group_id).order_by(GroupMessage.created_at.asc()).limit(200).all()
    return [MessageOut(id=msg.id, group_id=msg.group_id, user_id=msg.user_id, user_name=u.name, content=msg.content, created_at=msg.created_at) for msg, u in rows]


@router.post("/{group_id}/messages", response_model=MessageOut)
def post_message(group_id: int, payload: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    require_group_member(group_id, db, current_user)
    msg = GroupMessage(group_id=group_id, user_id=current_user.id, content=payload.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return MessageOut(id=msg.id, group_id=msg.group_id, user_id=msg.user_id, user_name=current_user.name, content=msg.content, created_at=msg.created_at)
