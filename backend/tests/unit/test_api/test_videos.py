import pytest
from fastapi.testclient import TestClient
from app.models.learning import Video


def test_get_videos(client):
    """Test retrieving all videos."""
    response = client.get("/videos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least the test video should be in the response
    assert len(data) >= 1


def test_get_video(client, test_video):
    """Test retrieving a specific video by ID."""
    response = client.get(f"/videos/{test_video.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_video.title
    assert data["description"] == test_video.description
    assert data["id"] == test_video.id
    assert data["unit_id"] == test_video.unit_id
    assert data["url"] == test_video.url
    assert data["order"] == test_video.order


def test_get_nonexistent_video(client):
    """Test retrieving a nonexistent video."""
    response = client.get("/videos/999999")  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_video_admin(client, admin_token_headers, db, test_unit):
    """Test creating a new video as admin."""
    video_data = {
        "title": "New Video",
        "description": "This is a new video created by the admin",
        "url": "https://example.com/new-video",
        "order": 2,
        "unit_id": test_unit.id
    }
    response = client.post("/videos/", json=video_data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Video"
    assert data["description"] == "This is a new video created by the admin"
    assert data["url"] == "https://example.com/new-video"
    assert data["order"] == 2
    assert data["unit_id"] == test_unit.id
    assert "id" in data
    
    # Check that the video was actually created in the database
    video = db.query(Video).filter(Video.title == "New Video").first()
    assert video is not None
    assert video.title == "New Video"
    assert video.description == "This is a new video created by the admin"
    assert video.url == "https://example.com/new-video"
    assert video.order == 2
    assert video.unit_id == test_unit.id


def test_create_video_regular_user(client, normal_token_headers, test_unit):
    """Test that regular users cannot create new videos."""
    video_data = {
        "title": "Unauthorized Video",
        "description": "This video should not be created",
        "url": "https://example.com/unauthorized-video",
        "order": 3,
        "unit_id": test_unit.id
    }
    response = client.post("/videos/", json=video_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_create_video_nonexistent_unit(client, admin_token_headers):
    """Test creating a video with a nonexistent unit."""
    video_data = {
        "title": "Invalid Unit Video",
        "description": "This video should not be created",
        "url": "https://example.com/invalid-unit-video",
        "order": 1,
        "unit_id": 999999  # Assuming this ID doesn't exist
    }
    response = client.post("/videos/", json=video_data, headers=admin_token_headers)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_duplicate_video(client, admin_token_headers, test_unit, test_video):
    """Test creating a video with a title that already exists in the same unit."""
    video_data = {
        "title": test_video.title,  # Same as test_video
        "description": "This is a duplicate video",
        "url": "https://example.com/duplicate-video",
        "order": 2,
        "unit_id": test_unit.id  # Same unit as test_video
    }
    response = client.post("/videos/", json=video_data, headers=admin_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_update_video_admin(client, admin_token_headers, db, test_video):
    """Test updating a video as admin."""
    update_data = {
        "title": "Updated Video",
        "description": "This is an updated video",
        "url": "https://example.com/updated-video",
        "order": 10
    }
    response = client.put(f"/videos/{test_video.id}", json=update_data, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Video"
    assert data["description"] == "This is an updated video"
    assert data["url"] == "https://example.com/updated-video"
    assert data["order"] == 10
    
    # Check that the video was actually updated in the database
    db.refresh(test_video)
    assert test_video.title == "Updated Video"
    assert test_video.description == "This is an updated video"
    assert test_video.url == "https://example.com/updated-video"
    assert test_video.order == 10


def test_update_video_regular_user(client, normal_token_headers, test_video):
    """Test that regular users cannot update videos."""
    update_data = {
        "title": "Unauthorized Update",
        "description": "This update should not be applied",
        "url": "https://example.com/unauthorized-update",
        "order": 20
    }
    response = client.put(f"/videos/{test_video.id}", json=update_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_update_nonexistent_video(client, admin_token_headers):
    """Test updating a nonexistent video."""
    update_data = {
        "title": "Update Nonexistent",
        "description": "This update should not be applied",
        "url": "https://example.com/nonexistent-update",
        "order": 5
    }
    response = client.put("/videos/999999", json=update_data, headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_delete_video_admin(client, admin_token_headers, db, test_unit):
    """Test deleting a video as admin."""
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
    video_id = video.id
    
    response = client.delete(f"/videos/{video_id}", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Video to Delete"
    
    # Check that the video was actually deleted from the database
    deleted_video = db.query(Video).filter(Video.id == video_id).first()
    assert deleted_video is None


def test_delete_video_regular_user(client, normal_token_headers, test_video):
    """Test that regular users cannot delete videos."""
    response = client.delete(f"/videos/{test_video.id}", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_delete_nonexistent_video(client, admin_token_headers):
    """Test deleting a nonexistent video."""
    response = client.delete("/videos/999999", headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_video_with_metadata(client, db, test_unit):
    """Test retrieving a video with metadata."""
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
    
    response = client.get(f"/videos/{video.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Metadata Video"
    assert data["duration_seconds"] == 120
    assert data["thumbnail_url"] == "https://example.com/thumbnail.jpg"
    assert "video_metadata" in data
    assert data["video_metadata"]["author"] == "Test Author"
    assert "tags" in data["video_metadata"]
    assert "test" in data["video_metadata"]["tags"]


def test_reorder_videos_admin(client, admin_token_headers, db, test_unit):
    """Test reordering videos as admin."""
    # Create multiple videos to reorder
    video1 = Video(
        title="Reorder Video 1",
        description="This is the first video to reorder",
        url="https://example.com/reorder-1",
        order=1,
        unit_id=test_unit.id
    )
    video2 = Video(
        title="Reorder Video 2",
        description="This is the second video to reorder",
        url="https://example.com/reorder-2",
        order=2,
        unit_id=test_unit.id
    )
    video3 = Video(
        title="Reorder Video 3",
        description="This is the third video to reorder",
        url="https://example.com/reorder-3",
        order=3,
        unit_id=test_unit.id
    )
    db.add_all([video1, video2, video3])
    db.commit()
    
    # New order: video3, video1, video2
    reorder_data = {
        "video_ids": [video3.id, video1.id, video2.id]
    }
    
    response = client.post(f"/units/{test_unit.id}/reorder-videos", json=reorder_data, headers=admin_token_headers)
    assert response.status_code == 200
    
    # Check that the videos were actually reordered in the database
    db.refresh(video1)
    db.refresh(video2)
    db.refresh(video3)
    assert video3.order == 1
    assert video1.order == 2
    assert video2.order == 3 