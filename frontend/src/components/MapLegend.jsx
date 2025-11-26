import React from 'react';

const MapLegend = ({ mode }) => {
    return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-slate-200 text-sm">
            <h4 className="font-bold mb-2 text-slate-700">
                {mode === 'heatmap' ? 'Report Density' : 'Report Count'}
            </h4>
            <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-red-600 opacity-80"></div>
                    <span>High</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-orange-500 opacity-80"></div>
                    <span>Medium</span>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-4 h-4 rounded bg-yellow-400 opacity-80"></div>
                    <span>Low</span>
                </div>
                {mode === 'grid' && (
                    <div className="flex items-center gap-2">
                        <div className="w-4 h-4 rounded bg-blue-200 opacity-40"></div>
                        <span>None/Sparse</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MapLegend;
