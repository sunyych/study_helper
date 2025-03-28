import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Table } from 'react-bootstrap';
import api from '../services/auth';

const Profile = ({ user, setUser }) => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState({ text: '', type: '' });
  const [learningGoals, setLearningGoals] = useState([
    { id: 1, title: 'Complete Chinese 101', targetDate: '2023-12-31', isCompleted: false },
    { id: 2, title: 'Master basic arithmetic', targetDate: '2023-10-15', isCompleted: true },
    { id: 3, title: 'Learn 500 English words', targetDate: '2023-11-30', isCompleted: false },
  ]);
  const [newGoal, setNewGoal] = useState({ title: '', targetDate: '' });
  const [showAddGoal, setShowAddGoal] = useState(false);

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      setMessage({ text: 'Passwords do not match', type: 'danger' });
      return;
    }
    
    try {
      // In a real app, we would call the API to update the password
      // await api.put('/users/me', { password });
      
      setMessage({ text: 'Password updated successfully', type: 'success' });
      setPassword('');
      setConfirmPassword('');
      
      setTimeout(() => {
        setMessage({ text: '', type: '' });
      }, 3000);
    } catch (error) {
      console.error('Error updating password:', error);
      setMessage({ 
        text: error.response?.data?.detail || 'Failed to update password', 
        type: 'danger' 
      });
    }
  };

  const handleAddGoal = (e) => {
    e.preventDefault();
    
    if (!newGoal.title || !newGoal.targetDate) return;
    
    const goal = {
      id: learningGoals.length + 1,
      title: newGoal.title,
      targetDate: newGoal.targetDate,
      isCompleted: false
    };
    
    setLearningGoals([...learningGoals, goal]);
    setNewGoal({ title: '', targetDate: '' });
    setShowAddGoal(false);
  };

  const toggleGoalStatus = (goalId) => {
    const updatedGoals = learningGoals.map(goal => {
      if (goal.id === goalId) {
        return { ...goal, isCompleted: !goal.isCompleted };
      }
      return goal;
    });
    setLearningGoals(updatedGoals);
  };

  const deleteGoal = (goalId) => {
    const updatedGoals = learningGoals.filter(goal => goal.id !== goalId);
    setLearningGoals(updatedGoals);
  };

  return (
    <Container className="mt-4">
      <h1 className="mb-4">Profile</h1>
      
      <Row>
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>User Information</Card.Header>
            <Card.Body>
              <p><strong>Username:</strong> {user?.username}</p>
              <p><strong>Role:</strong> {user?.is_admin ? 'Admin' : 'Student'}</p>
              <p><strong>Status:</strong> {user?.is_active ? 'Active' : 'Inactive'}</p>
            </Card.Body>
          </Card>
          
          <Card>
            <Card.Header>Change Password</Card.Header>
            <Card.Body>
              {message.text && (
                <Alert variant={message.type} onClose={() => setMessage({ text: '', type: '' })} dismissible>
                  {message.text}
                </Alert>
              )}
              
              <Form onSubmit={handlePasswordChange}>
                <Form.Group className="mb-3">
                  <Form.Label>New Password</Form.Label>
                  <Form.Control
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Confirm Password</Form.Label>
                  <Form.Control
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                  />
                </Form.Group>
                
                <Button type="submit" variant="primary">Update Password</Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>Learning Goals</span>
              <Button 
                variant="outline-primary" 
                size="sm"
                onClick={() => setShowAddGoal(!showAddGoal)}
              >
                {showAddGoal ? 'Cancel' : 'Add Goal'}
              </Button>
            </Card.Header>
            <Card.Body>
              {showAddGoal && (
                <Form onSubmit={handleAddGoal} className="mb-4">
                  <Form.Group className="mb-3">
                    <Form.Label>Goal Title</Form.Label>
                    <Form.Control
                      type="text"
                      value={newGoal.title}
                      onChange={(e) => setNewGoal({ ...newGoal, title: e.target.value })}
                      required
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Target Date</Form.Label>
                    <Form.Control
                      type="date"
                      value={newGoal.targetDate}
                      onChange={(e) => setNewGoal({ ...newGoal, targetDate: e.target.value })}
                      required
                    />
                  </Form.Group>
                  
                  <Button type="submit" variant="primary">Add Goal</Button>
                </Form>
              )}
              
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>Goal</th>
                    <th>Target Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {learningGoals.map(goal => (
                    <tr key={goal.id}>
                      <td className={goal.isCompleted ? 'text-decoration-line-through text-muted' : ''}>
                        {goal.title}
                      </td>
                      <td>{goal.targetDate}</td>
                      <td>
                        <span className={`badge ${goal.isCompleted ? 'bg-success' : 'bg-primary'}`}>
                          {goal.isCompleted ? 'Completed' : 'In Progress'}
                        </span>
                      </td>
                      <td>
                        <Button 
                          variant={goal.isCompleted ? 'outline-primary' : 'outline-success'} 
                          size="sm"
                          className="me-2"
                          onClick={() => toggleGoalStatus(goal.id)}
                        >
                          {goal.isCompleted ? 'Mark Incomplete' : 'Mark Complete'}
                        </Button>
                        <Button 
                          variant="outline-danger" 
                          size="sm"
                          onClick={() => deleteGoal(goal.id)}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default Profile; 