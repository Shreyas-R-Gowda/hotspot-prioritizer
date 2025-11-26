import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const { login, user } = useAuth();

    useEffect(() => {
        if (user) {
            if (user.role === 'admin') {
                navigate('/admin/dashboard', { replace: true });
            } else {
                navigate('/citizen/dashboard', { replace: true });
            }
        }
    }, [user, navigate]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                const success = await login(email, password);
                if (success) {
                    // Navigation will be handled by the useEffect that watches 'user'
                    // But we can also force it here if needed, though useEffect is safer
                } else {
                    setError('Invalid credentials');
                }
            } else {
                await axios.post('http://localhost:8000/auth/register', {
                    email,
                    password,
                    name
                });
                setIsLogin(true);
                alert("Registration successful! Please login.");
            }
        } catch (err) {
            console.error(err);
            setError(err.response?.data?.detail || 'An error occurred');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-50 pt-16">
            <div className="bg-white p-8 rounded-2xl shadow-[0_20px_50px_rgba(8,_112,_184,_0.7)] w-full max-w-md transform transition-all hover:scale-[1.01] border border-slate-100">
                <h2 className="text-3xl font-extrabold mb-6 text-center text-slate-800">
                    {isLogin ? 'Welcome Back' : 'Create Account'}
                </h2>
                {error && <div className="bg-red-50 text-red-500 p-3 rounded-lg mb-4 text-sm border border-red-100">{error}</div>}
                <form onSubmit={handleSubmit} className="space-y-5">
                    {!isLogin && (
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Name</label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm"
                                required={!isLogin}
                                placeholder="John Doe"
                            />
                        </div>
                    )}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm"
                            required
                            placeholder="you@example.com"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-2 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm"
                            required
                            placeholder="••••••••"
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 rounded-xl font-bold shadow-lg hover:shadow-blue-500/30 hover:-translate-y-0.5 transition-all duration-200 active:scale-95"
                    >
                        {isLogin ? 'Sign In' : 'Create Account'}
                    </button>
                </form>
                <div className="mt-6 text-center">
                    <button
                        onClick={() => setIsLogin(!isLogin)}
                        className="text-blue-600 hover:text-blue-700 font-medium text-sm hover:underline transition-colors"
                    >
                        {isLogin ? "New here? Create an account" : "Already have an account? Sign in"}
                    </button>
                    {isLogin && (
                        <div className="mt-4 pt-4 border-t border-slate-100">
                            <button
                                type="button"
                                onClick={() => {
                                    setEmail('admin@example.com');
                                    setPassword('admin123');
                                }}
                                className="text-xs text-slate-400 hover:text-slate-600 font-medium transition-colors"
                            >
                                Fill Admin Credentials (Dev)
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Login;
