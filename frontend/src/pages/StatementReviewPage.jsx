import React, { useState, useEffect } from 'react';
import { statementService, transactionService } from '../services/api';
import { CheckCircle2, AlertTriangle, ArrowRight, X, ShieldCheck, Tag } from 'lucide-react';

export default function StatementReviewPage({ statementId, setCurrentPage, setPendingReviewId }) {
  const [statement, setStatement] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!statementId) {
      setCurrentPage('dashboard');
      return;
    }

    const loadData = async () => {
      try {
        setLoading(true);
        const [stmtRes, catRes] = await Promise.all([
          statementService.get(statementId),
          transactionService.getCategories(),
        ]);
        setStatement(stmtRes.data);
        setTransactions(stmtRes.data.parsed_data?.transactions || []);
        setCategories(catRes.data);
      } catch (err) {
        setError('Failed to load statement preview.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [statementId]);

  const handleCategoryChange = (index, newCategory) => {
    const updated = [...transactions];
    updated[index] = {
      ...updated[index],
      category: newCategory,
      is_categorized_by_user: true,
      confidence: 1.0,
    };
    setTransactions(updated);
  };

  const handleConfirm = async () => {
    setConfirming(true);
    setError('');
    try {
      await statementService.confirm(statementId, { transactions });
      setPendingReviewId(null);
      setCurrentPage('transactions');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to finalize transaction import.');
      setConfirming(false);
    }
  };

  const handleDiscard = async () => {
    if (!window.confirm('Are you sure you want to discard this parsed statement preview?')) return;
    try {
      await statementService.delete(statementId);
      setPendingReviewId(null);
      setCurrentPage('upload');
    } catch (err) {
      setCurrentPage('dashboard');
    }
  };

  const formatCurrency = (amount) => {
    return `₹${Number(amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
        Loading statement preview...
      </div>
    );
  }

  if (error && !statement) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <p style={{ color: 'var(--accent-rose)', marginBottom: '1rem' }}>{error}</p>
        <button className="btn btn-secondary" onClick={() => setCurrentPage('upload')}>
          Back to Upload
        </button>
      </div>
    );
  }

  const {
    file_name,
    account_name,
    bank_name,
    extracted_opening_balance,
    extracted_closing_balance,
    total_credits,
    total_debits,
    reconciliation_status,
    reconciliation_difference,
  } = statement || {};

  return (
    <div>
      {/* Header & Status Card */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <span className="badge badge-warning" style={{ marginBottom: '0.5rem' }}>
              Pending Confirmation
            </span>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Statement Verification & Review</h2>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              File: <strong>{file_name}</strong> &nbsp;•&nbsp; Account: <strong>{account_name}</strong> ({bank_name})
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button className="btn btn-secondary" onClick={handleDiscard} disabled={confirming}>
              <X size={16} />
              <span>Discard</span>
            </button>
            <button className="btn btn-primary" onClick={handleConfirm} disabled={confirming}>
              <CheckCircle2 size={16} />
              <span>{confirming ? 'Importing Transactions...' : `Confirm & Import (${transactions.length})`}</span>
            </button>
          </div>
        </div>

        {error && (
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem',
            backgroundColor: 'var(--accent-rose-light)',
            color: 'var(--accent-rose)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.85rem'
          }}>
            {error}
          </div>
        )}

        {/* Reconciliation Banner */}
        <div
          style={{
            marginTop: '1.25rem',
            padding: '1rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            backgroundColor:
              reconciliation_status === 'RECONCILED'
                ? 'var(--accent-emerald-light)'
                : reconciliation_status === 'DISCREPANCY'
                ? 'var(--accent-amber-light)'
                : 'var(--bg-tertiary)',
            color:
              reconciliation_status === 'RECONCILED'
                ? 'var(--accent-emerald)'
                : reconciliation_status === 'DISCREPANCY'
                ? 'var(--accent-amber)'
                : 'var(--text-secondary)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {reconciliation_status === 'RECONCILED' ? (
              <CheckCircle2 size={22} />
            ) : (
              <AlertTriangle size={22} />
            )}
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>
                Reconciliation Status: {reconciliation_status}
              </div>
              <div style={{ fontSize: '0.8rem' }}>
                {reconciliation_status === 'RECONCILED'
                  ? 'Opening balance + deposits - withdrawals equals the verified statement closing balance.'
                  : reconciliation_status === 'DISCREPANCY'
                  ? `Calculated closing balance differs by ${formatCurrency(reconciliation_difference)}. Please inspect rows.`
                  : 'No explicit opening or closing balance detected in file text for cross-reconciliation.'}
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1.25rem', fontSize: '0.825rem', fontWeight: 600 }}>
            <div>Opening: <strong>{extracted_opening_balance ? formatCurrency(extracted_opening_balance) : 'N/A'}</strong></div>
            <div>Credits: <strong style={{ color: 'var(--accent-emerald)' }}>+{formatCurrency(total_credits)}</strong></div>
            <div>Debits: <strong style={{ color: 'var(--accent-rose)' }}>-{formatCurrency(total_debits)}</strong></div>
            <div>Closing: <strong>{extracted_closing_balance ? formatCurrency(extracted_closing_balance) : 'N/A'}</strong></div>
          </div>
        </div>
      </div>

      {/* Interactive Transactions Preview Table */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">Extracted Transactions Preview ({transactions.length})</h3>
            <p className="card-subtitle">
              Verify dates, amounts, and category classification. You may adjust any category before confirming.
            </p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="banksense-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Ref No</th>
                <th>Type</th>
                <th>Category</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
                <th style={{ textAlign: 'right' }}>Balance After</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t, idx) => (
                <tr key={idx}>
                  <td>{t.date}</td>
                  <td style={{ fontWeight: 500, maxWidth: '280px' }}>{t.description}</td>
                  <td style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>{t.reference_number || '-'}</td>
                  <td>
                    <span className={`badge ${t.transaction_type === 'CREDIT' ? 'badge-credit' : 'badge-debit'}`}>
                      {t.transaction_type}
                    </span>
                  </td>
                  <td>
                    <select
                      className="form-control"
                      value={t.category}
                      onChange={(e) => handleCategoryChange(idx, e.target.value)}
                      style={{ padding: '0.3rem 0.5rem', fontSize: '0.8rem', width: 'auto' }}
                    >
                      {categories.map((c) => (
                        <option key={c.value} value={c.value}>
                          {c.label}
                        </option>
                      ))}
                    </select>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <span className={t.transaction_type === 'CREDIT' ? 'amount-credit' : 'amount-debit'}>
                      {t.transaction_type === 'CREDIT' ? '+' : '-'}
                      {formatCurrency(t.amount)}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.825rem' }}>
                    {t.balance_after ? formatCurrency(t.balance_after) : '-'}
                  </td>
                </tr>
              ))}
              {transactions.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No transactions parsed from this statement.
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

