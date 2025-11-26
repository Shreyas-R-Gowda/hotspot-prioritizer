import React, { useEffect, useState } from 'react';

const CursorHighlighter = () => {
    const [position, setPosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const updatePosition = (e) => {
            setPosition({ x: e.clientX, y: e.clientY });
        };

        window.addEventListener('mousemove', updatePosition);

        return () => window.removeEventListener('mousemove', updatePosition);
    }, []);

    return (
        <div
            className="pointer-events-none fixed inset-0 z-50 transition-opacity duration-300"
            style={{
                background: `radial-gradient(600px at ${position.x}px ${position.y}px, rgba(29, 78, 216, 0.15), transparent 80%)`,
            }}
        />
    );
};

export default CursorHighlighter;
