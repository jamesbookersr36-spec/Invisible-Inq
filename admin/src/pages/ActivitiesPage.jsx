import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { format } from 'date-fns';
import { FiSearch, FiFilter } from 'react-icons/fi';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const ActivitiesPage = () => {
  const { getToken } = useAuth();
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    days: 7,
    activity_type: '',
    limit: 100
  });

  useEffect(() => {
    fetchActivities();
  }, [filters]);

  const fetchActivities = async () => {
    try {
      setLoading(true);
      const token = getToken();
      
      const params = new URLSearchParams();
      if (filters.days) params.append('days', filters.days);
      if (filters.activity_type) params.append('activity_type', filters.activity_type);
      if (filters.limit) params.append('limit', filters.limit);

      const response = await fetch(
        `${API_BASE_URL}/api/admin/activities?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setActivities(data);
      } else {
        setError('Failed to fetch activities');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const activityTypes = [
    { value: '', label: 'All Types' },
    { value: 'page_view', label: 'Page View' },
    { value: 'section_view', label: 'Section View' },
    { value: 'graph_interaction', label: 'Graph Interaction' },
    { value: 'search', label: 'Search' },
  ];

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      return format(new Date(timestamp), 'MMM dd, yyyy HH:mm:ss');
    } catch {
      return 'Invalid date';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-dark-text">User Activities</h1>
        <p className="mt-1 text-sm text-dark-text-secondary">
          Track and analyze user behavior and interactions
        </p>
      </div>

      {/* Filters */}
      <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <FiFilter className="w-5 h-5 text-dark-text-secondary" />
          <h2 className="text-lg font-semibold text-dark-text">Filters</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">
              Time Period
            </label>
            <select
              value={filters.days}
              onChange={(e) => setFilters({ ...filters, days: Number(e.target.value) })}
              className="w-full px-4 py-2 border border-dark-border rounded-lg bg-dark-bg text-dark-text focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value={1}>Last 24 Hours</option>
              <option value={7}>Last 7 Days</option>
              <option value={30}>Last 30 Days</option>
              <option value={90}>Last 90 Days</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">
              Activity Type
            </label>
            <select
              value={filters.activity_type}
              onChange={(e) => setFilters({ ...filters, activity_type: e.target.value })}
              className="w-full px-4 py-2 border border-dark-border rounded-lg bg-dark-bg text-dark-text focus:outline-none focus:ring-2 focus:ring-accent"
            >
              {activityTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-dark-text mb-2">
              Results Limit
            </label>
            <select
              value={filters.limit}
              onChange={(e) => setFilters({ ...filters, limit: Number(e.target.value) })}
              className="w-full px-4 py-2 border border-dark-border rounded-lg bg-dark-bg text-dark-text focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
              <option value={500}>500</option>
            </select>
          </div>
        </div>
      </div>

      {/* Activities Table */}
      <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-lg text-dark-text-secondary">Loading activities...</div>
          </div>
        ) : error ? (
          <div className="p-6 bg-red-900/20 border border-red-500 text-red-400">
            Error: {error}
          </div>
        ) : activities.length === 0 ? (
          <div className="flex items-center justify-center h-64 text-dark-text-secondary">
            No activities found
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-dark-border">
              <thead className="bg-dark-bg">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                    Timestamp
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                    Section/Page
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-dark-text-secondary uppercase tracking-wider">
                    Session
                  </th>
                </tr>
              </thead>
              <tbody className="bg-dark-surface divide-y divide-dark-border">
                {activities.map((activity) => (
                  <tr key={activity.id} className="hover:bg-dark-bg transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-text">
                      {formatTimestamp(activity.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-text">
                      {activity.user_email ? (
                        <div>
                          <div className="font-medium">{activity.user_name || 'Unknown'}</div>
                          <div className="text-dark-text-secondary">{activity.user_email}</div>
                        </div>
                      ) : (
                        <span className="text-dark-text-secondary">Anonymous</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        activity.activity_type === 'page_view' ? 'bg-blue-900/30 text-blue-400' :
                        activity.activity_type === 'section_view' ? 'bg-green-900/30 text-green-400' :
                        activity.activity_type === 'search' ? 'bg-purple-900/30 text-purple-400' :
                        'bg-gray-700 text-gray-300'
                      }`}>
                        {activity.activity_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-dark-text max-w-xs truncate">
                      {activity.section_title || activity.page_url || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-text">
                      {formatDuration(activity.duration_seconds)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-dark-text-secondary font-mono text-xs">
                      {activity.session_id?.substring(0, 12)}...
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Results Info */}
      {activities.length > 0 && (
        <div className="text-sm text-dark-text-secondary text-center">
          Showing {activities.length} activities
        </div>
      )}
    </div>
  );
};

export default ActivitiesPage;
