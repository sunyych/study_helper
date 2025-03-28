from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_active_admin
from app.core.database import get_db
from app.models.user import User
from app.models.learning import Category, CourseProgress, VideoProgress
from app.schemas.learning import Category as CategorySchema, CategoryCreate, CategoryUpdate, CourseResponse, CategoryWithProgress

router = APIRouter()


@router.get("/", response_model=List[CategoryWithProgress])
async def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all categories with course progress."""
    categories = db.query(Category).all()
    
    # Get all progress data for the user
    course_progress = {
        cp.course_id: cp for cp in db.query(CourseProgress).filter(
            CourseProgress.user_id == current_user.id
        ).all()
    }
    
    video_progress = {
        vp.video_id: vp for vp in db.query(VideoProgress).filter(
            VideoProgress.user_id == current_user.id
        ).all()
    }
    
    result = []
    for category in categories:
        category_data = category.__dict__
        category_data['courses'] = []
        
        for course in category.courses:
            course_data = course.__dict__
            course_data['progress'] = course_progress.get(course.id)
            course_data['videos'] = [
                video_progress.get(video.id) for video in course.videos
            ]
            category_data['courses'].append(course_data)
            
        result.append(category_data)
    
    return result


@router.post("/", response_model=CategorySchema, status_code=201)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Create new category.
    """
# Check if a category with the same name already exists
    existing_category = db.query(Category).filter(Category.name == category_in.name).first()
    if existing_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists")
    category = Category(
        name=category_in.name,
        description=category_in.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Update a category.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategorySchema)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Get category by ID.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", response_model=CategorySchema)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: User = Depends(get_current_active_admin),
) -> Any:
    """
    Delete a category.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return category


@router.get("/{category_id}/courses", response_model=List[CourseResponse])
def get_category_courses(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Get courses for a specific category.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category.courses
