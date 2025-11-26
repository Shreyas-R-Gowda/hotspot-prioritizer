import React from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const ReportCard = ({ report, onUpdate }) => {
    const navigate = useNavigate();

    const handleUpvote = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            alert("Please login to upvote.");
            return;
        }

        const isUpvoted = report.is_upvoted;

        // Optimistic update handled by parent or local state if needed, 
        // but here we just call API and trigger onUpdate
        try {
            const config = { headers: { Authorization: `Bearer ${token}` } };
            if (isUpvoted) {
                await axios.delete(`http://localhost:8000/reports/${report.report_id}/unvote`, config);
            } else {
                await axios.post(`http://localhost:8000/reports/${report.report_id}/upvote`, {}, config);
            }
            if (onUpdate) onUpdate();
        } catch (error) {
            console.error("Upvote failed:", error);
            alert("Action failed.");
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden hover:shadow-md transition-shadow">
            {report.images && report.images.length > 0 ? (
                <div className="h-48 w-full bg-gray-100">
                    <img
                        src={`http://localhost:8000${report.images[0]}`}
                        alt={report.title}
                        className="w-full h-full object-cover"
                    />
                </div>
            ) : (
                <div className="h-48 w-full bg-slate-50 flex items-center justify-center text-slate-400">
                    No Image
                </div>
            )}
            <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                    <span className={`text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wide ${report.status === 'resolved' ? 'bg-green-100 text-green-800' :
                        report.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                        }`}>
                        {report.status.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-slate-500">
                        {new Date(report.created_at).toLocaleDateString()}
                    </span>
                </div>
                <h3 className="font-bold text-lg text-slate-800 mb-1 truncate">{report.title}</h3>
                <p className="text-sm text-slate-600 mb-4 truncate">{report.category}</p>

                <div className="flex items-center justify-between pt-4 border-t border-slate-50">
                    <button
                        onClick={handleUpvote}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${report.is_upvoted
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                            }`}
                    >
                        <span>👍</span>
                        <span>{report.upvote_count}</span>
                    </button>

                    {/* Admin Actions Placeholder or View Details */}
                    <button
                        onClick={() => navigate(`/reports/${report.report_id}`)}
                        className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                    >
                        Details &rarr;
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ReportCard;
