import React from 'react';
import { Link } from 'react-router-dom';

import { useAuth } from '../context/AuthContext';

const Navbar = () => {
    const { user, logout } = useAuth();

    return (
        <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 fixed w-full z-[2000] shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16 items-center">
                    <div className="flex-shrink-0 flex items-center">
                        <Link to="/" className="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 hover:scale-105 transition-transform duration-200">
                            HotspotPrioritizer
                        </Link>
                    </div>
                    <div className="flex items-center space-x-4">
                        <NavLink to="/">Map</NavLink>
                        <NavLink to="/hotspots">Hotspots</NavLink>

                        {user ? (
                            <>
                                <span className="text-sm text-slate-500 hidden md:block">
                                    {user.name} ({user.role})
                                </span>
                                {user.role === 'admin' ? (
                                    <NavLink to="/admin/dashboard">Dashboard</NavLink>
                                ) : (
                                    <NavLink to="/citizen/dashboard">My Hotspots</NavLink>
                                )}
                                <button
                                    onClick={logout}
                                    className="text-slate-600 hover:text-red-600 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 hover:bg-red-50"
                                >
                                    Logout
                                </button>
                            </>
                        ) : (
                            <NavLink to="/auth/login">Login</NavLink>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

const NavLink = ({ to, children }) => (
    <Link
        to={to}
        className="text-slate-600 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 hover:bg-blue-50 hover:shadow-md hover:-translate-y-0.5"
    >
        {children}
    </Link>
);

export default Navbar;
