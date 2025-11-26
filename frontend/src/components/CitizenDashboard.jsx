import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import ReportCard from './ReportCard';

const CitizenDashboard = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMyReports();
    }, []);

    const fetchMyReports = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://localhost:8000/reports/', {
                params: { scope: 'mine' },
                headers: { Authorization: `Bearer ${token}` }
            });
            setReports(response.data);
        } catch (error) {
            console.error("Error fetching reports:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="pt-20 px-4 max-w-7xl mx-auto min-h-screen">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h2 className="text-3xl font-extrabold text-slate-800">My Hotspots</h2>
                    <p className="text-slate-500 mt-1">Manage the issues you've reported.</p>
                </div>
                <Link
                    to="/report/new"
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow-md hover:bg-blue-700 transition-colors font-medium"
                >
                    + New Report
                </Link>
            </div>

            {loading ? (
                <div className="text-center py-20">Loading...</div>
            ) : reports.length === 0 ? (
                <div className="text-center py-20 bg-white rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-medium text-slate-900">No reports yet</h3>
                    <p className="text-slate-500 mt-1">You haven't submitted any hotspot reports.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {reports.map(report => (
                        <ReportCard key={report.report_id} report={report} onUpdate={fetchMyReports} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default CitizenDashboard;
