import { useState, useEffect, useCallback, useMemo } from 'react';
import { FaTimes, FaSpinner, FaExclamationTriangle, FaSearch, FaRedo } from 'react-icons/fa';
import { getNodeTypeColor } from '../../utils/colorUtils';

/**
 * AISummaryModal - Displays AI-generated summaries with embedded entity buttons
 * 
 * The summary text contains [[Entity Name]] markers that are rendered as
 * clickable buttons. Clicking a button highlights/selects that entity in the graph.
 */
const AISummaryModal = ({ 
  isOpen, 
  onClose, 
  query: initialQuery = '',
  graphData = null,
  onEntityClick = null,
  apiBaseUrl = 'http://localhost:8000'
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Reset state when modal opens with new query
  useEffect(() => {
    if (isOpen && initialQuery) {
      setQuery(initialQuery);
      // Auto-fetch summary when modal opens with a query
      fetchSummary(initialQuery);
    }
  }, [isOpen, initialQuery]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      setSummary(null);
      setError(null);
    }
  }, [isOpen]);

  const fetchSummary = useCallback(async (searchQuery) => {
    if (!searchQuery?.trim() || !graphData) {
      setError('Please enter a question and ensure graph data is loaded.');
      return;
    }

    setLoading(true);
    setError(null);
    setSummary(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/ai/summary`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery.trim(),
          graphData: graphData
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Request failed: ${response.status}`);
      }

      const data = await response.json();
      setSummary(data);
    } catch (err) {
      console.error('Error fetching AI summary:', err);
      setError(err.message || 'Failed to generate summary. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [apiBaseUrl, graphData]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      fetchSummary(query);
    }
  };

  const handleRetry = () => {
    if (query.trim()) {
      fetchSummary(query);
    }
  };

  // Build a map of entity names to nodes for quick lookup
  const entityNodeMap = useMemo(() => {
    const map = new Map();
    if (graphData?.nodes) {
      graphData.nodes.forEach(node => {
        const name = node.name || node.entity_name || node.id;
        if (name) {
          map.set(name.toLowerCase(), node);
        }
      });
    }
    return map;
  }, [graphData]);

  // Parse summary text and render [[Entity]] as clickable buttons
  const renderSummaryWithButtons = useCallback((text) => {
    if (!text) return null;

    // Split by [[...]] pattern
    const parts = text.split(/(\[\[[^\]]+\]\])/g);

    return parts.map((part, index) => {
      // Check if this part is an entity marker
      const entityMatch = part.match(/^\[\[([^\]]+)\]\]$/);
      
      if (entityMatch) {
        const entityName = entityMatch[1];
        const node = entityNodeMap.get(entityName.toLowerCase());
        
        if (node) {
          const nodeType = node.node_type || node.type || 'Entity';
          const color = getNodeTypeColor(nodeType);
          
          return (
            <button
              key={`entity-${index}`}
              onClick={() => {
                if (onEntityClick) {
                  onEntityClick(node);
                }
              }}
              className="inline-flex items-center px-2 py-0.5 mx-0.5 text-sm font-medium rounded-full 
                         text-white hover:opacity-80 transition-all duration-200 
                         hover:scale-105 cursor-pointer border border-transparent
                         hover:border-white/30 shadow-sm"
              style={{ 
                backgroundColor: color,
                boxShadow: `0 0 8px ${color}40`
              }}
              title={`Click to highlight ${entityName} in graph`}
            >
              {entityName}
            </button>
          );
        } else {
          // Entity not found in graph - render as text with subtle styling
          return (
            <span 
              key={`entity-notfound-${index}`}
              className="inline-flex items-center px-2 py-0.5 mx-0.5 text-sm font-medium 
                         rounded-full bg-[#333] text-[#999] border border-[#444]"
              title={`${entityName} (not found in current graph)`}
            >
              {entityName}
            </span>
          );
        }
      }
      
      // Regular text
      return <span key={`text-${index}`}>{part}</span>;
    });
  }, [entityNodeMap, onEntityClick]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-[100] p-4">
      <div className="bg-[#0A0A0C] border border-[#333] rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col text-white overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[#333] flex-shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#4F46E5] to-[#7C3AED] flex items-center justify-center">
              <FaSearch className="text-white" size={14} />
            </div>
            <div>
              <h2 className="text-lg font-semibold">AI Analysis</h2>
              <p className="text-xs text-[#888]">Ask questions about your graph data</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[#222] rounded-lg transition-colors"
            title="Close"
          >
            <FaTimes className="text-[#888] hover:text-white" size={18} />
          </button>
        </div>

        {/* Search Input */}
        <form onSubmit={handleSubmit} className="p-4 border-b border-[#333] flex-shrink-0">
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about this graph..."
              className="w-full pl-4 pr-12 py-3 bg-[#131315] border border-[#444] rounded-lg 
                         text-white placeholder:text-[#666] focus:outline-none focus:border-[#4F46E5]
                         focus:ring-2 focus:ring-[#4F46E5]/20 transition-all"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg
                         bg-[#4F46E5] hover:bg-[#4338CA] disabled:bg-[#333] disabled:cursor-not-allowed
                         transition-colors"
              title="Generate Summary"
            >
              {loading ? (
                <FaSpinner className="animate-spin text-white" size={14} />
              ) : (
                <FaSearch className="text-white" size={14} />
              )}
            </button>
          </div>
          {graphData && (
            <div className="mt-2 text-xs text-[#666]">
              Analyzing {graphData.nodes?.length || 0} nodes and {graphData.links?.length || 0} relationships
            </div>
          )}
        </form>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-4 min-h-[200px]">
          {/* Loading State */}
          {loading && (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-[#888]">
              <div className="relative">
                <div className="w-12 h-12 rounded-full border-2 border-[#333]" />
                <div className="absolute inset-0 w-12 h-12 rounded-full border-2 border-t-[#4F46E5] animate-spin" />
              </div>
              <p className="text-sm">Analyzing graph data...</p>
            </div>
          )}

          {/* Error State */}
          {error && !loading && (
            <div className="flex flex-col items-center justify-center h-full gap-4">
              <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
                <FaExclamationTriangle className="text-red-500" size={20} />
              </div>
              <div className="text-center">
                <p className="text-red-400 font-medium mb-1">Error</p>
                <p className="text-sm text-[#888] max-w-md">{error}</p>
              </div>
              <button
                onClick={handleRetry}
                className="flex items-center gap-2 px-4 py-2 bg-[#222] hover:bg-[#333] 
                           rounded-lg text-sm transition-colors"
              >
                <FaRedo size={12} />
                Try Again
              </button>
            </div>
          )}

          {/* Summary Display */}
          {summary && !loading && !error && (
            <div className="space-y-4">
              {/* Query Badge */}
              <div className="flex items-start gap-2">
                <span className="px-2 py-1 bg-[#4F46E5]/20 text-[#A5B4FC] text-xs rounded-full flex-shrink-0">
                  Q
                </span>
                <p className="text-sm text-[#B4B4B4]">{summary.query}</p>
              </div>

              {/* Summary Text with Entity Buttons */}
              <div className="bg-[#111] rounded-lg p-4 border border-[#222]">
                <div className="flex items-start gap-2">
                  <span className="px-2 py-1 bg-[#22C55E]/20 text-[#86EFAC] text-xs rounded-full flex-shrink-0 mt-0.5">
                    A
                  </span>
                  <div className="text-[#E5E5E5] leading-relaxed text-sm whitespace-pre-wrap">
                    {renderSummaryWithButtons(summary.summary)}
                  </div>
                </div>
              </div>

              {/* Mentioned Entities */}
              {summary.entities && summary.entities.length > 0 && (
                <div className="bg-[#0D0D0F] rounded-lg p-3 border border-[#1a1a1a]">
                  <p className="text-xs text-[#666] mb-2">
                    Entities mentioned ({summary.entities.length}):
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {summary.entities.map((entity, idx) => {
                      const node = entityNodeMap.get(entity.name.toLowerCase());
                      const nodeType = node?.node_type || node?.type || 'Entity';
                      const color = getNodeTypeColor(nodeType);
                      
                      return (
                        <button
                          key={idx}
                          onClick={() => node && onEntityClick && onEntityClick(node)}
                          className="px-2 py-1 text-xs rounded-full text-white hover:opacity-80 
                                     transition-opacity cursor-pointer"
                          style={{ backgroundColor: color }}
                        >
                          {entity.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Stats Footer */}
              <div className="flex items-center justify-between text-xs text-[#666] pt-2 border-t border-[#222]">
                <span>
                  Based on {summary.node_count} nodes, {summary.link_count} relationships
                </span>
                <button
                  onClick={handleRetry}
                  className="flex items-center gap-1 hover:text-white transition-colors"
                >
                  <FaRedo size={10} />
                  Regenerate
                </button>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!loading && !error && !summary && (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-[#666]">
              <FaSearch size={32} className="opacity-30" />
              <p className="text-sm text-center">
                Enter a question above to get an AI-powered<br />
                analysis of your graph data
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AISummaryModal;


