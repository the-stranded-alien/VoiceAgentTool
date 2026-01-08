import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Phone,
  History,
  Settings,
  Bot,
  X,
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NavItem {
  path: string;
  label: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  {
    path: '/',
    label: 'Dashboard',
    icon: <LayoutDashboard size={20} />,
  },
  {
    path: '/agent-configs',
    label: 'Agent Configs',
    icon: <Bot size={20} />,
  },
  {
    path: '/calls',
    label: 'Call History',
    icon: <History size={20} />,
  },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64
          bg-gradient-to-b from-purple-900 via-purple-800 to-indigo-900
          text-white shadow-2xl
          transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:z-30
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-purple-700/50">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-white/10 backdrop-blur-sm rounded-lg flex items-center justify-center">
              <Phone size={20} className="text-purple-200" />
            </div>
            <span className="font-bold text-lg">Voice Agent</span>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden p-1 rounded-lg hover:bg-white/10 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Navigation */}
        <nav className="px-3 py-6 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => onClose()}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                  isActive
                    ? 'bg-white/20 text-white shadow-lg backdrop-blur-sm'
                    : 'text-purple-100 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Bottom section */}
        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-purple-700/50">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center flex-shrink-0">
                <span className="text-lg">💡</span>
              </div>
              <div>
                <h4 className="font-semibold text-sm mb-1">Need Help?</h4>
                <p className="text-xs text-purple-200 mb-2">
                  Check our documentation
                </p>
                <button className="text-xs font-medium text-purple-200 hover:text-white transition-colors">
                  Learn More →
                </button>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};


