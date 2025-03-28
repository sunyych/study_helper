import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Alert } from 'react-bootstrap';
import api from '../services/auth';

const Courses = () => {
  const { categoryId } = useParams();
  const [courses, setCourses] = useState([]);
  const [category, setCategory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        setError('');
        
        // Fetch category details
        const categoryResponse = await api.get(`/categories/${categoryId}`);
        setCategory(categoryResponse.data);
        
        // Fetch courses for this category
        const coursesResponse = await api.get(`/categories/${categoryId}/courses`);
        setCourses(coursesResponse.data);
      } catch (error) {
        console.error('Error fetching courses:', error);
        setError('Failed to load courses. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [categoryId]);

  if (loading) {
    return (
      <Container className="py-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading courses...</p>
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

  return (
    <Container className="py-4">
      <h2 className="mb-4">{category?.name} Courses</h2>
      <p className="text-muted mb-4">{category?.description}</p>
      
      {courses.length === 0 ? (
        <Alert variant="info">No courses available in this category yet.</Alert>
      ) : (
        <Row xs={1} md={2} lg={3} className="g-4">
          {courses.map(course => (
            <Col key={course.id}>
              <Card className="h-100 shadow-sm">
                <Card.Img 
                  variant="top" 
                  src={course.image_url || 'https://via.placeholder.com/300x150?text=Course+Image'} 
                  alt={course.title}
                />
                <Card.Body className="d-flex flex-column">
                  <Card.Title>{course.title}</Card.Title>
                  <Card.Text className="text-muted mb-2">
                    {course.description.length > 100 
                      ? `${course.description.substring(0, 100)}...` 
                      : course.description}
                  </Card.Text>
                  <div className="mt-auto">
                    <Link to={`/course/${course.id}`}>
                      <Button variant="primary" className="w-100">View Course</Button>
                    </Link>
                  </div>
                </Card.Body>
                <Card.Footer className="text-muted">
                  <small>{course.lessons_count} lessons</small>
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Container>
  );
};

export default Courses; 