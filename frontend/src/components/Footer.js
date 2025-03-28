import React from 'react';
import { Container, Row, Col } from 'react-bootstrap';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-dark text-white py-4">
      <Container>
        <Row>
          <Col md={6}>
            <h5>Learning Platform</h5>
            <p className="small">
              A comprehensive educational platform designed to help users of all ages learn
              Chinese, math, English, and other subjects.
            </p>
          </Col>
          <Col md={3}>
            <h5>Quick Links</h5>
            <ul className="list-unstyled">
              <li><a href="/dashboard" className="text-white">Dashboard</a></li>
              <li><a href="/categories" className="text-white">Categories</a></li>
              <li><a href="/profile" className="text-white">Profile</a></li>
            </ul>
          </Col>
          <Col md={3}>
            <h5>Support</h5>
            <ul className="list-unstyled">
              <li><a href="#" className="text-white">Help Center</a></li>
              <li><a href="#" className="text-white">Contact Us</a></li>
              <li><a href="#" className="text-white">Privacy Policy</a></li>
            </ul>
          </Col>
        </Row>
        <hr className="my-3" />
        <Row>
          <Col className="text-center">
            <p className="small mb-0">
              &copy; {currentYear} Learning Platform. All rights reserved.
            </p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer; 