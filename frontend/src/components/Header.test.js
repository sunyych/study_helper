import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from './Header';

// Mock react-router-dom's useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock the auth service
const mockLogout = jest.fn().mockResolvedValue(null);
jest.mock('../services/auth', () => ({
  logout: () => mockLogout(),
}));

describe('Header Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders login link when user is not logged in', () => {
    render(
      <BrowserRouter>
        <Header user={null} setUser={() => {}} />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/login/i)).toBeInTheDocument();
    expect(screen.queryByText(/dashboard/i)).not.toBeInTheDocument();
  });
  
  test('renders dashboard and categories when user is logged in', () => {
    const user = { username: 'testuser', is_admin: false };
    
    render(
      <BrowserRouter>
        <Header user={user} setUser={() => {}} />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/categories/i)).toBeInTheDocument();
    expect(screen.getByText(/testuser/i)).toBeInTheDocument();
    expect(screen.queryByText(/admin panel/i)).not.toBeInTheDocument();
  });
  
  test('renders admin panel link when user is admin', () => {
    const adminUser = { username: 'adminuser', is_admin: true };
    
    render(
      <BrowserRouter>
        <Header user={adminUser} setUser={() => {}} />
      </BrowserRouter>
    );
    
    expect(screen.getByText(/admin panel/i)).toBeInTheDocument();
  });
  
  test('calls logout and navigates when logout is clicked', async () => {
    const user = { username: 'testuser', is_admin: false };
    const setUser = jest.fn();
    
    render(
      <BrowserRouter>
        <Header user={user} setUser={setUser} />
      </BrowserRouter>
    );
    
    // Open dropdown and click logout
    fireEvent.click(screen.getByText(/testuser/i));
    fireEvent.click(screen.getByText(/logout/i));
    
    // Check that the logout function was called and navigation occurred
    await waitFor(() => {
      expect(mockLogout).toHaveBeenCalled();
    });
    
    await waitFor(() => {
      expect(setUser).toHaveBeenCalledWith(null);
    });
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
}); 