import React from 'react';
import {
  LayoutDashboard,
  Landmark,
  UploadCloud,
  ArrowLeftRight,
  PieChart,
  Bot,
  FileText,
  Settings,
  LogOut,
  FileCheck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'accounts', label: 'Accounts', icon: Landmark },
  { id: 'upload', label: 'Upload Statement', icon: UploadCloud },
  { id: 'transactions', label: 'Transactions', icon: ArrowLeftRight },
  { id: 'analytics', label: 'Analytics & Insights', icon: PieChart },
  { id: 'assistant', label: 'AI Assistant', icon: Bot },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ currentPage, setCurrentPage, pendingReviewId }) {
  const { user, logout } = useAuth();

  return (
    <aside className="banksense-sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">B</div>
        <div>
          <div className="brand-title">BankSense AI</div>
          <div className="brand-subtitle">Financial Intelligence</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setCurrentPage(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}

        {pendingReviewId && (
          <button
            className={`nav-item ${currentPage === 'review' ? 'active' : ''}`}
            onClick={() => setCurrentPage('review')}
            style={{ color: 'var(--accent-amber)' }}
          >
            <FileCheck size={18} />
            <span>Review Statement</span>
          </button>
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile-badge">
          <div className="user-avatar">
            {user?.username ? user.username[0].toUpperCase() : 'U'}
          </div>
          <div className="user-info">
            <div className="user-name">{user?.get_full_name || user?.username || 'User'}</div>
            <div className="user-email">{user?.email || 'Authenticated'}</div>
          </div>
        </div>

        <button className="nav-item" onClick={logout} style={{ color: 'var(--accent-rose)' }}>
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}

