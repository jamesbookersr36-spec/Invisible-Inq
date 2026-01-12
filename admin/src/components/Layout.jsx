import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiHome, FiActivity, FiUsers, FiLogOut, FiMenu, FiX } from 'react-icons/fi';
import { useState } from 'react';

export function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { path: '/', icon: FiHome, label: 'Dashboard' },
    { path: '/activities', icon: FiActivity, label: 'Activities' },
    { path: '/users', icon: FiUsers, label: 'Users' },
  ];

  return (
    <div className="min-h-screen bg-black">
      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-[#09090B] text-white transform transition-transform duration-300 ease-in-out ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      } lg:translate-x-0`}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-[#27272A]">
          <div className="flex items-center gap-2.5">
            <img
              src="/logo/logo-with-text.png"
              alt="Invisible Inquiry Logo"
              className="h-7 object-contain"
              onError={(e) => {
                console.error("Logo image failed to load");
                e.target.style.display = 'none';
              }}
            />
            <h1 className="text-base font-semibold text-white">Admin</h1>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-gray-400 hover:text-white transition-colors"
          >
            <FiX size={24} />
          </button>
        </div>
        
        <nav className="mt-6 px-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center px-4 py-2.5 mb-1.5 rounded-lg transition-colors text-sm ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-300 hover:bg-[#27272A] hover:text-white'
                }`}
              >
                <Icon className="mr-3" size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 w-full p-4 border-t border-[#27272A]">
          <div className="mb-4 px-4">
            <p className="text-sm text-gray-400 mb-1">Logged in as</p>
            <p className="text-white font-medium truncate text-sm">{user?.email || user?.full_name || 'Admin'}</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center px-4 py-2.5 text-gray-300 hover:bg-[#27272A] hover:text-white rounded-lg transition-colors text-sm"
          >
            <FiLogOut className="mr-2" size={18} />
            Logout
          </button>
        </div>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-70 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="sticky top-0 z-30 bg-[#09090B]/80 backdrop-blur-sm shadow-sm border-b border-[#27272A]">
          <div className="flex items-center justify-between h-14 px-6">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-gray-400 hover:text-white transition-colors p-2"
            >
              <FiMenu size={20} />
            </button>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-white">{user?.full_name || user?.email || 'Admin'}</span>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-6 bg-black min-h-[calc(100vh-3.5rem)]">{children}</main>
      </div>
    </div>
  );
}
