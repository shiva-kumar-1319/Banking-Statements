import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Settings, Moon, Sun, ShieldCheck, Check, Sparkles } from 'lucide-react';

export default function SettingsPage() {
  const { user, theme, toggleTheme, updateProfile } = useAuth();
  const [currency, setCurrency] = useState(user?.profile?.preferred_currency || 'INR');
  const [firstName, setFirstName] = useState(user?.first_name || '');
  const [lastName, setLastName] = useState(user?.last_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [savedMsg, setSavedMsg] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await updateProfile({
        first_name: firstName,
        last_name: lastName,
        email: email,
        preferred_currency: currency,
      });
      setSavedMsg(true);
      setTimeout(() => setSavedMsg(false), 3000);
    } catch (err) {
      alert('Failed to update profile settings.');
    }
  };

  return (
    <div style={{ maxWidth: '780px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">User Profile & Platform Settings</h2>
            <p className="card-subtitle">Manage preferences, currency representation, and security</p>
          </div>
          <Settings size={22} style={{ color: 'var(--primary)' }} />
        </div>

        {savedMsg && (
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              marginBottom: '1.25rem',
              backgroundColor: 'var(--accent-emerald-light)',
              color: 'var(--accent-emerald)',
              fontSize: '0.85rem',
              fontWeight: 500,
            }}
          >
            Settings updated successfully!
          </div>
        )}

        <form onSubmit={handleSave}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">First Name</label>
              <input
                type="text"
                className="form-control"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Last Name</label>
              <input
                type="text"
                className="form-control"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Username (Immutable)</label>
            <input
              type="text"
              className="form-control"
              value={user?.username || ''}
              disabled
              style={{ opacity: 0.7 }}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-control"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Default Currency</label>
            <select
              className="form-control"
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
            >
              <option value="INR">Indian Rupee (INR ₹)</option>
              <option value="USD">US Dollar (USD $)</option>
              <option value="EUR">Euro (EUR €)</option>
              <option value="GBP">British Pound (GBP £)</option>
              <option value="CAD">Canadian Dollar (CAD $)</option>
              <option value="AUD">Australian Dollar (AUD $)</option>
            </select>
          </div>

          <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'flex-end' }}>
            <button type="submit" className="btn btn-primary">
              <Check size={16} />
              <span>Save Settings</span>
            </button>
          </div>
        </form>
      </div>

      {/* Visual Theme & Appearance Card */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '0.5rem' }}>Visual Theme & Appearance</h3>
        <p className="card-subtitle" style={{ marginBottom: '1.25rem' }}>
          Choose between Dark Obsidian mode and Clean Light fintech mode.
        </p>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button
            type="button"
            className={`btn ${theme === 'dark' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { if (theme !== 'dark') toggleTheme(); }}
          >
            <Moon size={16} />
            <span>Dark Theme</span>
          </button>
          <button
            type="button"
            className={`btn ${theme === 'light' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => { if (theme !== 'light') toggleTheme(); }}
          >
            <Sun size={16} />
            <span>Light Theme</span>
          </button>
        </div>
      </div>

      {/* Security & Intelligence Info */}
      <div className="card">
        <h3 className="card-title" style={{ marginBottom: '0.5rem' }}>Security & Engine Status</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
            <ShieldCheck size={18} style={{ color: 'var(--accent-emerald)' }} />
            <span><strong>Multi-Tenant Isolation:</strong> Data rows scoped strictly to authenticated user tokens.</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
            <Sparkles size={18} style={{ color: 'var(--primary)' }} />
            <span><strong>AI Grounding Engine:</strong> Deterministic Python financial aggregator with LLM zero-hallucination guarantee.</span>
          </div>
        </div>
      </div>
    </div>
  );
}

