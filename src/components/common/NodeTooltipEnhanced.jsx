import React from 'react';
import { 
  FaUser, FaBuilding, FaMapMarkerAlt, FaDollarSign, 
  FaHandshake, FaFlag, FaBullseye, FaCog, 
  FaFileAlt, FaGlobe, FaLink, FaLayerGroup,
  FaPlus, FaTimes, FaShareAlt
} from 'react-icons/fa';

/**
 * NodeTooltipEnhanced - Comprehensive tooltip component for Three.js graph nodes
 * Displays different layouts and information based on node type
 * 
 * Supported node types with custom layouts:
 * - Entity
 * - Agency
 * - Country
 * - Location
 * - Amount/Transaction
 * - Relationship
 * - Action
 * - Result
 * - Process
 * - Description
 * - And more...
 */

// Icon mapping for different node types
const getNodeIcon = (nodeType) => {
  const type = nodeType?.toLowerCase() || '';
  
  if (type.includes('entity') || type.includes('person')) return FaUser;
  if (type.includes('agency') || type.includes('organization')) return FaBuilding;
  if (type.includes('country')) return FaFlag;
  if (type.includes('location') || type.includes('place')) return FaMapMarkerAlt;
  if (type.includes('amount') || type.includes('transaction')) return FaDollarSign;
  if (type.includes('relationship')) return FaHandshake;
  if (type.includes('action')) return FaCog;
  if (type.includes('result')) return FaBullseye;
  if (type.includes('description')) return FaFileAlt;
  if (type.includes('region')) return FaGlobe;
  if (type.includes('process')) return FaLayerGroup;
  
  return FaLink; // Default icon
};

// Color scheme for different node types - matched to colorUtils.js
const getNodeColor = (nodeType) => {
  const type = nodeType?.toLowerCase() || '';
  
  if (type.includes('entity')) return '#4263EB';
  if (type.includes('relationship')) return '#F03E3E';
  if (type.includes('funding')) return '#40C057';
  if (type.includes('amount')) return '#61d619';
  if (type.includes('agency')) return '#7950F2';
  if (type.includes('action')) return '#FD7E14';
  if (type.includes('country')) return '#9775FA';
  if (type.includes('dba')) return '#FF922B';
  if (type.includes('description')) return '#51CF66';
  if (type.includes('location')) return '#339AF0';
  if (type.includes('place of performance') || type.includes('placeofperformance')) return '#845EF7';
  if (type.includes('process')) return '#20A4F3';
  if (type.includes('recipient')) return '#4ECDC4';
  if (type.includes('region')) return '#95E1D3';
  if (type.includes('result')) return '#F38181';
  
  return '#495057'; // Default
};

// Base tooltip layout - Same style as Amount tooltip with dynamic accent bar color
const BaseTooltipLayout = ({ node, color }) => {
  const name = node.name || node.id || 'Unknown';
  const nodeType = node.node_type || node.type || node.category || '';
  const subtype = node.subtype || node.sub_type || '';
  const description = node.description || node.desc || node.summary || node.properties?.description || '';
  const relatedCount = node.degree || node.related_count || node.count || node.properties?.related_count || null;
  
  // Format type display
  const typeDisplay = subtype ? `${nodeType} / ${subtype}` : nodeType;

  return (
    <div 
      className="flex flex-row rounded-[10px] relative"
      style={{ 
        width: '520px',
        minHeight: '140px',
        padding: '12px 15px',
        background: '#1a1a1a',
        border: '2px solid #1F1F22',
        backdropFilter: 'blur(10px)'
      }}
    >
      {/* Vertical Accent Bar - Color based on node type */}
      <div 
        className="absolute left-3 top-3 bottom-3 w-1.5 rounded-full"
        style={{ backgroundColor: color }}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-5 min-w-0 flex flex-col">
        {/* Node Name */}
        <h3 className="text-white text-xl font-bold mb-1 leading-tight truncate">
          {name}
        </h3>

        {/* Type Information */}
        {typeDisplay && (
          <div className="flex items-center mb-3">
            <span className="text-[#707070] text-xs">
              Type: <span style={{ color }}>{typeDisplay}</span>
            </span>
          </div>
        )}

        {/* Description */}
        {description && (
          <p className="text-[#909090] text-sm leading-relaxed line-clamp-3">
            {description}
          </p>
        )}
      </div>

      {/* Right Side - Icon Group (matching Figma design) */}
      <div className="flex flex-col items-center justify-between ml-4 flex-shrink-0 self-stretch" style={{ gap: '6px' }}>
        {/* Top: Chevron/Expand Icon */}
        <button 
          className="flex items-center justify-center text-white hover:text-gray-300 transition-colors"
          title="Expand"
          style={{ padding: '5px 0 0 0' }}
        >
          <svg width="16" height="8" viewBox="0 0 16 8" fill="none">
            <path d="M1 7L8 1L15 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>

        {/* Middle: Spacer + Network Icon */}
        <div className="flex-1 flex items-center justify-center">
          <button 
            className="flex items-center justify-center text-white hover:text-gray-300 transition-colors"
            title="Network"
          >
          <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14.8868 9.49648C14.313 9.49671 13.7642 9.73132 13.3674 10.1459L11.7565 9.46128C11.8666 9.13184 11.9246 8.78726 11.9284 8.43992C11.9245 6.57423 10.413 5.06273 8.54735 5.05888C8.26529 5.0624 7.98483 5.10168 7.71266 5.17582L6.78639 3.52685C7.57065 2.66732 7.50962 1.33475 6.65009 0.55049C5.79056 -0.233768 4.45799 -0.17274 3.67373 0.686789C2.88947 1.54632 2.9505 2.87889 3.81003 3.66315C4.19987 4.01886 4.709 4.21529 5.23677 4.21362C5.33807 4.21074 5.43907 4.20061 5.53895 4.18334L6.44971 5.80342C5.08174 6.86865 4.75702 8.80386 5.70234 10.2573L3.03696 12.836C1.94634 12.3522 0.669978 12.8441 0.186142 13.9347C-0.297694 15.0253 0.19421 16.3017 1.28483 16.7855C2.37546 17.2694 3.65182 16.7775 4.13565 15.6868C4.40476 15.0802 4.38016 14.3836 4.06888 13.7975L6.6899 11.2617C8.08241 12.1883 9.94507 11.945 11.0529 10.6919L12.7913 11.4301C12.7864 11.4899 12.7737 11.5477 12.7737 11.6083C12.7737 12.7753 13.7198 13.7214 14.8868 13.7214C16.0539 13.7214 17 12.7753 17 11.6082C17 10.4412 16.0539 9.49508 14.8868 9.49508V9.49648Z" fill="#D7D7D7"/>
          </svg>
          </button>
        </div>

        {/* Bottom: Count Badge */}
        <div 
          className="flex items-center justify-end gap-0.5 self-stretch"
          style={{ 
            background: '#000000',
            border: '0.5px solid #D7D7D7',
            borderRadius: '0 0 5px 0',
            padding: '0 5px 0 0'
          }}
        >
          <svg width="7.5" height="7.5" viewBox="0 0 10 10" fill="white">
            <path d="M5 0V10M0 5H10" stroke="white" strokeWidth="2" />
          </svg>
          <span style={{ 
            fontFamily: 'Open Sans, sans-serif',
            fontWeight: 600,
            fontSize: '10px',
            lineHeight: '1.1em',
            letterSpacing: '-0.025em',
            color: '#D7D7D7'
          }}>
            {Math.floor(Math.random() * 1000)}
          </span>
        </div>
      </div>
    </div>
  );
};

// Entity-specific layout (placeholder for future customization)
const EntityTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Agency-specific layout (placeholder for future customization)
const AgencyTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Country-specific layout (placeholder for future customization)
const CountryTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Location-specific layout (placeholder for future customization)
const LocationTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Amount/Transaction-specific layout - Custom flow design
const AmountTooltipLayout = ({ node, color }) => {
  // Extract transaction/amount specific data
  const amount = node.Amount || node.amount || node.value || node.properties?.amount || node.name || '0';
  
  // Source entity - check multiple possible property names
  const sourceEntity = node['Distributor Full Name'] || 
                       node.source_entity || 
                       node.source_name ||
                       node.from_name ||
                       node.from_entity ||
                       node.from ||
                       node.sourceName ||
                       node.properties?.source || 
                       node.properties?.source_name ||
                       node.properties?.from ||
                       'Entity Source';
  
  // Target entity - check multiple possible property names
  const targetEntity = node['Receiver Name'] || 
                       node.target_entity || 
                       node.target_name ||
                       node.to_name ||
                       node.to_entity ||
                       node.to ||
                       node.targetName ||
                       node.properties?.target || 
                       node.properties?.target_name ||
                       node.properties?.to ||
                       'Entity Target';
  
  const entityType = node.section || node.entity_type || node.subtype || node.node_type || node.type || node.properties?.type || 'Type';
  const relatedCount = node.degree || node.related_count || node.count || node.properties?.related_count || null;

  // Format amount with currency
  const formattedAmount = typeof amount === 'number' 
    ? `$${amount.toLocaleString()}` 
    : amount.toString().startsWith('$') 
      ? amount 
      : `$${amount}`;

  // Description text
  const description = node.description || node.desc || node.summary || node.properties?.description || '';

  return (
    <div 
      className="flex flex-row rounded-[10px] relative"
      style={{ 
        width: '520px',
        minHeight: '140px',
        padding: '12px 15px',
        background: '#1a1a1a',
        border: '2px solid #1F1F22',
        backdropFilter: 'blur(10px)'
      }}
    >
      {/* Vertical Accent Bar - Color based on node type */}
      <div 
        className="absolute left-3 top-3 bottom-3 w-1.5 rounded-full"
        style={{ backgroundColor: color }}
      />

      {/* Main Content Area */}
      <div className="flex-1 ml-5 min-w-0 flex flex-col">
        {/* Transaction Flow: Source → Amount → Target */}
        <div className="flex items-center gap-2 mb-1">
          {/* Source Entity */}
          <span className="text-[#B0B0B0] text-base font-medium truncate max-w-[120px]">
            {sourceEntity}
          </span>

          {/* Arrow */}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="text-[#EF4444] flex-shrink-0">
            <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>

          {/* Amount (highlighted in node color) */}
          <span className="text-xl font-bold flex-shrink-0" style={{ color }}>
            {formattedAmount}
          </span>

          {/* Arrow */}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" className="text-[#EF4444] flex-shrink-0">
            <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>

          {/* Target Entity */}
          <span className="text-[#B0B0B0] text-base font-medium truncate max-w-[120px]">
            {targetEntity}
          </span>
        </div>

        {/* Type Information */}
        <div className="flex items-center mb-3">
          <span className="text-[#707070] text-xs">
            Type: <span style={{ color }}>{entityType}</span>
          </span>
        </div>

        {/* Description */}
        {description && (
          <p className="text-[#909090] text-sm leading-relaxed line-clamp-3">
            {description}
          </p>
        )}
      </div>

      {/* Right Side - Icon Group (matching Figma design) */}
      <div className="flex flex-col items-center justify-between ml-4 flex-shrink-0 self-stretch" style={{ gap: '6px' }}>
        {/* Top: Chevron/Expand Icon */}
        <button 
          className="flex items-center justify-center text-white hover:text-gray-300 transition-colors"
          title="Expand"
          style={{ padding: '5px 0 0 0' }}
        >
          <svg width="16" height="8" viewBox="0 0 16 8" fill="none">
            <path d="M1 7L8 1L15 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>

        {/* Middle: Spacer + Network Icon */}
        <div className="flex-1 flex items-center justify-center">
          <button 
            className="flex items-center justify-center text-white hover:text-gray-300 transition-colors"
            title="Network"
          >
            <svg width="17" height="17" viewBox="0 0 17 17" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14.8868 9.49648C14.313 9.49671 13.7642 9.73132 13.3674 10.1459L11.7565 9.46128C11.8666 9.13184 11.9246 8.78726 11.9284 8.43992C11.9245 6.57423 10.413 5.06273 8.54735 5.05888C8.26529 5.0624 7.98483 5.10168 7.71266 5.17582L6.78639 3.52685C7.57065 2.66732 7.50962 1.33475 6.65009 0.55049C5.79056 -0.233768 4.45799 -0.17274 3.67373 0.686789C2.88947 1.54632 2.9505 2.87889 3.81003 3.66315C4.19987 4.01886 4.709 4.21529 5.23677 4.21362C5.33807 4.21074 5.43907 4.20061 5.53895 4.18334L6.44971 5.80342C5.08174 6.86865 4.75702 8.80386 5.70234 10.2573L3.03696 12.836C1.94634 12.3522 0.669978 12.8441 0.186142 13.9347C-0.297694 15.0253 0.19421 16.3017 1.28483 16.7855C2.37546 17.2694 3.65182 16.7775 4.13565 15.6868C4.40476 15.0802 4.38016 14.3836 4.06888 13.7975L6.6899 11.2617C8.08241 12.1883 9.94507 11.945 11.0529 10.6919L12.7913 11.4301C12.7864 11.4899 12.7737 11.5477 12.7737 11.6083C12.7737 12.7753 13.7198 13.7214 14.8868 13.7214C16.0539 13.7214 17 12.7753 17 11.6082C17 10.4412 16.0539 9.49508 14.8868 9.49508V9.49648Z" fill="#D7D7D7"/>
            </svg>
          </button>
        </div>

        {/* Bottom: Count Badge */}
          <div 
            className="flex items-center justify-end gap-0.5 self-stretch"
            style={{ 
              background: '#000000',
              border: '0.5px solid #D7D7D7',
              borderRadius: '0 0 5px 0',
              padding: '0 5px 0 0'
            }}
          >
            <svg width="7.5" height="7.5" viewBox="0 0 10 10" fill="white">
              <path d="M5 0V10M0 5H10" stroke="white" strokeWidth="2" />
            </svg>
            <span style={{ 
              fontFamily: 'Open Sans, sans-serif',
              fontWeight: 600,
              fontSize: '10px',
              lineHeight: '1.1em',
              letterSpacing: '-0.025em',
              color: '#D7D7D7'
            }}>
              {relatedCount}
            </span>
          </div>
      </div>
    </div>
  );
};

// Relationship-specific layout (placeholder for future customization)
const RelationshipTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Action-specific layout - Uses base layout
const ActionTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Result-specific layout (placeholder for future customization)
const ResultTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Process-specific layout (placeholder for future customization)
const ProcessTooltipLayout = ({ node, color }) => {
  return <BaseTooltipLayout node={node} color={color} />;
};

// Get the appropriate layout component based on node type
const getTooltipLayout = (nodeType) => {
  const type = nodeType?.toLowerCase() || '';
  
  if (type.includes('entity') || type.includes('person')) return EntityTooltipLayout;
  if (type.includes('agency') || type.includes('organization')) return AgencyTooltipLayout;
  if (type.includes('country')) return CountryTooltipLayout;
  if (type.includes('location') || type.includes('place')) return LocationTooltipLayout;
  if (type.includes('amount') || type.includes('transaction') || type.includes('funding')) return AmountTooltipLayout;
  if (type.includes('relationship')) return RelationshipTooltipLayout;
  if (type.includes('action')) return ActionTooltipLayout;
  if (type.includes('result')) return ResultTooltipLayout;
  if (type.includes('process')) return ProcessTooltipLayout;
  
  return BaseTooltipLayout; // Default layout
};

/**
 * Main NodeTooltipEnhanced Component
 */
const NodeTooltipEnhanced = ({ node, position }) => {
  if (!node || !position) return null;

  const nodeType = node.node_type || node.type || node.category || '';
  const color = getNodeColor(nodeType);
  const TooltipLayout = getTooltipLayout(nodeType);

  return (
    <div
      className="fixed z-[9999] pointer-events-none"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        transform: 'translate(-50%, -120%)', // Position above the cursor
      }}
    >
      <TooltipLayout node={node} color={color} />
    </div>
  );
};

export default NodeTooltipEnhanced;

