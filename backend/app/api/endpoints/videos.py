from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User
from app.models.learning import Video, VideoProgress
from app.models.quiz import Quiz, QuizAttempt
from app.schemas.learning import (
    VideoCreate, VideoUpdate, VideoResponse, VideoWithMetadataResponse,
    QuizResponse, QuizAttemptCreate, QuizAttemptResponse,
    VideoProgressResponse, VideoProgressUpdate,
)

router = APIRouter()

@router.get("/", response_model=List[VideoResponse])
def get_videos(
    skip: int = 0, 
    limit: int = 100,
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve all videos, optionally filtered by unit.
    """
    query = db.query(Video)
    if unit_id:
        query = query.filter(Video.unit_id == unit_id)
    
    return query.order_by(Video.order).offset(skip).limit(limit).all()

@router.get("/{video_id}", response_model=VideoResponse)
def get_video(video_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific video by ID.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    return video

@router.get("/{video_id}/metadata", response_model=VideoWithMetadataResponse)
def get_video_with_metadata(video_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a video with its metadata.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    return video

@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
def create_video(
    video: VideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new video (admin only).
    """
    # Check if video with same title exists in the same unit
    existing_video = db.query(Video).filter(
        Video.title == video.title,
        Video.unit_id == video.unit_id
    ).first()
    
    if existing_video:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Video with this title already exists in this unit"
        )
    
    # Get max order for the unit
    max_order = db.query(Video).filter(
        Video.unit_id == video.unit_id
    ).count()
    
    db_video = Video(
        title=video.title,
        description=video.description,
        url=video.url,
        unit_id=video.unit_id,
        order=max_order + 1,
        video_metadata=video.video_metadata or {}
    )
    
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

@router.put("/{video_id}", response_model=VideoResponse)
def update_video(
    video_id: int,
    video: VideoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a video (admin only).
    """
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Check if updating to a title that already exists in the same unit
    if video.title and video.title != db_video.title:
        existing_video = db.query(Video).filter(
            Video.title == video.title,
            Video.unit_id == db_video.unit_id,
            Video.id != video_id
        ).first()
        
        if existing_video:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Video with this title already exists in this unit"
            )
    
    # Update fields
    update_data = video.dict(exclude_unset=True)
    
    # Special handling for video_metadata to merge instead of replace
    if "video_metadata" in update_data:
        if db_video.video_metadata is None:
            db_video.video_metadata = {}
        db_video.video_metadata.update(update_data.pop("video_metadata", {}))
    
    # Update other fields
    for key, value in update_data.items():
        setattr(db_video, key, value)
    
    db.commit()
    db.refresh(db_video)
    return db_video

@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_video(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a video (admin only).
    """
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if not db_video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    db.delete(db_video)
    db.commit()
    return None

@router.post("/reorder", status_code=status.HTTP_200_OK)
def reorder_videos(
    video_orders: List[dict] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Reorder videos within a unit (admin only).
    
    Expects a list of dictionaries with video_id and new order:
    [{"video_id": 1, "order": 3}, {"video_id": 2, "order": 1}, ...]
    """
    for item in video_orders:
        video_id = item.get("video_id")
        new_order = item.get("order")
        
        if video_id is None or new_order is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each item must contain video_id and order"
            )
        
        db_video = db.query(Video).filter(Video.id == video_id).first()
        if not db_video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video with id {video_id} not found"
            )
        
        db_video.order = new_order
    
    db.commit()
    return {"message": "Videos reordered successfully"}

@router.get("/{video_id}/quiz", response_model=QuizResponse)
def get_video_quiz(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quiz for a specific video."""
    quiz = db.query(Quiz).filter(Quiz.video_id == video_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    return quiz

@router.post("/{video_id}/quiz/attempt", response_model=QuizAttemptResponse)
def submit_quiz_attempt(
    video_id: int,
    attempt: QuizAttemptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a quiz attempt."""
    quiz = db.query(Quiz).filter(Quiz.video_id == video_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    # Calculate score
    score = calculate_quiz_score(quiz, attempt.responses)
    
    # Create attempt record
    db_attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        responses=attempt.responses,
        score=score
    )
    
    db.add(db_attempt)
    db.commit()
    db.refresh(db_attempt)
    return db_attempt

@router.get("/{video_id}/progress", response_model=VideoProgressResponse)
def get_video_progress(
    video_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's progress for a specific video."""
    progress = db.query(VideoProgress).filter(
        VideoProgress.video_id == video_id,
        VideoProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        progress = VideoProgress(
            user_id=current_user.id,
            video_id=video_id
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    return progress

@router.put("/{video_id}/progress", response_model=VideoProgressResponse)
def update_video_progress(
    video_id: int,
    progress_update: VideoProgressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user's progress for a specific video."""
    progress = db.query(VideoProgress).filter(
        VideoProgress.video_id == video_id,
        VideoProgress.user_id == current_user.id
    ).first()
    
    if not progress:
        progress = VideoProgress(
            user_id=current_user.id,
            video_id=video_id
        )
        db.add(progress)
    
    progress.progress = progress_update.progress
    progress.last_position = progress_update.last_position
    
    db.commit()
    db.refresh(progress)
    return progress

def calculate_quiz_score(quiz: Quiz, responses: Dict[str, Any]) -> float:
    """Calculate quiz score based on responses."""
    correct_answers = 0
    total_questions = len(quiz.questions)
    
    for question in quiz.questions:
        question_id = str(question['id'])
        if question_id not in responses:
            continue
            
        if question['question_type'] == 'multiple_choice':
            # For multiple choice, check if selected answer is correct
            selected_choice = responses[question_id]
            correct_choice = next(
                (choice for choice in question['choices'] if choice['is_correct']),
                None
            )
            if correct_choice and selected_choice == correct_choice['id']:
                correct_answers += 1
        else:
            # For short answer, we could implement more sophisticated checking
            # For now, just check if an answer was provided
            if responses[question_id].strip():
                correct_answers += 1
    
    return (correct_answers / total_questions) * 100 if total_questions > 0 else 0 