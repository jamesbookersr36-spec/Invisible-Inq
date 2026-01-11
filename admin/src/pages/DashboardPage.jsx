import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { FiUsers, FiActivity, FiClock, FiEye } from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

const DashboardPage = () => {
  const { getToken } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState(7); // 7 or 30 days

  useEffect(() => {
    fetchDashboardData();
  }, [period]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = getToken();
      
      const response = await fetch(`${API_BASE_URL}/api/admin/statistics?days=${period}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      } else {
        setError('Failed to fetch dashboard data');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-dark-text-secondary">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg">
        Error: {error}
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Activities',
      value: dashboardData?.total_activities || 0,
      icon: FiActivity,
      color: 'bg-blue-500',
    },
    {
      name: 'Unique Users',
      value: dashboardData?.unique_users || 0,
      icon: FiUsers,
      color: 'bg-green-500',
    },
    {
      name: 'Unique Sessions',
      value: dashboardData?.unique_sessions || 0,
      icon: FiEye,
      color: 'bg-purple-500',
    },
    {
      name: 'Total Time (hours)',
      value: Math.round((dashboardData?.total_duration_seconds || 0) / 3600),
      icon: FiClock,
      color: 'bg-orange-500',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-dark-text">Analytics Dashboard</h1>
        <select
          value={period}
          onChange={(e) => setPeriod(Number(e.target.value))}
          className="px-4 py-2 border border-dark-border rounded-lg bg-dark-surface text-dark-text focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value={7}>Last 7 Days</option>
          <option value={30}>Last 30 Days</option>
        </select>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-dark-text-secondary">{stat.name}</p>
                  <p className="mt-2 text-3xl font-bold text-dark-text">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity by Type */}
        <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-dark-text mb-4">Activities by Type</h2>
          {dashboardData?.activities_by_type?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={dashboardData.activities_by_type}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => entry.type}
                >
                  {dashboardData.activities_by_type.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#18181B', border: '1px solid #27272A', color: '#FAFAFA' }} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-dark-text-secondary">
              No data available
            </div>
          )}
        </div>

        {/* Activities Over Time */}
        <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-dark-text mb-4">Activities Over Time</h2>
          {dashboardData?.activities_by_day?.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={dashboardData.activities_by_day}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                <XAxis dataKey="date" stroke="#A1A1AA" />
                <YAxis stroke="#A1A1AA" />
                <Tooltip contentStyle={{ backgroundColor: '#18181B', border: '1px solid #27272A', color: '#FAFAFA' }} />
                <Legend />
                <Line type="monotone" dataKey="count" stroke="#6366f1" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-dark-text-secondary">
              No data available
            </div>
          )}
        </div>
      </div>

      {/* Top Sections Viewed */}
      <div className="bg-dark-surface border border-dark-border rounded-lg shadow-lg p-6">
        <h2 className="text-lg font-semibold text-dark-text mb-4">Top Sections Viewed</h2>
        {dashboardData?.top_sections?.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={dashboardData.top_sections}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
              <XAxis dataKey="section" angle={-45} textAnchor="end" height={120} stroke="#A1A1AA" />
              <YAxis stroke="#A1A1AA" />
              <Tooltip contentStyle={{ backgroundColor: '#18181B', border: '1px solid #27272A', color: '#FAFAFA' }} />
              <Legend />
              <Bar dataKey="views" fill="#6366f1" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-64 text-dark-text-secondary">
            No section data available
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
