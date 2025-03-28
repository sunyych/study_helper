import axios from 'axios';
import { login, logout, getCurrentUser, isAuthenticated } from './auth';

// Mock axios
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    get: jest.fn(),
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    }
  })),
  post: jest.fn()
}));

describe('Auth Service', () => {
  let localStorageMock;
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock localStorage
    localStorageMock = {
      store: {},
      getItem: jest.fn(key => localStorageMock.store[key] || null),
      setItem: jest.fn((key, value) => {
        localStorageMock.store[key] = value;
      }),
      removeItem: jest.fn(key => {
        delete localStorageMock.store[key];
      }),
      clear: jest.fn(() => {
        localStorageMock.store = {};
      })
    };
    
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock
    });
  });
  
  describe('login', () => {
    test('successful login should store token and return user data', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token'
        }
      };
      
      const mockUserResponse = {
        data: {
          id: 1,
          username: 'testuser',
          is_admin: false
        }
      };
      
      // Mock axios.post for login request
      axios.post.mockResolvedValueOnce(mockResponse);
      
      // Mock axios.get for getCurrentUser request
      axios.create().get.mockResolvedValueOnce(mockUserResponse);
      
      const result = await login('testuser', 'password');
      
      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/auth/token'),
        expect.any(FormData),
        expect.objectContaining({
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        })
      );
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'test-token');
      expect(result).toEqual(mockUserResponse.data);
    });
    
    test('failed login should return null', async () => {
      const mockResponse = {
        data: {}
      };
      
      axios.post.mockResolvedValueOnce(mockResponse);
      
      const result = await login('wronguser', 'wrongpass');
      
      expect(result).toBeNull();
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });
  });
  
  describe('logout', () => {
    test('logout should remove token from localStorage', async () => {
      localStorageMock.setItem('token', 'test-token');
      
      await logout();
      
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
    });
  });
  
  describe('getCurrentUser', () => {
    test('should return user data when token exists', async () => {
      localStorageMock.getItem.mockReturnValueOnce('test-token');
      
      const mockUserResponse = {
        data: {
          id: 1,
          username: 'testuser',
          is_admin: false
        }
      };
      
      axios.create().get.mockResolvedValueOnce(mockUserResponse);
      
      const result = await getCurrentUser();
      
      expect(axios.create().get).toHaveBeenCalledWith('/users/me');
      expect(result).toEqual(mockUserResponse.data);
    });
    
    test('should return null when token does not exist', async () => {
      localStorageMock.getItem.mockReturnValueOnce(null);
      
      const result = await getCurrentUser();
      
      expect(result).toBeNull();
      expect(axios.create().get).not.toHaveBeenCalled();
    });
    
    test('should return null and remove token when API call fails', async () => {
      localStorageMock.getItem.mockReturnValueOnce('test-token');
      
      axios.create().get.mockRejectedValueOnce(new Error('API error'));
      
      const result = await getCurrentUser();
      
      expect(result).toBeNull();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
    });
  });
  
  describe('isAuthenticated', () => {
    test('should return true when token exists', () => {
      localStorageMock.getItem.mockReturnValueOnce('test-token');
      
      const result = isAuthenticated();
      
      expect(result).toBe(true);
    });
    
    test('should return false when token does not exist', () => {
      localStorageMock.getItem.mockReturnValueOnce(null);
      
      const result = isAuthenticated();
      
      expect(result).toBe(false);
    });
  });
}); 