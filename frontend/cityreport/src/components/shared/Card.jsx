import React from 'react';
import './Card.css';

const Card = ({ children, className = '', padding = 'md', onClick }) => {
    return (
        <div
            className={`card card-p-${padding} ${onClick ? 'card-interactive' : ''} ${className}`}
            onClick={onClick}
        >
            {children}
        </div>
    );
};

export default Card;
