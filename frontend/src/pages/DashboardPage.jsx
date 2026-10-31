import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  ArrowUpRight,
  ArrowDownRight,
  Landmark,
  UploadCloud,
  FileCheck,
  Bot,
  Calendar,
  AlertCircle,
} from 'lucide-react';

export default function DashboardPage({ setCurrentPage, setPendingReviewId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const res = await analyticsService.getDashboard();
      setData(res.data);
    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const formatCurrency = (amount, currency = 'INR') => {
    const sym = currency === 'INR' ? '₹' : (currency === 'USD' ? '$' : `${currency} `);
    return `${sym}${Number(amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
        <p>Loading your financial intelligence dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{ color: 'var(--accent-rose)', marginBottom: '1rem' }}>{error}</div>
        <button className="btn btn-secondary" onClick={fetchDashboard}>Retry</button>
      </div>
    );
  }

  const {
    total_balance,
    total_income,
    total_expenses,
    net_savings,
    savings_rate,
    preferred_currency,
    monthly_trends,
    category_breakdown,
    recent_transactions,
    accounts,
    statements,
    transaction_count,
  } = data || {};

  return (
    <div>
      {/* KPI Cards Grid */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-header">
            <span>Total Balance</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--primary-light)', color: 'var(--primary)' }}>
              <Wallet size={20} />
            </div>
          </div>
          <div className="kpi-value">{formatCurrency(total_balance, preferred_currency)}</div>
          <div className="kpi-subtext">Across {accounts?.length || 0} active bank accounts</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span>Total Income (Credits)</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--accent-emerald-light)', color: 'var(--accent-emerald)' }}>
              <TrendingUp size={20} />
            </div>
          </div>
          <div className="kpi-value" style={{ color: 'var(--accent-emerald)' }}>
            {formatCurrency(total_income, preferred_currency)}
          </div>
          <div className="kpi-subtext positive">Verified deposits & payroll</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span>Total Expenses (Debits)</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--accent-rose-light)', color: 'var(--accent-rose)' }}>
              <TrendingDown size={20} />
            </div>
          </div>
          <div className="kpi-value" style={{ color: 'var(--accent-rose)' }}>
            {formatCurrency(total_expenses, preferred_currency)}
          </div>
          <div className="kpi-subtext negative">Categorized living & discretionary</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-header">
            <span>Net Savings & Rate</span>
            <div className="kpi-icon-wrap" style={{ backgroundColor: 'var(--accent-indigo-light)', color: 'var(--accent-indigo)' }}>
              <PiggyBank size={20} />
            </div>
          </div>
          <div className="kpi-value" style={{ color: net_savings >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
            {formatCurrency(net_savings, preferred_currency)}
          </div>
          <div className={`kpi-subtext ${savings_rate >= 20 ? 'positive' : ''}`}>
            Savings Rate: <strong>{savings_rate}%</strong>
          </div>
        </div>
      </div>

      {/* Quick Action Banner if no accounts or statements */}
      {accounts?.length === 0 && (
        <div className="card" style={{ backgroundColor: 'var(--primary-light)', borderColor: 'var(--primary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--primary-text)' }}>Welcome to BankSense AI!</h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                Start by connecting your first bank account and uploading a PDF, CSV, or Excel bank statement.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-primary" onClick={() => setCurrentPage('accounts')}>
                <Landmark size={16} />
                <span>Add Bank Account</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Visual Analytics Grid: Monthly Trends + Spending Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Monthly Income vs Expenses Chart / Bars */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div>
              <h2 className="card-title">Monthly Cash Flow Trends</h2>
              <p className="card-subtitle">Income vs Expenses over the past 6 months</p>
            </div>
          </div>

          {monthly_trends?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', paddingTop: '0.5rem' }}>
              {monthly_trends.map((item) => {
                const maxVal = Math.max(...monthly_trends.map((m) => Math.max(m.income, m.expense)), 1);
                const incPct = Math.min((item.income / maxVal) * 100, 100);
                const expPct = Math.min((item.expense / maxVal) * 100, 100);

                return (
                  <div key={item.month}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                      <span>{item.label}</span>
                      <span style={{ color: item.net >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
                        Net: {item.net >= 0 ? '+' : ''}{formatCurrency(item.net, preferred_currency)}
                      </span>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '55px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>Income</div>
                        <div style={{ flex: 1, backgroundColor: 'var(--bg-tertiary)', borderRadius: '4px', height: '10px', overflow: 'hidden' }}>
                          <div style={{ width: `${incPct}%`, height: '100%', backgroundColor: 'var(--accent-emerald)', borderRadius: '4px' }} />
                        </div>
                        <div style={{ width: '80px', fontSize: '0.725rem', textAlign: 'right', fontWeight: 600 }}>
                          {formatCurrency(item.income, preferred_currency)}
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div style={{ width: '55px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>Expense</div>
                        <div style={{ flex: 1, backgroundColor: 'var(--bg-tertiary)', borderRadius: '4px', height: '10px', overflow: 'hidden' }}>
                          <div style={{ width: `${expPct}%`, height: '100%', backgroundColor: 'var(--accent-rose)', borderRadius: '4px' }} />
                        </div>
                        <div style={{ width: '80px', fontSize: '0.725rem', textAlign: 'right', fontWeight: 600 }}>
                          {formatCurrency(item.expense, preferred_currency)}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No monthly activity data available yet.</p>
          )}
        </div>

        {/* Spending by Category */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div>
              <h2 className="card-title">Spending by Category</h2>
              <p className="card-subtitle">Auto-categorized debit expenditures</p>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => setCurrentPage('analytics')}>
              View Insights
            </button>
          </div>

          {category_breakdown?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {category_breakdown.slice(0, 6).map((cat) => (
                <div key={cat.category}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.825rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 600 }}>{cat.category}</span>
                    <span style={{ fontWeight: 700 }}>
                      {formatCurrency(cat.amount, preferred_currency)} <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>({cat.percentage}%)</span>
                    </span>
                  </div>
                  <div style={{ width: '100%', backgroundColor: 'var(--bg-tertiary)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${Math.min(cat.percentage, 100)}%`,
                        height: '100%',
                        backgroundColor: 'var(--primary)',
                        borderRadius: '4px',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Upload statements to view categorized spending.</p>
          )}
        </div>
      </div>

      {/* Connected Accounts & Recent Uploads */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Connected Bank Accounts */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <h2 className="card-title">Connected Accounts ({accounts?.length || 0})</h2>
            <button className="btn btn-secondary btn-sm" onClick={() => setCurrentPage('accounts')}>
              Manage
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {accounts?.map((acc) => (
              <div
                key={acc.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--bg-tertiary)',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{acc.name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {acc.bank_name} • {acc.masked_account_number}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>
                    {formatCurrency(acc.balance, acc.currency)}
                  </div>
                  <span className="badge badge-neutral">{acc.account_type}</span>
                </div>
              </div>
            ))}
            {accounts?.length === 0 && (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No accounts linked yet.</p>
            )}
          </div>
        </div>

        {/* Uploaded Statements History */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <h2 className="card-title">Recent Statements</h2>
            <button className="btn btn-secondary btn-sm" onClick={() => setCurrentPage('upload')}>
              Upload New
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {statements?.map((stmt) => (
              <div
                key={stmt.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--bg-tertiary)',
                }}
              >
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem' }}>{stmt.file_name}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    {stmt.account_name} • {stmt.total_transactions} txns
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span
                    className={`badge ${
                      stmt.status === 'CONFIRMED'
                        ? 'badge-credit'
                        : stmt.status === 'PREVIEW_READY'
                        ? 'badge-warning'
                        : 'badge-neutral'
                    }`}
                  >
                    {stmt.status}
                  </span>
                  {stmt.status === 'PREVIEW_READY' && (
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => {
                        setPendingReviewId(stmt.id);
                        setCurrentPage('review');
                      }}
                    >
                      Review
                    </button>
                  )}
                </div>
              </div>
            ))}
            {statements?.length === 0 && (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No statements uploaded yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Transactions Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Recent Transactions</h2>
            <p className="card-subtitle">Latest verified banking activity</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => setCurrentPage('transactions')}>
            Explore All ({transaction_count})
          </button>
        </div>

        <div className="table-responsive">
          <table className="banksense-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th>Account</th>
                <th>Type</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {recent_transactions?.map((tx) => (
                <tr key={tx.id}>
                  <td>{tx.date}</td>
                  <td style={{ fontWeight: 500 }}>{tx.description}</td>
                  <td>
                    <span className="badge badge-category">{tx.category}</span>
                  </td>
                  <td>{tx.account_name}</td>
                  <td>
                    <span className={`badge ${tx.transaction_type === 'CREDIT' ? 'badge-credit' : 'badge-debit'}`}>
                      {tx.transaction_type}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <span className={tx.transaction_type === 'CREDIT' ? 'amount-credit' : 'amount-debit'}>
                      {tx.transaction_type === 'CREDIT' ? '+' : '-'}
                      {formatCurrency(tx.amount, tx.currency)}
                    </span>
                  </td>
                </tr>
              ))}
              {recent_transactions?.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No transactions found. Upload your first statement to begin analysis.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

