import React from 'react';
import { Sun, Moon, UploadCloud } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const PAGE_TITLES = {
  dashboard: 'Financial Dashboard',
  accounts: 'Bank Accounts',
  upload: 'Upload Bank Statement',
  review: 'Statement Review & Validation',
  transactions: 'Transaction Explorer',
  analytics: 'Analytics & Spending Insights',
  assistant: 'BankSense AI Assistant',
  reports: 'Reports & Export',
  settings: 'System & Profile Settings',
};

export default function Navbar({ currentPage, setCurrentPage }) {
  const { theme, toggleTheme } = useAuth();

  return (
    <header className="main-topbar">
      <h1 className="page-title">{PAGE_TITLES[currentPage] || 'BankSense AI'}</h1>

      <div className="topbar-actions">
        {currentPage !== 'upload' && (
          <button
            className="btn btn-primary btn-sm"
            onClick={() => setCurrentPage('upload')}
          >
            <UploadCloud size={16} />
            <span>Upload Statement</span>
          </button>
        )}

        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}

