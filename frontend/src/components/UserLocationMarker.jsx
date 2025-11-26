import React, { useEffect } from 'react';
import { Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';

const UserLocationMarker = ({ position }) => {
    const map = useMap();

    useEffect(() => {
        if (position) {
            map.flyTo(position, 15);
        }
    }, [position, map]);

    if (!position) return null;

    const pulsingIcon = L.divIcon({
        className: 'css-icon',
        html: '<div class="gps-marker"><div class="gps-dot"></div><div class="gps-ring"></div></div>',
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });

    return (
        <Marker position={position} icon={pulsingIcon}>
            <Popup>You are here</Popup>
        </Marker>
    );
};

export default UserLocationMarker;
