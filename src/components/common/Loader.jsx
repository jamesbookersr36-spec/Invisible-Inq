import PropTypes from 'prop-types';
import './Loader.css';

/**
 * Custom animated loading spinner with segmented conic gradient
 * @param {number} size - Size of the loader in pixels (default: 50)
 * @param {string} color - Color of the loader (default: #333333 - dark gray)
 * @param {number} thickness - Thickness of the loader ring in pixels (default: 8)
 */
const Loader = ({ size = 25, color = '#333333', thickness = 8 }) => {
  return (
    <div 
      className="custom-loader"
      style={{
        '--loader-size': `${size}px`,
        '--loader-color': color,
        '--loader-thickness': `${thickness}px`
      }}
    />
  );
};

Loader.propTypes = {
  size: PropTypes.number,
  color: PropTypes.string,
  thickness: PropTypes.number
};

export default Loader;

