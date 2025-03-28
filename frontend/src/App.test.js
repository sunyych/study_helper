import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

// Mock the auth service
jest.mock('./services/auth', () => ({
  getCurrentUser: jest.fn().mockResolvedValue(null),
  isAuthenticated: jest.fn().mockReturnValue(false),
}));

test('renders login page when user is not authenticated', async () => {
  render(
    <BrowserRouter>
      <App />
    </BrowserRouter>
  );
  
  // Initially shows loading state
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  
  // Wait for authentication check to complete and navigate to login
  await screen.findByText(/login/i);
  expect(screen.getByText(/login/i)).toBeInTheDocument();
}); 