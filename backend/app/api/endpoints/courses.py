from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import shutil
from pathlib import Path

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.models.learning import Course, Unit, CourseProgress
from app.schemas.learning import (
    CourseCreate, CourseUpdate, CourseResponse, 
    UnitResponse, CourseWithUnitsResponse, CourseProgressResponse
)
from app.core.config import settings

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
def get_courses(
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all courses, optionally filtered by category.
    """
    query = db.query(Course)
    if category_id:
        query = query.filter(Course.category_id == category_id)
    
    return query.order_by(Course.order).offset(skip).limit(limit).all()

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific course by ID.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course

@router.get("/{course_id}/units", response_model=CourseWithUnitsResponse)
def get_course_units(course_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a course with all its units.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    units = db.query(Unit).filter(Unit.course_id == course_id).order_by(Unit.order).all()
    
    return {
        **course.__dict__,
        "units": units
    }

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new course (admin only).
    """
    # Check if course with same title exists in the same category
    existing_course = db.query(Course).filter(
        Course.title == course.title,
        Course.category_id == course.category_id
    ).first()
    
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this title already exists in this category"
        )
    
    # Get max order for the category
    max_order = db.query(Course).filter(
        Course.category_id == course.category_id
    ).count()
    
    db_course = Course(
        title=course.title,
        description=course.description,
        category_id=course.category_id,
        order=max_order + 1
    )
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course: CourseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a course (admin only).
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if updating to a title that already exists in the same category
    if course.title and course.title != db_course.title:
        existing_course = db.query(Course).filter(
            Course.title == course.title,
            Course.category_id == db_course.category_id,
            Course.id != course_id
        ).first()
        
        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course with this title already exists in this category"
            )
    
    # Update fields
    for key, value in course.dict(exclude_unset=True).items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a course (admin only).
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    db.delete(db_course)
    db.commit()
    return None

@router.post("/scan-directory", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def scan_directory(
    directory_path: str,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Scan a directory and create a course from its contents (admin only).
    """
    if not os.path.exists(directory_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Directory not found"
        )
    
    # Get directory name as course title
    course_title = os.path.basename(directory_path)
    
    # Check if course with same title exists in the same category
    existing_course = db.query(Course).filter(
        Course.title == course_title,
        Course.category_id == category_id
    ).first()
    
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this title already exists in this category"
        )
    
    # Create course
    db_course = Course(
        title=course_title,
        description=f"Course created from directory: {directory_path}",
        category_id=category_id,
        order=0  # Will be updated later
    )
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    # Get max order for the category
    max_order = db.query(Course).filter(
        Course.category_id == category_id
    ).count()
    
    # Update course order
    db_course.order = max_order
    db.commit()
    
    # Create units based on subdirectories
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isdir(item_path):
            # Create unit for each subdirectory
            unit_title = os.path.basename(item_path)
            
            # Check if unit with same title exists in the same course
            existing_unit = db.query(Unit).filter(
                Unit.title == unit_title,
                Unit.course_id == db_course.id
            ).first()
            
            if not existing_unit:
                # Get max order for the course
                max_unit_order = db.query(Unit).filter(
                    Unit.course_id == db_course.id
                ).count()
                
                db_unit = Unit(
                    title=unit_title,
                    description=f"Unit created from directory: {item_path}",
                    course_id=db_course.id,
                    order=max_unit_order + 1
                )
                
                db.add(db_unit)
                db.commit()
    
    return db_course 

@router.get("/{course_id}/progress", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific course."""
    progress = db.query(CourseProgress).filter(
        CourseProgress.course_id == course_id,
        CourseProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        # Create new progress entry
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
            
        total_units = len(course.units)
        progress = CourseProgress(
            user_id=current_user.id,
            course_id=course_id,
            total_units=total_units
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return progress

@router.put("/{course_id}/progress", response_model=CourseProgressResponse)
async def update_course_progress(
    course_id: int,
    completed_units: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update progress for a specific course."""
    progress = db.query(CourseProgress).filter(
        CourseProgress.course_id == course_id,
        CourseProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    
    progress.completed_units = completed_units
    progress.progress_percentage = (completed_units / progress.total_units) * 100
    
    db.commit()
    db.refresh(progress)
    return progress 