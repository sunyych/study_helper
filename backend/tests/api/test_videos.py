from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.models.learning import Quiz, UserQuizAttempt, UserVideoProgress
from app.core.security import create_access_token

client = TestClient(app)

def test_get_video_quiz(db, test_user, test_video):
    # Create test quiz
    quiz = Quiz(
        title="Test Quiz",
        video_id=test_video.id,
        questions=[{
            "id": 1,
            "question_text": "Test question",
            "question_type": "multiple_choice",
            "choices": [
                {"id": 1, "text": "Choice 1", "is_correct": True},
                {"id": 2, "text": "Choice 2", "is_correct": False}
            ]
        }]
    )
    db.add(quiz)
    db.commit()

    access_token = create_access_token(test_user.id)
    response = client.get(
        f"/api/v1/videos/{test_video.id}/quiz",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["title"] == "Test Quiz"

def test_submit_quiz_attempt(db, test_user, test_video):
    # Create test quiz
    quiz = Quiz(
        title="Test Quiz",
        video_id=test_video.id,
        questions=[{
            "id": 1,
            "question_text": "Test question",
            "question_type": "multiple_choice",
            "choices": [
                {"id": 1, "text": "Choice 1", "is_correct": True},
                {"id": 2, "text": "Choice 2", "is_correct": False}
            ]
        }]
    )
    db.add(quiz)
    db.commit()

    access_token = create_access_token(test_user.id)
    response = client.post(
        f"/api/v1/videos/{test_video.id}/quiz/attempt",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "quiz_id": quiz.id,
            "responses": {"1": 1}  # Correct answer
        }
    )
    
    assert response.status_code == 200
    assert response.json()["score"] == 100.0

def test_get_video_progress(db, test_user, test_video):
    access_token = create_access_token(test_user.id)
    response = client.get(
        f"/api/v1/videos/{test_video.id}/progress",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["progress"] == 0
    assert response.json()["last_position"] == 0

def test_update_video_progress(db, test_user, test_video):
    access_token = create_access_token(test_user.id)
    response = client.put(
        f"/api/v1/videos/{test_video.id}/progress",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "progress": 50.0,
            "last_position": 30.5
        }
    )
    
    assert response.status_code == 200
    assert response.json()["progress"] == 50.0
    assert response.json()["last_position"] == 30.5 