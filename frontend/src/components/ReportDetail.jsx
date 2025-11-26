import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const ReportDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [report, setReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedImage, setSelectedImage] = useState(null);

    useEffect(() => {
        fetchReportDetail();
    }, [id]);

    const fetchReportDetail = async () => {
        try {
            const token = localStorage.getItem('token');
            const config = token ? { headers: { Authorization: `Bearer ${token}` } } : {};

            const response = await axios.get(`http://localhost:8000/reports/${id}`, config);
            setReport(response.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching report details:", error);
            setError(error.response?.data?.detail || "Failed to load report");
            setLoading(false);
        }
    };

    const handleUpvote = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            alert("Please login to upvote.");
            return;
        }

        const isUpvoted = report.is_upvoted;

        try {
            const config = { headers: { Authorization: `Bearer ${token}` } };
            if (isUpvoted) {
                await axios.delete(`http://localhost:8000/reports/${report.report_id}/unvote`, config);
            } else {
                await axios.post(`http://localhost:8000/reports/${report.report_id}/upvote`, {}, config);
            }
            fetchReportDetail(); // Refresh data
        } catch (error) {
            console.error("Upvote failed:", error);
            alert("Failed to update upvote. Please try again.");
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-slate-50">
                <div className="text-center">
                    <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                    <p className="mt-4 text-slate-600">Loading report...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-slate-50">
                <div className="text-center bg-white p-8 rounded-xl shadow-lg max-w-md">
                    <svg className="mx-auto h-12 w-12 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <h3 className="mt-4 text-lg font-semibold text-slate-800">Error Loading Report</h3>
                    <p className="mt-2 text-sm text-slate-600">{error}</p>
                    <button
                        onClick={() => navigate(-1)}
                        className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Go Back
                    </button>
                </div>
            </div>
        );
    }

    if (!report) return null;

    const statusColors = {
        open: 'bg-red-100 text-red-800',
        in_progress: 'bg-yellow-100 text-yellow-800',
        resolved: 'bg-green-100 text-green-800'
    };

    return (
        <div className="min-h-screen bg-slate-50 pt-20 pb-10 px-4">
            <div className="max-w-5xl mx-auto">
                {/* Back Button */}
                <button
                    onClick={() => navigate(-1)}
                    className="mb-6 flex items-center text-blue-600 hover:text-blue-800 font-medium transition-colors"
                >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Back
                </button>

                <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
                    {/* Header */}
                    <div className="p-8 border-b border-slate-100">
                        <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <span className={`text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wide ${statusColors[report.status]}`}>
                                        {report.status.replace('_', ' ')}
                                    </span>
                                    <span className="text-sm text-slate-500">
                                        Report #{report.report_id}
                                    </span>
                                </div>
                                <h1 className="text-3xl font-extrabold text-slate-800 mb-2">{report.title}</h1>
                                <p className="text-lg text-slate-600">{report.category}</p>
                            </div>

                            {/* Upvote Button */}
                            <button
                                onClick={handleUpvote}
                                className={`flex items-center gap-2 px-6 py-3 rounded-xl text-lg font-bold transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 ${report.is_upvoted
                                        ? 'bg-blue-600 text-white hover:bg-blue-700'
                                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                                    }`}
                            >
                                <span>👍</span>
                                <span>{report.upvote_count}</span>
                            </button>
                        </div>

                        {/* Metadata */}
                        <div className="flex flex-wrap gap-6 text-sm text-slate-600">
                            <div className="flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                                <span>
                                    {report.created_by ? report.created_by.name : 'Unknown User'}
                                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                <span>
                                    {new Date(report.created_at).toLocaleDateString('en-US', {
                                        year: 'numeric',
                                        month: 'long',
                                        day: 'numeric'
                                    })}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Content Grid */}
                    <div className="grid md:grid-cols-2 gap-8 p-8">
                        {/* Left Column - Images and Description */}
                        <div className="space-y-6">
                            {/* Image Gallery */}
                            {report.images && report.images.length > 0 ? (
                                <div className="space-y-4">
                                    <h3 className="text-lg font-bold text-slate-800">Photos</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        {report.images.map((img, index) => (
                                            <div
                                                key={index}
                                                className="relative aspect-square bg-slate-100 rounded-xl overflow-hidden cursor-pointer hover:ring-4 hover:ring-blue-500 transition-all"
                                                onClick={() => setSelectedImage(img)}
                                            >
                                                <img
                                                    src={`http://localhost:8000${img}`}
                                                    alt={`Report image ${index + 1}`}
                                                    className="w-full h-full object-cover"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : (
                                <div className="bg-slate-50 rounded-xl p-8 text-center">
                                    <svg className="mx-auto h-12 w-12 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <p className="mt-2 text-slate-500">No images attached</p>
                                </div>
                            )}

                            {/* Description */}
                            <div>
                                <h3 className="text-lg font-bold text-slate-800 mb-3">Description</h3>
                                <div className="bg-slate-50 rounded-xl p-6">
                                    <p className="text-slate-700 leading-relaxed">
                                        {report.description || 'No description provided.'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Right Column - Location Map */}
                        <div className="space-y-6">
                            <h3 className="text-lg font-bold text-slate-800">Location</h3>
                            <div className="bg-slate-100 rounded-xl overflow-hidden" style={{ height: '400px' }}>
                                <MapContainer
                                    center={[report.lat, report.lon]}
                                    zoom={16}
                                    scrollWheelZoom={false}
                                    className="h-full w-full"
                                >
                                    <TileLayer
                                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                    />
                                    <Marker position={[report.lat, report.lon]}>
                                        <Popup>
                                            <div className="text-center">
                                                <p className="font-semibold">{report.title}</p>
                                                <p className="text-xs text-slate-600">{report.category}</p>
                                            </div>
                                        </Popup>
                                    </Marker>
                                </MapContainer>
                            </div>

                            {/* Coordinates */}
                            <div className="bg-slate-50 rounded-xl p-6 space-y-3">
                                <div className="flex justify-between items-center">
                                    <span className="font-medium text-slate-700">Latitude</span>
                                    <span className="font-mono text-sm bg-white px-3 py-1.5 rounded-lg border border-slate-200">
                                        {report.lat.toFixed(6)}
                                    </span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <span className="font-medium text-slate-700">Longitude</span>
                                    <span className="font-mono text-sm bg-white px-3 py-1.5 rounded-lg border border-slate-200">
                                        {report.lon.toFixed(6)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Image Modal */}
            {selectedImage && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
                    onClick={() => setSelectedImage(null)}
                >
                    <div className="relative max-w-6xl max-h-full">
                        <button
                            onClick={() => setSelectedImage(null)}
                            className="absolute -top-12 right-0 text-white hover:text-slate-300 text-3xl font-bold"
                        >
                            &times;
                        </button>
                        <img
                            src={`http://localhost:8000${selectedImage}`}
                            alt="Full size"
                            className="max-w-full max-h-[90vh] rounded-lg"
                            onClick={(e) => e.stopPropagation()}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ReportDetail;
