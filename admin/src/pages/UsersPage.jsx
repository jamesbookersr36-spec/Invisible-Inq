import { useState, useEffect } from 'react';
import { apiRequest } from '../utils/api';
import { FiUsers, FiRefreshCw, FiMail, FiUser, FiCheckCircle, FiXCircle } from 'react-icons/fi';
import Loader from '../components/Loader';

export function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await apiRequest('/api/admin/users?limit=1000');
      console.log('API Response:', data);
      
      // Handle different response formats
      let usersArray = [];
      if (Array.isArray(data)) {
        usersArray = data;
      } else if (data && Array.isArray(data.users)) {
        usersArray = data.users;
      } else if (data && typeof data === 'object') {
        // If it's an object, try to extract users array
        usersArray = Object.values(data).find(val => Array.isArray(val)) || [];
      }
      
      setUsers(usersArray);
      console.log('Processed users:', usersArray.length, usersArray);
      
      if (usersArray.length === 0 && !loading) {
        console.warn('No users returned from API');
      }
    } catch (err) {
      const errorMessage = err.message || 'Failed to load users';
      setError(errorMessage);
      console.error('Error fetching users:', err);
      setUsers([]); // Clear users on error
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchUsers();
  };

  if (loading && users.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <span className="loader"></span>
      </div>
    );
  }

  // Calculate statistics - handle null/undefined values properly
  const totalUsers = users.length;
  // Count active users: is_active is true, or null/undefined (defaults to active)
  const activeUsers = users.filter(u => {
    const isActive = u.is_active;
    return isActive === true || isActive === undefined || isActive === null;
  }).length;
  // Count admin users: is_admin must be explicitly true
  const adminUsers = users.filter(u => u.is_admin === true).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">User Management</h1>
          <p className="text-gray-400 text-sm">View and manage all users</p>
        </div>
        <button
          onClick={handleRefresh}
          className="flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
        >
          <FiRefreshCw className="mr-2" size={16} />
          Refresh
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-[#18181B] rounded-lg shadow-sm border border-[#27272A] p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 rounded-lg bg-indigo-500 text-white flex items-center justify-center w-11 h-11">
              <FiUsers size={20} />
            </div>
          </div>
          <h3 className="text-xs font-medium text-gray-400 mb-1.5">Total Users</h3>
          <p className="text-2xl font-bold text-white">{totalUsers}</p>
        </div>
        <div className="bg-[#18181B] rounded-lg shadow-sm border border-[#27272A] p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 rounded-lg bg-green-500 text-white flex items-center justify-center w-11 h-11">
              <FiCheckCircle size={20} />
            </div>
          </div>
          <h3 className="text-xs font-medium text-gray-400 mb-1.5">Active Users</h3>
          <p className="text-2xl font-bold text-white">{activeUsers}</p>
        </div>
        <div className="bg-[#18181B] rounded-lg shadow-sm border border-[#27272A] p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="p-2.5 rounded-lg bg-purple-500 text-white flex items-center justify-center w-11 h-11">
              <FiUser size={20} />
            </div>
          </div>
          <h3 className="text-xs font-medium text-gray-400 mb-1.5">Admin Users</h3>
          <p className="text-2xl font-bold text-white">{adminUsers}</p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-900/20 border border-red-500 text-red-400 px-4 py-3 rounded-lg mb-4">
          <p className="font-medium">Error loading users:</p>
          <p className="text-sm mt-1">{error}</p>
          <p className="text-xs mt-2 text-red-300">Check browser console for details.</p>
        </div>
      )}
      
      {/* Debug Info (only in development) */}
      {process.env.NODE_ENV === 'development' && users.length === 0 && !loading && (
        <div className="bg-yellow-900/20 border border-yellow-500 text-yellow-400 px-4 py-3 rounded-lg mb-4">
          <p className="text-sm">Debug: No users found. Check console for API response details.</p>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-[#18181B] rounded-lg shadow-sm border border-[#27272A]">
        <div className="px-6 py-4 border-b border-[#27272A]">
          <h2 className="text-xl font-semibold text-white">
            All Users ({users.length})
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-[#09090B]">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Auth Provider
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                  Created At
                </th>
              </tr>
            </thead>
            <tbody className="bg-[#18181B] divide-y divide-[#27272A]">
              {users.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-gray-400">
                    {loading ? 'Loading...' : 'No users found'}
                  </td>
                </tr>
              ) : (
                users.map((user, index) => (
                  <tr key={index} className="hover:bg-[#09090B]">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center">
                        <FiMail className="mr-2 text-gray-400" size={16} />
                        <span className="text-sm font-medium text-white">
                          {user.email || '-'}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-400">
                      {user.full_name || '-'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium rounded-full bg-[#27272A] text-gray-300">
                        {user.auth_provider || 'local'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {user.is_active !== false ? (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-green-600/20 text-green-400 border border-green-600/30">
                          <FiCheckCircle className="mr-1" size={12} />
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 text-xs font-medium rounded-full bg-red-600/20 text-red-400 border border-red-600/30">
                          <FiXCircle className="mr-1" size={12} />
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {user.is_admin ? (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-600/20 text-purple-400 border border-purple-600/30">
                          Admin
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-[#27272A] text-gray-300">
                          User
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-400">
                      {user.created_at ? 
                        new Date(user.created_at).toLocaleDateString() : '-'}
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
