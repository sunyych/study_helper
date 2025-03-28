import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Alert, ListGroup, Badge, ProgressBar } from 'react-bootstrap';
import api from '../services/auth';

const CourseDetail = () => {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [lessons, setLessons] = useState([]);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Fetch course details
        const courseResponse = await api.get(`/courses/${courseId}`);
        setCourse(courseResponse.data);
        
        // Fetch lessons for this course
        const lessonsResponse = await api.get(`/courses/${courseId}/lessons`);
        setLessons(lessonsResponse.data);
        
        // Fetch user progress for this course
        const progressResponse = await api.get(`/courses/${courseId}/progress`);
        setProgress(progressResponse.data.progress || 0);
      } catch (error) {
        console.error('Error fetching course details:', error);
        setError('Failed to load course details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourseDetails();
  }, [courseId]);

  if (loading) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading course details...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  if (!course) {
    return (
      <Container className="py-5">
        <Alert variant="warning">Course not found.</Alert>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <Row className="mb-4">
        <Col md={8}>
          <h2>{course.title}</h2>
          <p className="text-muted">{course.description}</p>
          
          <div className="mb-3">
            <strong>Your Progress:</strong>
            <ProgressBar 
              now={progress} 
              label={`${progress}%`} 
              variant="success" 
              className="mt-2" 
            />
          </div>
        </Col>
        <Col md={4}>
          <Card className="shadow-sm">
            <Card.Img 
              variant="top" 
              src={course.image_url || 'https://via.placeholder.com/400x200?text=Course+Image'} 
              alt={course.title}
            />
            <Card.Body>
              <div className="d-grid gap-2">
                {progress === 0 ? (
                  <Button 
                    variant="primary" 
                    as={Link} 
                    to={lessons.length > 0 ? `/video/${lessons[0].id}` : '#'}
                    disabled={lessons.length === 0}
                  >
                    Start Course
                  </Button>
                ) : (
                  <Button 
                    variant="success" 
                    as={Link} 
                    to={`/video/${lessons.find(lesson => !lesson.completed)?.id || lessons[0].id}`}
                  >
                    Continue Learning
                  </Button>
                )}
              </div>
            </Card.Body>
            <Card.Footer>
              <small className="text-muted">
                {lessons.length} lessons • {course.duration || 'Self-paced'}
              </small>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
      
      <h3 className="mb-3">Course Content</h3>
      {lessons.length === 0 ? (
        <Alert variant="info">No lessons available for this course yet.</Alert>
      ) : (
        <ListGroup className="mb-4">
          {lessons.map((lesson, index) => (
            <ListGroup.Item 
              key={lesson.id}
              className="d-flex justify-content-between align-items-center"
            >
              <div>
                <span className="me-2">{index + 1}.</span>
                <Link to={`/video/${lesson.id}`} className="text-decoration-none">
                  {lesson.title}
                </Link>
                {lesson.completed && (
                  <Badge bg="success" className="ms-2">Completed</Badge>
                )}
              </div>
              <span className="text-muted">{lesson.duration || '10 min'}</span>
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
    </Container>
  );
};

export default CourseDetail; 