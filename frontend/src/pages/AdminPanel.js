import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Nav, Tab, Form, Button, Table, Alert, ProgressBar, Spinner } from 'react-bootstrap';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import api from '../services/auth';

const AdminPanel = () => {
  return (
    <Container className="mt-4">
      <h1 className="mb-4">Admin Panel</h1>
      
      <Tab.Container defaultActiveKey="users">
        <Row>
          <Col md={3}>
            <Card className="mb-4">
              <Card.Header>Admin Menu</Card.Header>
              <Card.Body className="p-0">
                <Nav variant="pills" className="flex-column">
                  <Nav.Item>
                    <Nav.Link as={Link} to="/admin/users" eventKey="users">User Management</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link as={Link} to="/admin/categories" eventKey="categories">Categories</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link as={Link} to="/admin/courses" eventKey="courses">Courses</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link as={Link} to="/admin/videos" eventKey="videos">Videos</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link as={Link} to="/admin/processing" eventKey="processing">Video Processing</Nav.Link>
                  </Nav.Item>
                  <Nav.Item>
                    <Nav.Link as={Link} to="/admin/progress" eventKey="progress">
                      Progress Tracking
                    </Nav.Link>
                  </Nav.Item>
                </Nav>
              </Card.Body>
            </Card>
          </Col>
          <Col md={9}>
            <Card>
              <Card.Body>
                <Routes>
                  <Route path="/" element={<UserManagement />} />
                  <Route path="/users" element={<UserManagement />} />
                  <Route path="/categories" element={<CategoryManagement />} />
                  <Route path="/courses" element={<CourseManagement />} />
                  <Route path="/videos" element={<VideoManagement />} />
                  <Route path="/processing" element={<VideoProcessing />} />
                  <Route path="/progress" element={<ProgressTracking />} />
                </Routes>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Tab.Container>
    </Container>
  );
};

const UserManagement = () => {
  const [users, setUsers] = useState([
    { id: 1, username: 'admin', is_active: true, is_admin: true },
    { id: 2, username: 'student1', is_active: true, is_admin: false },
    { id: 3, username: 'student2', is_active: false, is_admin: false },
  ]);
  const [newUser, setNewUser] = useState({ username: '', password: '', is_admin: false });
  const [message, setMessage] = useState({ text: '', type: '' });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewUser({
      ...newUser,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleCreateUser = (e) => {
    e.preventDefault();
    // In a real app, we would call the API to create the user
    const newUserId = users.length + 1;
    const createdUser = {
      id: newUserId,
      username: newUser.username,
      is_active: true,
      is_admin: newUser.is_admin
    };
    
    setUsers([...users, createdUser]);
    setNewUser({ username: '', password: '', is_admin: false });
    setMessage({ text: 'User created successfully!', type: 'success' });
    
    setTimeout(() => {
      setMessage({ text: '', type: '' });
    }, 3000);
  };

  const toggleUserStatus = (userId) => {
    const updatedUsers = users.map(user => {
      if (user.id === userId) {
        return { ...user, is_active: !user.is_active };
      }
      return user;
    });
    setUsers(updatedUsers);
  };

  return (
    <div>
      <h2 className="mb-4">User Management</h2>
      
      {message.text && (
        <Alert variant={message.type} onClose={() => setMessage({ text: '', type: '' })} dismissible>
          {message.text}
        </Alert>
      )}
      
      <h4>Create New User</h4>
      <Form onSubmit={handleCreateUser} className="mb-4">
        <Row>
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                name="username"
                value={newUser.username}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
          </Col>
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Password</Form.Label>
              <Form.Control
                type="password"
                name="password"
                value={newUser.password}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
          </Col>
          <Col md={4}>
            <Form.Group className="mb-3 mt-4">
              <Form.Check
                type="checkbox"
                label="Admin User"
                name="is_admin"
                checked={newUser.is_admin}
                onChange={handleInputChange}
              />
            </Form.Group>
          </Col>
        </Row>
        <Button type="submit" variant="primary">Create User</Button>
      </Form>
      
      <h4>User List</h4>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Status</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.id}</td>
              <td>{user.username}</td>
              <td>
                <span className={`badge ${user.is_active ? 'bg-success' : 'bg-danger'}`}>
                  {user.is_active ? 'Active' : 'Inactive'}
                </span>
              </td>
              <td>
                <span className={`badge ${user.is_admin ? 'bg-warning' : 'bg-info'}`}>
                  {user.is_admin ? 'Admin' : 'Student'}
                </span>
              </td>
              <td>
                <Button 
                  variant={user.is_active ? 'outline-danger' : 'outline-success'} 
                  size="sm"
                  onClick={() => toggleUserStatus(user.id)}
                >
                  {user.is_active ? 'Deactivate' : 'Activate'}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
};

const CategoryManagement = () => {
  const [categories, setCategories] = useState([
    { id: 1, name: 'Chinese', description: 'Learning resources for Chinese' },
    { id: 2, name: 'Math', description: 'Learning resources for Math' },
    { id: 3, name: 'English', description: 'Learning resources for English' },
  ]);
  const [newCategory, setNewCategory] = useState({ name: '', description: '' });
  const [message, setMessage] = useState({ text: '', type: '' });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCategory({
      ...newCategory,
      [name]: value
    });
  };

  const handleCreateCategory = (e) => {
    e.preventDefault();
    // In a real app, we would call the API to create the category
    const newCategoryId = categories.length + 1;
    const createdCategory = {
      id: newCategoryId,
      name: newCategory.name,
      description: newCategory.description
    };
    
    setCategories([...categories, createdCategory]);
    setNewCategory({ name: '', description: '' });
    setMessage({ text: 'Category created successfully!', type: 'success' });
    
    setTimeout(() => {
      setMessage({ text: '', type: '' });
    }, 3000);
  };

  const deleteCategory = (categoryId) => {
    const updatedCategories = categories.filter(category => category.id !== categoryId);
    setCategories(updatedCategories);
    setMessage({ text: 'Category deleted successfully!', type: 'success' });
    
    setTimeout(() => {
      setMessage({ text: '', type: '' });
    }, 3000);
  };

  return (
    <div>
      <h2 className="mb-4">Category Management</h2>
      
      {message.text && (
        <Alert variant={message.type} onClose={() => setMessage({ text: '', type: '' })} dismissible>
          {message.text}
        </Alert>
      )}
      
      <h4>Create New Category</h4>
      <Form onSubmit={handleCreateCategory} className="mb-4">
        <Row>
          <Col md={4}>
            <Form.Group className="mb-3">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="text"
                name="name"
                value={newCategory.name}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
          </Col>
          <Col md={8}>
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                type="text"
                name="description"
                value={newCategory.description}
                onChange={handleInputChange}
                required
              />
            </Form.Group>
          </Col>
        </Row>
        <Button type="submit" variant="primary">Create Category</Button>
      </Form>
      
      <h4>Category List</h4>
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Description</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {categories.map(category => (
            <tr key={category.id}>
              <td>{category.id}</td>
              <td>{category.name}</td>
              <td>{category.description}</td>
              <td>
                <Button 
                  variant="outline-danger" 
                  size="sm"
                  onClick={() => deleteCategory(category.id)}
                >
                  Delete
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
};

const CourseManagement = () => {
  const [courses, setCourses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [newCourse, setNewCourse] = useState({ title: '', description: '', category_id: '' });
  const [scanDirectory, setScanDirectory] = useState({ directory_path: '', category_id: '' });
  const [message, setMessage] = useState({ text: '', type: '' });
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    // Fetch courses and categories
    const fetchData = async () => {
      try {
        const [coursesResponse, categoriesResponse] = await Promise.all([
          api.get('/courses'),
          api.get('/categories')
        ]);
        setCourses(coursesResponse.data);
        setCategories(categoriesResponse.data);
      } catch (error) {
        console.error('Error fetching data:', error);
        setMessage({ text: 'Failed to load data', type: 'danger' });
      }
    };

    fetchData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewCourse({
      ...newCourse,
      [name]: value
    });
  };

  const handleScanInputChange = (e) => {
    const { name, value } = e.target;
    setScanDirectory({
      ...scanDirectory,
      [name]: value
    });
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/courses', newCourse);
      setCourses([...courses, response.data]);
      setNewCourse({ title: '', description: '', category_id: '' });
      setMessage({ text: 'Course created successfully!', type: 'success' });
    } catch (error) {
      console.error('Error creating course:', error);
      setMessage({ text: 'Failed to create course', type: 'danger' });
    }
  };

  const handleScanDirectory = async (e) => {
    e.preventDefault();
    if (!scanDirectory.directory_path || !scanDirectory.category_id) {
      setMessage({ text: 'Please fill in all fields', type: 'warning' });
      return;
    }

    setIsScanning(true);
    try {
      const response = await api.post('/courses/scan-directory', {
        directory_path: scanDirectory.directory_path,
        category_id: parseInt(scanDirectory.category_id)
      });
      setCourses([...courses, response.data]);
      setScanDirectory({ directory_path: '', category_id: '' });
      setMessage({ text: 'Course created from directory successfully!', type: 'success' });
    } catch (error) {
      console.error('Error scanning directory:', error);
      setMessage({ text: error.response?.data?.detail || 'Failed to scan directory', type: 'danger' });
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div>
      <h2 className="mb-4">Course Management</h2>
      
      {message.text && (
        <Alert variant={message.type} onClose={() => setMessage({ text: '', type: '' })} dismissible>
          {message.text}
        </Alert>
      )}
      
      <Card className="mb-4">
        <Card.Header>Create New Course</Card.Header>
        <Card.Body>
          <Form onSubmit={handleCreateCourse}>
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Title</Form.Label>
                  <Form.Control
                    type="text"
                    name="title"
                    value={newCourse.title}
                    onChange={handleInputChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    name="category_id"
                    value={newCourse.category_id}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Select a category</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>Description</Form.Label>
                  <Form.Control
                    type="text"
                    name="description"
                    value={newCourse.description}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>
            <Button type="submit" variant="primary">Create Course</Button>
          </Form>
        </Card.Body>
      </Card>

      <Card className="mb-4">
        <Card.Header>Create Course from Directory</Card.Header>
        <Card.Body>
          <Form onSubmit={handleScanDirectory}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Directory Path</Form.Label>
                  <Form.Control
                    type="text"
                    name="directory_path"
                    value={scanDirectory.directory_path}
                    onChange={handleScanInputChange}
                    placeholder="Enter the full path to the directory"
                    required
                  />
                  <Form.Text className="text-muted">
                    Enter the full path to the directory containing course materials
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Category</Form.Label>
                  <Form.Select
                    name="category_id"
                    value={scanDirectory.category_id}
                    onChange={handleScanInputChange}
                    required
                  >
                    <option value="">Select a category</option>
                    {categories.map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            <Button 
              type="submit" 
              variant="primary"
              disabled={isScanning}
            >
              {isScanning ? 'Scanning...' : 'Scan Directory'}
            </Button>
          </Form>
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>Course List</Card.Header>
        <Card.Body>
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>ID</th>
                <th>Title</th>
                <th>Category</th>
                <th>Description</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {courses.map(course => (
                <tr key={course.id}>
                  <td>{course.id}</td>
                  <td>{course.title}</td>
                  <td>
                    {categories.find(c => c.id === course.category_id)?.name || 'Unknown'}
                  </td>
                  <td>{course.description}</td>
                  <td>
                    <Button 
                      variant="outline-primary" 
                      size="sm"
                      className="me-2"
                    >
                      Edit
                    </Button>
                    <Button 
                      variant="outline-danger" 
                      size="sm"
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
    </div>
  );
};

const VideoManagement = () => {
  return (
    <div>
      <h2>Video Management</h2>
      <p>Here you can manage videos, upload new ones, and organize them into courses and units.</p>
      <Alert variant="info">
        This section is under development. Check back soon for more features!
      </Alert>
    </div>
  );
};

const VideoProcessing = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [processingStatus, setProcessingStatus] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleProcessVideo = (e) => {
    e.preventDefault();
    if (!videoUrl) return;
    
    setIsProcessing(true);
    setProcessingStatus('Processing video...');
    
    // Simulate video processing
    setTimeout(() => {
      setProcessingStatus('Video processed successfully! Quizzes have been generated.');
      setIsProcessing(false);
      setVideoUrl('');
    }, 3000);
  };

  return (
    <div>
      <h2 className="mb-4">Video Processing</h2>
      <p>Process videos to automatically generate quizzes and learning materials.</p>
      
      <Card className="mb-4">
        <Card.Header>Process YouTube Video</Card.Header>
        <Card.Body>
          <Form onSubmit={handleProcessVideo}>
            <Form.Group className="mb-3">
              <Form.Label>YouTube URL</Form.Label>
              <Form.Control
                type="text"
                placeholder="https://www.youtube.com/watch?v=..."
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                required
              />
              <Form.Text className="text-muted">
                Enter the URL of a YouTube video to process.
              </Form.Text>
            </Form.Group>
            <Button 
              type="submit" 
              variant="primary"
              disabled={isProcessing}
            >
              {isProcessing ? 'Processing...' : 'Process Video'}
            </Button>
          </Form>
          
          {processingStatus && (
            <Alert variant="info" className="mt-3">
              {processingStatus}
            </Alert>
          )}
        </Card.Body>
      </Card>
      
      <Card>
        <Card.Header>Upload Local Video</Card.Header>
        <Card.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Video File</Form.Label>
              <Form.Control
                type="file"
                accept="video/*"
              />
              <Form.Text className="text-muted">
                Upload a video file from your computer.
              </Form.Text>
            </Form.Group>
            <Button 
              type="submit" 
              variant="primary"
            >
              Upload & Process
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
};

const ProgressTracking = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await api.get('/admin/progress');
        setUsers(response.data);
      } catch (error) {
        console.error('Error fetching progress data:', error);
        setError('Failed to load progress data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <h2>Progress Tracking</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      {loading ? (
        <div className="text-center">
          <Spinner animation="border" />
        </div>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>User</th>
              <th>Course</th>
              <th>Progress</th>
              <th>Last Accessed</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              user.courses.map(course => (
                <tr key={`${user.id}-${course.id}`}>
                  <td>{user.username}</td>
                  <td>{course.title}</td>
                  <td>
                    <ProgressBar 
                      now={course.progress.progress_percentage} 
                      label={`${Math.round(course.progress.progress_percentage)}%`}
                    />
                  </td>
                  <td>
                    {new Date(course.progress.last_accessed).toLocaleDateString()}
                  </td>
                </tr>
              ))
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default AdminPanel; 