from typing import Optional, List, Any, Dict, ForwardRef, TYPE_CHECKING, Annotated
from pydantic import BaseModel, HttpUrl, Field
from enum import Enum
from datetime import datetime

# Forward references
UnitResponse = ForwardRef('UnitResponse')
VideoResponse = ForwardRef('VideoResponse')
CourseResponse = ForwardRef('CourseResponse')


class VideoSourceType(str, Enum):
    YOUTUBE = "youtube"
    KHAN_ACADEMY = "khan_academy"
    LOCAL = "local"


# Base Progress Schemas
class ProgressBase(BaseModel):
    progress_percentage: float = 0
    last_accessed: datetime

    class Config:
        from_attributes = True

class CourseProgressResponse(ProgressBase):
    course_id: int
    completed_units: int
    total_units: int

class VideoProgressResponse(ProgressBase):
    video_id: int
    watched_duration: float
    total_duration: float
    last_position: float
    completed: bool

# Base Course Schema (without progress)
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: int
    order: Optional[int] = 0

class CourseResponse(CourseBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Course With Progress
class CourseWithProgress(CourseResponse):
    progress: Optional[CourseProgressResponse] = None
    videos: List[VideoProgressResponse] = []


# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class CategoryInDBBase(CategoryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Category(CategoryInDBBase):
    pass


class CategoryResponse(CategoryInDBBase):
    pass


class CategoryWithCoursesResponse(CategoryResponse):
    courses: List[Any] = Field(default_factory=list)


# Course schemas
class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    title: Optional[str] = None
    category_id: Optional[int] = None
    order: Optional[int] = None


class CourseInDBBase(CourseBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Course(CourseInDBBase):
    pass


class CourseWithUnitsResponse(CourseResponse):
    units: List[Any] = Field(default_factory=list)


# Unit schemas
class UnitBase(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: int
    order: Optional[int] = 0


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    title: Optional[str] = None
    course_id: Optional[int] = None
    order: Optional[int] = None


class UnitInDBBase(UnitBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Unit(UnitInDBBase):
    pass


class UnitResponse(UnitInDBBase):
    pass


class UnitWithVideosResponse(UnitResponse):
    videos: List[Any] = Field(default_factory=list)


# Video schemas
class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    unit_id: int
    url: str
    order: Optional[int] = 0
    video_metadata: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None


class VideoCreate(VideoBase):
    pass


class VideoUpdate(VideoBase):
    title: Optional[str] = None
    description: Optional[str] = None
    unit_id: Optional[int] = None
    url: Optional[str] = None
    order: Optional[int] = None
    video_metadata: Optional[Dict[str, Any]] = None
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None


class VideoInDBBase(VideoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Video(VideoInDBBase):
    pass


class VideoResponse(VideoInDBBase):
    pass


class VideoWithMetadataResponse(VideoResponse):
    pass


# Note schemas
class NoteBase(BaseModel):
    content: str
    video_id: int
    user_id: int


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    content: Optional[str] = None
    video_id: Optional[int] = None


class NoteInDBBase(NoteBase):
    id: int

    class Config:
        from_attributes = True


class Note(NoteInDBBase):
    pass


# Quiz schemas
class QuizQuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"


class QuizQuestionChoiceBase(BaseModel):
    text: str
    is_correct: bool = False


class QuizQuestionChoiceCreate(QuizQuestionChoiceBase):
    pass


class QuizQuestionChoiceUpdate(QuizQuestionChoiceBase):
    text: Optional[str] = None
    is_correct: Optional[bool] = None


class QuizQuestionChoiceInDBBase(QuizQuestionChoiceBase):
    id: int
    question_id: int

    class Config:
        from_attributes = True


class QuizQuestionChoice(QuizQuestionChoiceInDBBase):
    pass


class QuizQuestionBase(BaseModel):
    question_text: str
    question_type: str  # 'multiple_choice' or 'short_answer'
    choices: Optional[List[Dict[str, Any]]] = None  # For multiple choice questions


class QuizCreate(BaseModel):
    title: str
    video_id: int
    questions: List[QuizQuestionBase]


class QuizUpdate(BaseModel):
    title: Optional[str] = None
    video_id: Optional[int] = None


class QuizInDBBase(BaseModel):
    id: int
    title: str
    video_id: int
    questions: List[QuizQuestionBase]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Quiz(QuizInDBBase):
    pass


class QuizResponse(QuizInDBBase):
    pass


class QuizAttemptCreate(BaseModel):
    quiz_id: int
    responses: Dict[str, Any]


class QuizAttemptResponse(BaseModel):
    id: int
    quiz_id: int
    score: float
    completed_at: datetime
    responses: Dict[str, Any]

    class Config:
        from_attributes = True


class VideoProgressUpdate(BaseModel):
    progress: float
    last_position: float


class VideoProgressResponse(BaseModel):
    video_id: int
    progress: float
    last_position: float
    updated_at: datetime

    class Config:
        from_attributes = True


# Progress schemas
class ProgressCreate(ProgressBase):
    pass


class ProgressUpdate(ProgressBase):
    watched_seconds: Optional[float] = None
    is_completed: Optional[bool] = None
    last_position: Optional[float] = None


class ProgressInDBBase(ProgressBase):
    id: int

    class Config:
        from_attributes = True


class Progress(ProgressInDBBase):
    pass


# Learning Goal schemas
class LearningGoalBase(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    target_date: Optional[str] = None
    is_completed: bool = False


class LearningGoalCreate(LearningGoalBase):
    pass


class LearningGoalUpdate(LearningGoalBase):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[str] = None
    is_completed: Optional[bool] = None


class LearningGoalInDBBase(LearningGoalBase):
    id: int

    class Config:
        from_attributes = True


class LearningGoal(LearningGoalInDBBase):
    pass


# Learning Session schemas
class LearningSessionBase(BaseModel):
    user_id: int
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[float] = None


class LearningSessionCreate(LearningSessionBase):
    pass


class LearningSessionUpdate(LearningSessionBase):
    end_time: Optional[str] = None
    duration: Optional[float] = None


class LearningSessionInDBBase(LearningSessionBase):
    id: int

    class Config:
        from_attributes = True


class LearningSession(LearningSessionInDBBase):
    pass


# Video Processing Job schemas
class VideoProcessingJobBase(BaseModel):
    video_id: int
    status: str = "pending"
    error_message: Optional[str] = None


class VideoProcessingJobCreate(VideoProcessingJobBase):
    pass


class VideoProcessingJobUpdate(VideoProcessingJobBase):
    status: Optional[str] = None
    error_message: Optional[str] = None


class VideoProcessingJobInDBBase(VideoProcessingJobBase):
    id: int

    class Config:
        from_attributes = True


class VideoProcessingJob(VideoProcessingJobInDBBase):
    pass


# LLM Interaction schemas
class LLMInteractionBase(BaseModel):
    user_id: int
    video_id: Optional[int] = None
    query: str
    response: str


class LLMInteractionCreate(LLMInteractionBase):
    pass


class LLMInteractionInDBBase(LLMInteractionBase):
    id: int

    class Config:
        from_attributes = True


class LLMInteraction(LLMInteractionInDBBase):
    pass


class CategoryWithProgress(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    courses: List[CourseResponse] = []


# Update forward references at the end of the file
CategoryWithCoursesResponse.model_rebuild()
CourseWithUnitsResponse.model_rebuild()
UnitWithVideosResponse.model_rebuild()

# Now update the field types
CategoryWithCoursesResponse.__annotations__["courses"] = List["CourseResponse"]
CourseWithUnitsResponse.__annotations__["units"] = List["UnitResponse"]
UnitWithVideosResponse.__annotations__["videos"] = List["VideoResponse"]

# Now add the new CategoryWithProgress schema
CategoryWithProgress(id=0, name="", courses=[]) 