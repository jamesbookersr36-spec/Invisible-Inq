const BackgroundOverlay = ({ 
  opacity = 0.3, 
  gradient = true,
  className = '' 
}) => {
  const overlayStyle = {
    background: gradient
      ? `linear-gradient(135deg, rgba(0, 0, 0, ${opacity}) 0%, rgba(20, 20, 40, ${opacity * 0.8}) 50%, rgba(0, 0, 0, ${opacity}) 100%)`
      : `rgba(0, 0, 0, ${opacity})`,
  };

  return (
    <div
      className={`absolute inset-0 pointer-events-none ${className}`}
      style={overlayStyle}
    />
  );
};

export default BackgroundOverlay;
