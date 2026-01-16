import React, { useState } from 'react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Users, FileText, CheckCircle2 } from 'lucide-react';
import Navbar from '../../components/shared/Navbar';
import Card from '../../components/shared/Card';
import './AdminDashboard.css';

const CATEGORY_DATA = [
    { name: 'Roads', value: 45 },
    { name: 'Sanitation', value: 32 },
    { name: 'Electricity', value: 28 },
    { name: 'Water', value: 18 },
    { name: 'Health', value: 12 }
];

const MONTHLY_DATA = [
    { month: 'Jan', reports: 65, resolved: 52 },
    { month: 'Feb', reports: 72, resolved: 58 },
    { month: 'Mar', reports: 88, resolved: 71 },
    { month: 'Apr', reports: 95, resolved: 78 },
    { month: 'May', reports: 102, resolved: 85 },
    { month: 'Jun', reports: 118, resolved: 96 }
];

const COLORS = ['#0F766E', '#F59E0B', '#EF4444', '#3B82F6', '#10B981'];

const AdminDashboard = () => {
    const stats = {
        totalReports: 542,
        activeUsers: 1248,
        resolvedReports: 428,
        resolutionRate: 79
    };

    return (
        <div className="min-h-screen bg-background">
            <Navbar />

            <main className="container py-lg">
                <div className="dashboard-header">
                    <h1 className="text-2xl mb-xs">Admin Dashboard</h1>
                    <p className="text-muted">System overview and analytics</p>
                </div>

                <div className="admin-stats-grid">
                    <Card className="admin-stat-card">
                        <div className="admin-stat-icon reports">
                            <FileText size={24} />
                        </div>
                        <div className="admin-stat-content">
                            <p className="admin-stat-label">Total Reports</p>
                            <p className="admin-stat-value">{stats.totalReports}</p>
                            <p className="admin-stat-trend positive">
                                <TrendingUp size={14} /> +12% from last month
                            </p>
                        </div>
                    </Card>

                    <Card className="admin-stat-card">
                        <div className="admin-stat-icon users">
                            <Users size={24} />
                        </div>
                        <div className="admin-stat-content">
                            <p className="admin-stat-label">Active Users</p>
                            <p className="admin-stat-value">{stats.activeUsers}</p>
                            <p className="admin-stat-trend positive">
                                <TrendingUp size={14} /> +8% from last month
                            </p>
                        </div>
                    </Card>

                    <Card className="admin-stat-card">
                        <div className="admin-stat-icon resolved">
                            <CheckCircle2 size={24} />
                        </div>
                        <div className="admin-stat-content">
                            <p className="admin-stat-label">Resolved Reports</p>
                            <p className="admin-stat-value">{stats.resolvedReports}</p>
                            <p className="admin-stat-trend positive">
                                <TrendingUp size={14} /> +15% from last month
                            </p>
                        </div>
                    </Card>

                    <Card className="admin-stat-card">
                        <div className="admin-stat-icon rate">
                            <TrendingUp size={24} />
                        </div>
                        <div className="admin-stat-content">
                            <p className="admin-stat-label">Resolution Rate</p>
                            <p className="admin-stat-value">{stats.resolutionRate}%</p>
                            <p className="admin-stat-trend positive">
                                <TrendingUp size={14} /> +3% from last month
                            </p>
                        </div>
                    </Card>
                </div>

                <div className="charts-grid">
                    <Card>
                        <h3 className="text-lg mb-md">Reports by Category</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={CATEGORY_DATA}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {CATEGORY_DATA.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </Card>

                    <Card>
                        <h3 className="text-lg mb-md">Monthly Trends</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={MONTHLY_DATA}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="month" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="reports" fill="#0F766E" name="Total Reports" />
                                <Bar dataKey="resolved" fill="#10B981" name="Resolved" />
                            </BarChart>
                        </ResponsiveContainer>
                    </Card>
                </div>
            </main>
        </div>
    );
};

export default AdminDashboard;
