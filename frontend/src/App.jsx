import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import AuthPage from './pages/AuthPage';
import DashboardPage from './pages/DashboardPage';
import AccountsPage from './pages/AccountsPage';
import UploadPage from './pages/UploadPage';
import StatementReviewPage from './pages/StatementReviewPage';
import TransactionsPage from './pages/TransactionsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AssistantPage from './pages/AssistantPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';
import './App.css';

function MainApp() {
  const { user, loading } = useAuth();
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [pendingReviewId, setPendingReviewId] = useState(null);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-muted)',
        fontFamily: 'var(--font-family)',
      }}>
        Initializing BankSense AI...
      </div>
    );
  }

  if (!user) {
    return <AuthPage />;
  }

  return (
    <div className="banksense-app">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        pendingReviewId={pendingReviewId}
      />

      <div className="banksense-main">
        <Navbar currentPage={currentPage} setCurrentPage={setCurrentPage} />

        <main className="content-container">
          {currentPage === 'dashboard' && (
            <DashboardPage
              setCurrentPage={setCurrentPage}
              setPendingReviewId={setPendingReviewId}
            />
          )}

          {currentPage === 'accounts' && <AccountsPage />}

          {currentPage === 'upload' && (
            <UploadPage
              setCurrentPage={setCurrentPage}
              setPendingReviewId={setPendingReviewId}
            />
          )}

          {currentPage === 'review' && (
            <StatementReviewPage
              statementId={pendingReviewId}
              setCurrentPage={setCurrentPage}
              setPendingReviewId={setPendingReviewId}
            />
          )}

          {currentPage === 'transactions' && <TransactionsPage />}

          {currentPage === 'analytics' && <AnalyticsPage />}

          {currentPage === 'assistant' && <AssistantPage />}

          {currentPage === 'reports' && <ReportsPage />}

          {currentPage === 'settings' && <SettingsPage />}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
