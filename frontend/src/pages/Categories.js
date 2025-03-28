import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import api from '../services/auth';

const Categories = () => {
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchCategories = async () => {
      setLoading(true);
      try {
        const response = await api.get('/categories');
        setCategories(response.data);
      } catch (error) {
        console.error('Error fetching categories:', error);
        setError('Failed to load categories. Please try again later.');
        
        // Fallback to sample data if API fails
        setCategories([
          { id: 1, name: 'Chinese', description: 'Learning resources for Chinese' },
          { id: 2, name: 'Math', description: 'Learning resources for Math' },
          { id: 3, name: 'English', description: 'Learning resources for English' },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) {
    return <Container className="mt-4"><div>Loading categories...</div></Container>;
  }

  if (error) {
    return <Container className="mt-4"><div className="text-danger">{error}</div></Container>;
  }

  return (
    <Container className="mt-4">
      <h1 className="mb-4">Categories</h1>
      <p className="lead mb-4">Browse our learning categories and find courses that interest you.</p>
      
      <Row>
        {categories.map(category => (
          <Col md={4} key={category.id} className="mb-4">
            <Card className="h-100">
              <Card.Body className="d-flex flex-column">
                <Card.Title>{category.name}</Card.Title>
                <Card.Text className="flex-grow-1">
                  {category.description}
                </Card.Text>
                <Button 
                  as={Link} 
                  to={`/courses/${category.id}`} 
                  variant="primary"
                >
                  Browse Courses
                </Button>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default Categories; 