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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
      return (
        <div className="bg-red-900/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
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
      blue: 'bg-indigo-500 text-white',
      green: 'bg-green-500 text-white',
      purple: 'bg-purple-500 text-white',
      orange: 'bg-orange-500 text-white',
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-gray-400 text-sm">Overview of system statistics and recent activities</p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="bg-[#18181B] rounded-lg shadow-sm border border-[#27272A] p-5">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2.5 rounded-lg flex items-center justify-center w-11 h-11 ${getColorClasses(stat.color)}`}>
                  <Icon size={20} />
                </div>
                <span className="text-xs text-gray-400">{stat.change} of 30d</span>
              </div>
              <h3 className="text-xs font-medium text-gray-400 mb-1.5">{stat.title}</h3>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
            </div>
          );
        })}
      </div>

      {/* Recent Activities */}
      <div className="bg-[#18181B] rounded-lg shadow-sm border border-[#27272A]">
        <div className="px-6 py-4 border-b border-[#27272A]">
          <h2 className="text-xl font-semibold text-white">Recent Activities</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#09090B]">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  User
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Activity Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Details
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="bg-[#18181B] divide-y divide-[#27272A]">
              {recentActivities.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-4 py-8 text-center text-gray-400">
                    No activities found
                  </td>
                </tr>
              ) : (
                recentActivities.map((activity, index) => (
                  <tr key={index} className="hover:bg-[#27272A]">
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-white">
                      {activity.user_email || activity.user_id || 'Unknown'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-indigo-600 text-white">
                        {activity.activity_type || 'N/A'}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-300">
                      {activity.details || '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-400">
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
