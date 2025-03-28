import { render, screen } from '@testing-library/react';
import Footer from './Footer';

describe('Footer Component', () => {
  test('renders footer with correct content', () => {
    render(<Footer />);
    
    // Check main title
    expect(screen.getByText('Learning Platform')).toBeInTheDocument();
    
    // Check educational platform description 
    expect(screen.getByText(/comprehensive educational platform/i)).toBeInTheDocument();
    
    // Check quick links section
    expect(screen.getByText('Quick Links')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Categories')).toBeInTheDocument();
    expect(screen.getByText('Profile')).toBeInTheDocument();
    
    // Check support section
    expect(screen.getByText('Support')).toBeInTheDocument();
    expect(screen.getByText('Help Center')).toBeInTheDocument();
    expect(screen.getByText('Contact Us')).toBeInTheDocument();
    expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    
    // Check copyright notice with current year
    const currentYear = new Date().getFullYear();
    expect(screen.getByText(`© ${currentYear} Learning Platform. All rights reserved.`)).toBeInTheDocument();
  });
}); 