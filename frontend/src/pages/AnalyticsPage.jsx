import React, { useState, useEffect } from 'react';
import { analyticsService } from '../services/api';
import {
  PieChart,
  TrendingUp,
  TrendingDown,
  Repeat,
  AlertTriangle,
  Zap,
  CheckCircle2,
  Calendar,
} from 'lucide-react';

export default function AnalyticsPage() {
  const [insights, setInsights] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadAll = async () => {
      try {
        setLoading(true);
        const [insRes, dashRes] = await Promise.all([
          analyticsService.getInsights(),
          analyticsService.getDashboard(),
        ]);
        setInsights(insRes.data);
        setDashboard(dashRes.data);
      } catch (err) {
        console.error('Error loading analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    loadAll();
  }, []);

  const formatCurrency = (amt) => {
    return `₹${Number(amt || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
        Computing financial analytics, recurring patterns, and spending anomalies...
      </div>
    );
  }

  const { top_categories, recurring_transactions, unusual_transactions, month_over_month } = insights || {};

  return (
    <div>
      {/* Month over Month Highlights */}
      <div className="card" style={{ backgroundColor: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              Month-over-Month Velocity
            </div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>
              {month_over_month?.trend === 'INCREASED' ? 'Spending Increased' : month_over_month?.trend === 'DECREASED' ? 'Spending Reduced' : 'Stable Spending'}
            </h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Current Month: {formatCurrency(month_over_month?.current_month_expenses)} vs Previous Month:{' '}
              {formatCurrency(month_over_month?.previous_month_expenses)}
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span
              className={`badge ${
                month_over_month?.expense_change_percentage > 0 ? 'badge-debit' : 'badge-credit'
              }`}
              style={{ fontSize: '0.95rem', padding: '0.4rem 0.8rem' }}
            >
              {month_over_month?.expense_change_percentage > 0 ? '+' : ''}
              {month_over_month?.expense_change_percentage}%
            </span>
          </div>
        </div>
      </div>

      {/* Grid: Top Categories + Unusual Transactions */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Top Expense Categories */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div>
              <h3 className="card-title">Top 5 Expenditure Categories</h3>
              <p className="card-subtitle">Highest drains on your cashflow</p>
            </div>
            <PieChart size={20} style={{ color: 'var(--primary)' }} />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {top_categories?.map((c, i) => (
              <div key={c.category}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                  <span style={{ fontWeight: 600 }}>
                    #{i + 1} {c.category} ({c.count} transactions)
                  </span>
                  <span style={{ fontWeight: 700 }}>
                    {formatCurrency(c.amount)} <span style={{ color: 'var(--text-muted)' }}>({c.percentage}%)</span>
                  </span>
                </div>
                <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--bg-tertiary)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div
                    style={{
                      width: `${c.percentage}%`,
                      height: '100%',
                      backgroundColor: i === 0 ? 'var(--accent-rose)' : i === 1 ? 'var(--accent-amber)' : 'var(--primary)',
                      borderRadius: '4px',
                    }}
                  />
                </div>
              </div>
            ))}
            {top_categories?.length === 0 && (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No categorized debits found.</p>
            )}
          </div>
        </div>

        {/* Unusual Transactions / Anomalies */}
        <div className="card" style={{ marginBottom: 0 }}>
          <div className="card-header">
            <div>
              <h3 className="card-title">Anomalies & Unusual Spikes</h3>
              <p className="card-subtitle">Transactions exceeding statistical threshold</p>
            </div>
            <AlertTriangle size={20} style={{ color: 'var(--accent-amber)' }} />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {unusual_transactions?.map((a) => (
              <div
                key={a.id}
                style={{
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--bg-tertiary)',
                  borderLeft: `4px solid ${a.severity === 'HIGH' ? 'var(--accent-rose)' : 'var(--accent-amber)'}`,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.2rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{a.description}</span>
                  <span style={{ fontWeight: 700, color: 'var(--accent-rose)', fontFamily: 'var(--font-mono)' }}>
                    {formatCurrency(a.amount)}
                  </span>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                  {a.reason} &nbsp;•&nbsp; {a.date} ({a.account_name})
                </div>
              </div>
            ))}
            {unusual_transactions?.length === 0 && (
              <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
                <CheckCircle2 size={32} style={{ color: 'var(--accent-emerald)', margin: '0 auto 0.5rem' }} />
                <p style={{ fontSize: '0.85rem' }}>No unusual anomalies detected in your spending records.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recurring Transactions Section */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Recurring & Subscription Obligations</h3>
            <p className="card-subtitle">
              Repeated bills, rent, subscriptions, and periodic commitments detected across multiple months
            </p>
          </div>
          <Repeat size={20} style={{ color: 'var(--accent-indigo)' }} />
        </div>

        <div className="table-responsive">
          <table className="banksense-table">
            <thead>
              <tr>
                <th>Merchant / Obligation</th>
                <th>Category</th>
                <th>Occurrences</th>
                <th>Active Months</th>
                <th style={{ textAlign: 'right' }}>Average Monthly Amount</th>
              </tr>
            </thead>
            <tbody>
              {recurring_transactions?.map((r, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>{r.merchant_sample}</td>
                  <td>
                    <span className="badge badge-category">{r.category}</span>
                  </td>
                  <td>{r.occurrences} recorded</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {r.months_active?.join(', ')}
                  </td>
                  <td style={{ textAlign: 'right', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                    {formatCurrency(r.average_amount)}
                  </td>
                </tr>
              ))}
              {recurring_transactions?.length === 0 && (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No recurring patterns detected yet. Upload statements spanning 2 or more months.
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

