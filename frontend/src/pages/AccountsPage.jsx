import React, { useState, useEffect } from 'react';
import { accountService } from '../services/api';
import { Landmark, Plus, Trash2, Edit3, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

export default function AccountsPage() {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    bank_name: 'HDFC Bank',
    account_number: '',
    account_type: 'SAVINGS',
    currency: 'INR',
    opening_balance: '0.00',
  });
  const [msg, setMsg] = useState({ type: '', text: '' });

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const res = await accountService.list();
      setAccounts(res.data.results || res.data);
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to load bank accounts.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const openCreateModal = () => {
    setEditingAccount(null);
    setFormData({
      name: '',
      bank_name: 'HDFC Bank',
      account_number: '',
      account_type: 'SAVINGS',
      currency: 'INR',
      opening_balance: '0.00',
    });
    setShowModal(true);
  };

  const openEditModal = (acc) => {
    setEditingAccount(acc);
    setFormData({
      name: acc.name,
      bank_name: acc.bank_name,
      account_number: '', // keep blank unless user specifically updates
      account_type: acc.account_type,
      currency: acc.currency,
      opening_balance: acc.opening_balance,
    });
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      if (editingAccount) {
        const payload = { ...formData };
        if (!payload.account_number) delete payload.account_number;
        await accountService.update(editingAccount.id, payload);
        setMsg({ type: 'success', text: 'Account updated successfully.' });
      } else {
        await accountService.create(formData);
        setMsg({ type: 'success', text: 'Bank account created successfully.' });
      }
      setShowModal(false);
      fetchAccounts();
    } catch (err) {
      const errText = err.response?.data?.account_number?.[0] || err.response?.data?.error || 'Failed to save account.';
      setMsg({ type: 'error', text: errText });
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to remove '${name}'? All related statements and transactions will be removed.`)) return;
    try {
      await accountService.delete(id);
      setMsg({ type: 'success', text: 'Account deleted.' });
      fetchAccounts();
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to delete account.' });
    }
  };

  const handleRecalculate = async (id) => {
    try {
      const res = await accountService.recalculate(id);
      setMsg({ type: 'success', text: `Balance recalculated: ${res.data.balance}` });
      fetchAccounts();
    } catch (err) {
      setMsg({ type: 'error', text: 'Failed to recalculate balance.' });
    }
  };

  const formatCurrency = (amt, curr = 'INR') => {
    const sym = curr === 'INR' ? '₹' : (curr === 'USD' ? '$' : `${curr} `);
    return `${sym}${Number(amt || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Bank Account Portfolio</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Manage multiple bank, checking, and investment accounts safely.
          </p>
        </div>
        <button className="btn btn-primary" onClick={openCreateModal}>
          <Plus size={16} />
          <span>Add Bank Account</span>
        </button>
      </div>

      {msg.text && (
        <div
          style={{
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            marginBottom: '1.25rem',
            backgroundColor: msg.type === 'success' ? 'var(--accent-emerald-light)' : 'var(--accent-rose-light)',
            color: msg.type === 'success' ? 'var(--accent-emerald)' : 'var(--accent-rose)',
            fontSize: '0.85rem',
            fontWeight: 500,
          }}
        >
          {msg.text}
        </div>
      )}

      {loading ? (
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '3rem' }}>Loading accounts...</p>
      ) : accounts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem' }}>
          <Landmark size={44} style={{ color: 'var(--text-muted)', margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.5rem' }}>No Bank Accounts Connected</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', maxWidth: '420px', margin: '0 auto 1.5rem' }}>
            Add an account to begin uploading statement files (PDF, CSV, Excel) and extracting intelligent financial insights.
          </p>
          <button className="btn btn-primary" onClick={openCreateModal}>
            <Plus size={16} />
            <span>Create First Account</span>
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {accounts.map((acc) => (
            <div key={acc.id} className="card" style={{ marginBottom: 0, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <span className="badge badge-neutral">{acc.account_type}</span>
                  <div style={{ display: 'flex', gap: '0.35rem' }}>
                    <button
                      className="theme-toggle-btn"
                      onClick={() => handleRecalculate(acc.id)}
                      title="Recalculate Balance"
                      style={{ width: '30px', height: '30px' }}
                    >
                      <RefreshCw size={14} />
                    </button>
                    <button
                      className="theme-toggle-btn"
                      onClick={() => openEditModal(acc)}
                      title="Edit Account"
                      style={{ width: '30px', height: '30px' }}
                    >
                      <Edit3 size={14} />
                    </button>
                    <button
                      className="theme-toggle-btn"
                      onClick={() => handleDelete(acc.id, acc.name)}
                      title="Delete Account"
                      style={{ width: '30px', height: '30px', color: 'var(--accent-rose)' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>{acc.name}</h3>
                <div style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
                  {acc.bank_name} &nbsp;•&nbsp; <span style={{ fontFamily: 'var(--font-mono)' }}>{acc.masked_account_number}</span>
                </div>

                <div style={{ padding: '0.85rem', backgroundColor: 'var(--bg-tertiary)', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Calculated Current Balance</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
                    {formatCurrency(acc.balance, acc.currency)}
                  </div>
                  <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                    Opening balance: {formatCurrency(acc.opening_balance, acc.currency)}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Dialog */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                {editingAccount ? 'Edit Bank Account' : 'Connect New Bank Account'}
              </h3>
            </div>
            <form onSubmit={handleSave}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Account Nickname</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="e.g. Primary Salary Checking"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Bank Institution Name</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="e.g. HDFC Bank, Chase, State Bank of India"
                    value={formData.bank_name}
                    onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Account Number {editingAccount && <span style={{ color: 'var(--text-muted)' }}>(Leave blank to keep existing)</span>}
                  </label>
                  <input
                    type="text"
                    required={!editingAccount}
                    className="form-control"
                    placeholder="e.g. 5010049281729"
                    value={formData.account_number}
                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label className="form-label">Account Type</label>
                    <select
                      className="form-control"
                      value={formData.account_type}
                      onChange={(e) => setFormData({ ...formData, account_type: e.target.value })}
                    >
                      <option value="SAVINGS">Savings Account</option>
                      <option value="CHECKING">Checking / Current</option>
                      <option value="CREDIT_CARD">Credit Card</option>
                      <option value="INVESTMENT">Investment / Trading</option>
                      <option value="LOAN">Loan Account</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Currency</label>
                    <select
                      className="form-control"
                      value={formData.currency}
                      onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                    >
                      <option value="INR">INR (₹)</option>
                      <option value="USD">USD ($)</option>
                      <option value="EUR">EUR (€)</option>
                      <option value="GBP">GBP (£)</option>
                      <option value="CAD">CAD ($)</option>
                      <option value="AUD">AUD ($)</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Opening Initial Balance</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-control"
                    placeholder="0.00"
                    value={formData.opening_balance}
                    onChange={(e) => setFormData({ ...formData, opening_balance: e.target.value })}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingAccount ? 'Save Changes' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

