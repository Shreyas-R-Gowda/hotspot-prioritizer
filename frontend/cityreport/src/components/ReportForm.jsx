import React, { useState } from 'react';
import api from '../api';

function ReportForm() {
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        category: 'pothole',
        latitude: 40.7128, // Default NYC
        longitude: -74.0060,
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/reports/', formData);
            alert('Report submitted successfully!');
        } catch (error) {
            console.error('Error submitting report:', error);
            alert('Failed to submit report.');
        }
    };

    return (
        <div className="max-w-md mx-auto bg-white p-6 rounded shadow">
            <h2 className="text-2xl font-bold mb-4">Submit a Report</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block mb-1">Title</label>
                    <input
                        type="text"
                        className="w-full border p-2 rounded"
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        required
                    />
                </div>
                <div>
                    <label className="block mb-1">Description</label>
                    <textarea
                        className="w-full border p-2 rounded"
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        required
                    />
                </div>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block mb-1">Latitude</label>
                        <input
                            type="number"
                            step="any"
                            className="w-full border p-2 rounded"
                            value={formData.latitude}
                            onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) })}
                            required
                        />
                    </div>
                    <div>
                        <label className="block mb-1">Longitude</label>
                        <input
                            type="number"
                            step="any"
                            className="w-full border p-2 rounded"
                            value={formData.longitude}
                            onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) })}
                            required
                        />
                    </div>
                </div>
                <div>
                    <label className="block mb-1">Category</label>
                    <select
                        className="w-full border p-2 rounded"
                        value={formData.category}
                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    >
                        <option value="pothole">Pothole</option>
                        <option value="garbage">Garbage</option>
                        <option value="street_light">Street Light</option>
                    </select>
                </div>
                <button type="submit" className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700">
                    Submit
                </button>
            </form>
        </div>
    );
}

export default ReportForm;
