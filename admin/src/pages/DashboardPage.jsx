import { useState, useEffect } from 'react';
import { apiRequest } from '../utils/api';
import { FiUsers, FiActivity, FiTrendingUp, FiClock } from 'react-icons/fi';

export function DashboardPage() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiRequest('/api/admin/dashboard');
      setDashboardData(data);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
      console.error('Error fetching dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    );
  }

  const stats7d = dashboardData?.stats_7_days || {};
  const stats30d = dashboardData?.stats_30_days || {};
  const recentActivities = dashboardData?.recent_activities || [];

  const statCards = [
    {
      title: 'Total Activities (7 days)',
      value: stats7d.total_activities || 0,
      icon: FiActivity,
      color: 'blue',
      change: stats30d.total_activities ? 
        (((stats7d.total_activities || 0) / (stats30d.total_activities || 1)) * 100).toFixed(1) + '%' : 'N/A',
    },
    {
      title: 'Total Users (7 days)',
      value: stats7d.total_users || 0,
      icon: FiUsers,
      color: 'green',
      change: stats30d.total_users ? 
        (((stats7d.total_users || 0) / (stats30d.total_users || 1)) * 100).toFixed(1) + '%' : 'N/A',
    },
    {
      title: 'Active Sessions (7 days)',
      value: stats7d.active_sessions || 0,
      icon: FiTrendingUp,
      color: 'purple',
      change: stats30d.active_sessions ? 
        (((stats7d.active_sessions || 0) / (stats30d.active_sessions || 1)) * 100).toFixed(1) + '%' : 'N/A',
    },
    {
      title: 'Avg Duration (7 days)',
      value: stats7d.avg_session_duration ? 
        Math.round(stats7d.avg_session_duration / 60) + ' min' : '0 min',
      icon: FiClock,
      color: 'orange',
      change: stats30d.avg_session_duration ? 
        (((stats7d.avg_session_duration || 0) / (stats30d.avg_session_duration || 1)) * 100).toFixed(1) + '%' : 'N/A',
    },
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-500 text-white',
      green: 'bg-green-500 text-white',
      purple: 'bg-purple-500 text-white',
      orange: 'bg-orange-500 text-white',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Overview of system statistics and recent activities</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${getColorClasses(stat.color)}`}>
                  <Icon size={24} />
                </div>
                <span className="text-sm text-gray-500">{stat.change} of 30d</span>
              </div>
              <h3 className="text-sm font-medium text-gray-600 mb-1">{stat.title}</h3>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Recent Activities */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Recent Activities</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Activity Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentActivities.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                    No activities found
                  </td>
                </tr>
              ) : (
                recentActivities.map((activity, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {activity.user_email || activity.user_id || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800">
                        {activity.activity_type || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {activity.details || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.timestamp ? 
                        new Date(activity.timestamp).toLocaleString() : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
