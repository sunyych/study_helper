import pytest
from sqlalchemy.exc import IntegrityError
from app.models.learning import Video


def test_create_video(db, test_unit):
    """Test creating a video."""
    video = Video(
        title="New Test Video",
        description="This is a new test video",
        url="https://example.com/new-test-video",
        order=1,
        unit_id=test_unit.id
    )
    db.add(video)
    db.commit()
    
    retrieved_video = db.query(Video).filter(Video.title == "New Test Video").first()
    assert retrieved_video is not None
    assert retrieved_video.title == "New Test Video"
    assert retrieved_video.description == "This is a new test video"
    assert retrieved_video.url == "https://example.com/new-test-video"
    assert retrieved_video.order == 1
    assert retrieved_video.unit_id == test_unit.id


def test_video_unique_title_per_unit(db, test_unit, test_video):
    """Test that video title must be unique per unit."""
    with pytest.raises(IntegrityError):
        # Create a video with the same title in the same unit
        video = Video(
            title="Test Video",  # Same as test_video fixture
            description="This is a duplicate video",
            url="https://example.com/duplicate-video",
            order=2,
            unit_id=test_unit.id  # Same unit as test_video
        )
        db.add(video)
        db.commit()
    
    # Rollback to clean up
    db.rollback()


def test_video_same_title_different_unit(db, test_unit, test_video):
    """Test that same video title is allowed in different units."""
    # Get a different unit
    different_unit = db.query(Video).filter(Video.id == test_video.id).first()
    unit_id = different_unit.unit_id
    
    # Create a new unit with a different ID
    new_unit = db.query(Video).filter(Video.id != test_video.id).first().unit
    
    # Verify that unit_id and new_unit.id are different
    assert unit_id != new_unit.id
    
    # Create a video with the same title but in a different unit
    video = Video(
        title="Test Video",  # Same as test_video fixture
        description="This is a video with the same title but in a different unit",
        url="https://example.com/different-unit-video",
        order=1,
        unit_id=new_unit.id
    )
    db.add(video)
    db.commit()
    
    # Verify that both videos exist
    videos = db.query(Video).filter(Video.title == "Test Video").all()
    assert len(videos) >= 2
    # Ensure we have videos in different units
    unit_ids = {v.unit_id for v in videos}
    assert len(unit_ids) >= 2


def test_update_video(db, test_video):
    """Test updating a video."""
    # Update the video
    test_video.title = "Updated Video"
    test_video.description = "This is an updated video"
    test_video.url = "https://example.com/updated-video"
    test_video.order = 99
    db.commit()
    
    # Verify changes
    updated_video = db.query(Video).filter(Video.id == test_video.id).first()
    assert updated_video.title == "Updated Video"
    assert updated_video.description == "This is an updated video"
    assert updated_video.url == "https://example.com/updated-video"
    assert updated_video.order == 99


def test_delete_video(db, test_unit):
    """Test deleting a video."""
    # Create a video to delete
    video = Video(
        title="Video to Delete",
        description="This video will be deleted",
        url="https://example.com/video-to-delete",
        order=3,
        unit_id=test_unit.id
    )
    db.add(video)
    db.commit()
    
    # Get the ID before deletion
    video_id = video.id
    
    # Delete the video
    db.delete(video)
    db.commit()
    
    # Verify deletion
    deleted_video = db.query(Video).filter(Video.id == video_id).first()
    assert deleted_video is None


def test_video_metadata(db, test_unit):
    """Test video with metadata."""
    # Create a video with metadata
    video = Video(
        title="Metadata Video",
        description="This video has metadata",
        url="https://example.com/metadata-video",
        order=4,
        unit_id=test_unit.id,
        duration_seconds=120,
        thumbnail_url="https://example.com/thumbnail.jpg",
        video_metadata={"author": "Test Author", "tags": ["test", "video", "metadata"]}
    )
    db.add(video)
    db.commit()
    
    # Retrieve the video and check metadata
    retrieved_video = db.query(Video).filter(Video.title == "Metadata Video").first()
    assert retrieved_video.duration_seconds == 120
    assert retrieved_video.thumbnail_url == "https://example.com/thumbnail.jpg"
    assert retrieved_video.video_metadata["author"] == "Test Author"
    assert "tags" in retrieved_video.video_metadata
    assert "test" in retrieved_video.video_metadata["tags"]


def test_repr_method(db, test_unit):
    """Test the __repr__ method."""
    video = Video(
        title="ReprTest",
        description="Testing the repr method",
        url="https://example.com/repr-test",
        order=1,
        unit_id=test_unit.id
    )
    
    # Test the __repr__ method
    assert str(video) == "<Video ReprTest>" 