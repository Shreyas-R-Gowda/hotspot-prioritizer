import React from 'react';
import './Button.css';

const Button = ({
    children,
    variant = 'primary',
    size = 'md',
    className = '',
    disabled = false,
    onClick,
    type = 'button',
    fullWidth = false,
    icon: Icon
}) => {
    return (
        <button
            type={type}
            className={`btn btn-${variant} btn-${size} ${fullWidth ? 'btn-full' : ''} ${className}`}
            disabled={disabled}
            onClick={onClick}
        >
            {Icon && <Icon size={18} className="btn-icon" />}
            {children}
        </button>
    );
};

export default Button;
