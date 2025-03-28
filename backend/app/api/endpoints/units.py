from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.models.learning import Unit, Video
from app.schemas.learning import (
    UnitCreate, UnitUpdate, UnitResponse, 
    VideoResponse, UnitWithVideosResponse
)

router = APIRouter()

@router.get("/", response_model=List[UnitResponse])
def get_units(
    skip: int = 0, 
    limit: int = 100,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all units, optionally filtered by course.
    """
    query = db.query(Unit)
    if course_id:
        query = query.filter(Unit.course_id == course_id)
    
    return query.order_by(Unit.order).offset(skip).limit(limit).all()

@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(unit_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific unit by ID.
    """
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    return unit

@router.get("/{unit_id}/videos", response_model=UnitWithVideosResponse)
def get_unit_videos(unit_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a unit with all its videos.
    """
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    videos = db.query(Video).filter(Video.unit_id == unit_id).order_by(Video.order).all()
    
    return {
        **unit.__dict__,
        "videos": videos
    }

@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new unit (admin only).
    """
    # Check if unit with same title exists in the same course
    existing_unit = db.query(Unit).filter(
        Unit.title == unit.title,
        Unit.course_id == unit.course_id
    ).first()
    
    if existing_unit:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unit with this title already exists in this course"
        )
    
    # Get max order for the course
    max_order = db.query(Unit).filter(
        Unit.course_id == unit.course_id
    ).count()
    
    db_unit = Unit(
        title=unit.title,
        description=unit.description,
        course_id=unit.course_id,
        order=max_order + 1
    )
    
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: int,
    unit: UnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a unit (admin only).
    """
    db_unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not db_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    # Check if updating to a title that already exists in the same course
    if unit.title and unit.title != db_unit.title:
        existing_unit = db.query(Unit).filter(
            Unit.title == unit.title,
            Unit.course_id == db_unit.course_id,
            Unit.id != unit_id
        ).first()
        
        if existing_unit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unit with this title already exists in this course"
            )
    
    # Update fields
    for key, value in unit.dict(exclude_unset=True).items():
        setattr(db_unit, key, value)
    
    db.commit()
    db.refresh(db_unit)
    return db_unit

@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a unit (admin only).
    """
    db_unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not db_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unit not found"
        )
    
    db.delete(db_unit)
    db.commit()
    return None

@router.post("/reorder", status_code=status.HTTP_200_OK)
def reorder_units(
    unit_orders: List[dict] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Reorder units within a course (admin only).
    
    Expects a list of dictionaries with unit_id and new order:
    [{"unit_id": 1, "order": 3}, {"unit_id": 2, "order": 1}, ...]
    """
    for item in unit_orders:
        unit_id = item.get("unit_id")
        new_order = item.get("order")
        
        if unit_id is None or new_order is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each item must contain unit_id and order"
            )
        
        db_unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if not db_unit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Unit with id {unit_id} not found"
            )
        
        db_unit.order = new_order
    
    db.commit()
    return {"message": "Units reordered successfully"} 