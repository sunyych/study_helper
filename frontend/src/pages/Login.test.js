import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Login from './Login';

// Mock the auth service
jest.mock('../services/auth', () => ({
  login: jest.fn(),
}));

describe('Login Page', () => {
  const mockSetUser = jest.fn();
  const mockUser = { id: 1, username: 'testuser', is_admin: false };
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renders login form correctly', () => {
    render(<Login setUser={mockSetUser} />);
    
    expect(screen.getByRole('heading', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/enter password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });
  
  test('handles input changes correctly', async () => {
    render(<Login setUser={mockSetUser} />);
    
    const usernameInput = screen.getByPlaceholderText(/enter username/i);
    const passwordInput = screen.getByPlaceholderText(/enter password/i);
    
    await userEvent.type(usernameInput, 'testuser');
    await userEvent.type(passwordInput, 'password123');
    
    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('password123');
  });
  
  test('submits form with correct values and sets user on success', async () => {
    const { login } = require('../services/auth');
    login.mockResolvedValueOnce(mockUser);
    
    render(<Login setUser={mockSetUser} />);
    
    await userEvent.type(screen.getByPlaceholderText(/enter username/i), 'testuser');
    await userEvent.type(screen.getByPlaceholderText(/enter password/i), 'password123');
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    // Check loading state
    expect(screen.getByText(/logging in/i)).toBeInTheDocument();
    
    await waitFor(() => {
      expect(login).toHaveBeenCalledWith('testuser', 'password123');
    });
    
    await waitFor(() => {
      expect(mockSetUser).toHaveBeenCalledWith(mockUser);
    });
  });
  
  test('shows error message when login fails', async () => {
    const { login } = require('../services/auth');
    login.mockResolvedValueOnce(null);
    
    render(<Login setUser={mockSetUser} />);
    
    await userEvent.type(screen.getByPlaceholderText(/enter username/i), 'wronguser');
    await userEvent.type(screen.getByPlaceholderText(/enter password/i), 'wrongpass');
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/login failed/i)).toBeInTheDocument();
    });
    
    expect(mockSetUser).not.toHaveBeenCalled();
  });
  
  test('shows error message when login throws exception', async () => {
    const { login } = require('../services/auth');
    login.mockRejectedValueOnce({ response: { data: { detail: 'Invalid credentials' } } });
    
    render(<Login setUser={mockSetUser} />);
    
    await userEvent.type(screen.getByPlaceholderText(/enter username/i), 'testuser');
    await userEvent.type(screen.getByPlaceholderText(/enter password/i), 'password123');
    
    fireEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
    
    expect(mockSetUser).not.toHaveBeenCalled();
  });
}); 