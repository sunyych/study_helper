import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, ProgressBar, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../services/auth';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [recentVideos, setRecentVideos] = useState([]);
  const [progress, setProgress] = useState([]);
  const [learningGoals, setLearningGoals] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // Fetch categories
        const categoriesResponse = await api.get('/categories');
        setCategories(categoriesResponse.data);

        // In a real app, we would fetch these from the API
        // For now, we'll use placeholder data
        setRecentVideos([
          { id: 1, title: 'Introduction to Chinese Characters', unit: 'Basic Chinese', course: 'Chinese 101', thumbnail: 'https://via.placeholder.com/150', progress: 75 },
          { id: 2, title: 'Basic Math Operations', unit: 'Arithmetic', course: 'Math Fundamentals', thumbnail: 'https://via.placeholder.com/150', progress: 100 },
          { id: 3, title: 'English Grammar Rules', unit: 'Grammar', course: 'English Basics', thumbnail: 'https://via.placeholder.com/150', progress: 30 },
        ]);

        setProgress([
          { id: 1, course: 'Chinese 101', completed: 12, total: 20, percentage: 60 },
          { id: 2, course: 'Math Fundamentals', completed: 8, total: 15, percentage: 53 },
          { id: 3, course: 'English Basics', completed: 5, total: 25, percentage: 20 },
        ]);

        setLearningGoals([
          { id: 1, title: 'Complete Chinese 101', targetDate: '2023-12-31', isCompleted: false },
          { id: 2, title: 'Master basic arithmetic', targetDate: '2023-10-15', isCompleted: true },
          { id: 3, title: 'Learn 500 English words', targetDate: '2023-11-30', isCompleted: false },
        ]);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        setError('Failed to load dashboard data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const renderCourseProgress = (course) => {
    if (!course.progress) return null;
    
    return (
      <div className="mt-2">
        <small className="text-muted">
          Progress: {course.progress.completed_units} / {course.progress.total_units} units
        </small>
        <ProgressBar 
          now={course.progress.progress_percentage} 
          label={`${Math.round(course.progress.progress_percentage)}%`}
          variant={course.progress.progress_percentage === 100 ? "success" : "primary"}
        />
      </div>
    );
  };

  if (loading) {
    return <Container className="mt-4"><div>Loading dashboard...</div></Container>;
  }

  if (error) {
    return <Container className="mt-4"><div className="text-danger">{error}</div></Container>;
  }

  return (
    <Container className="mt-4">
      <h1 className="mb-4">Dashboard</h1>

      {/* Recent Videos */}
      <h2 className="mb-3">Continue Learning</h2>
      <Row className="mb-5">
        {recentVideos.map(video => (
          <Col md={4} key={video.id}>
            <Card className="h-100">
              <Card.Img variant="top" src={video.thumbnail} />
              <Card.Body>
                <Card.Title>{video.title}</Card.Title>
                <Card.Text>
                  {video.course} - {video.unit}
                </Card.Text>
                <ProgressBar 
                  now={video.progress} 
                  label={`${video.progress}%`} 
                  variant={video.progress === 100 ? "success" : "primary"}
                  className="mb-3"
                />
                <Button as={Link} to={`/video/${video.id}`} variant="primary">Continue</Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Course Progress */}
      <h2 className="mb-3">Your Progress</h2>
      <Row className="mb-5">
        {progress.map(course => (
          <Col md={4} key={course.id}>
            <Card className="h-100">
              <Card.Body>
                <Card.Title>{course.course}</Card.Title>
                <Card.Text>
                  Completed {course.completed} of {course.total} lessons
                </Card.Text>
                <ProgressBar 
                  now={course.percentage} 
                  label={`${course.percentage}%`} 
                  variant={course.percentage === 100 ? "success" : "primary"}
                  className="mb-3"
                />
                <Button as={Link} to={`/course/${course.id}`} variant="outline-primary">View Course</Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Learning Goals */}
      <Row className="mb-4">
        <Col md={6}>
          <h2 className="mb-3">Learning Goals</h2>
          <Card>
            <Card.Body>
              <ul className="list-group list-group-flush">
                {learningGoals.map(goal => (
                  <li key={goal.id} className="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <span className={goal.isCompleted ? 'text-decoration-line-through text-muted' : ''}>
                        {goal.title}
                      </span>
                      <br />
                      <small className="text-muted">Target: {goal.targetDate}</small>
                    </div>
                    {goal.isCompleted ? (
                      <span className="badge bg-success rounded-pill">Completed</span>
                    ) : (
                      <span className="badge bg-primary rounded-pill">In Progress</span>
                    )}
                  </li>
                ))}
              </ul>
              <div className="mt-3">
                <Button variant="outline-primary" size="sm">Add New Goal</Button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Categories */}
        <Col md={6}>
          <h2 className="mb-3">Categories</h2>
          <Card>
            <Card.Body>
              <Row>
                {categories.map(category => (
                  <Col md={6} key={category.id} className="mb-3">
                    <Card className="h-100">
                      <Card.Body className="d-flex flex-column">
                        <Card.Title>{category.name}</Card.Title>
                        <Card.Text className="flex-grow-1">
                          {category.description}
                        </Card.Text>
                        <Button 
                          as={Link} 
                          to={`/courses/${category.id}`} 
                          variant="outline-primary"
                          size="sm"
                        >
                          Browse Courses
                        </Button>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard; 