import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, Bell, User, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import Button from './Button';
import './Navbar.css';

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="navbar">
            <div className="container navbar-container">
                <div className="navbar-brand">
                    <Link to="/" className="flex items-center gap-sm">
                        <div className="logo-placeholder">C</div>
                        <span className="text-xl font-bold">CityReport</span>
                    </Link>
                </div>

                <div className="navbar-menu hidden md:flex">
                    {user?.role === 'citizen' && (
                        <>
                            <Link to="/citizen/dashboard" className="nav-link">Dashboard</Link>
                            <Link to="/citizen/map" className="nav-link">Map View</Link>
                            <Link to="/citizen/reports" className="nav-link">My Reports</Link>
                        </>
                    )}
                    {/* Add other role links here */}
                </div>

                <div className="navbar-actions flex items-center gap-md">
                    <Button variant="ghost" size="sm" className="icon-btn">
                        <Bell size={20} />
                    </Button>

                    <div className="user-menu flex items-center gap-sm">
                        <div className="avatar">
                            <User size={18} />
                        </div>
                        <span className="hidden md:block text-sm font-medium">{user?.name || 'User'}</span>
                        <Button variant="ghost" size="sm" onClick={handleLogout} className="icon-btn">
                            <LogOut size={18} />
                        </Button>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
