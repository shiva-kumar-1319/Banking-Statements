import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Landmark, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function AuthPage() {
  const { login, register } = useAuth();
  const [isRegister, setIsRegister] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    preferred_currency: 'INR',
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isRegister) {
        if (form.password !== form.password_confirm) {
          setError('Passwords do not match');
          setLoading(false);
          return;
        }
        await register(form);
      } else {
        await login(form.username, form.password);
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.password?.[0] ||
        err.response?.data?.username?.[0] ||
        err.response?.data?.error ||
        'Authentication failed. Please verify your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      backgroundColor: 'var(--bg-primary)'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '440px',
        backgroundColor: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-xl)',
        padding: '2.5rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <div className="brand-icon">B</div>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>BankSense AI</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Intelligent Financial Platform</p>
          </div>
        </div>

        <div style={{
          display: 'flex',
          borderBottom: '1px solid var(--border-color)',
          marginBottom: '1.75rem',
        }}>
          <button
            type="button"
            onClick={() => { setIsRegister(false); setError(''); }}
            style={{
              flex: 1,
              padding: '0.75rem',
              fontWeight: 600,
              fontSize: '0.9rem',
              color: !isRegister ? 'var(--primary)' : 'var(--text-muted)',
              borderBottom: !isRegister ? '2px solid var(--primary)' : 'none',
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setIsRegister(true); setError(''); }}
            style={{
              flex: 1,
              padding: '0.75rem',
              fontWeight: 600,
              fontSize: '0.9rem',
              color: isRegister ? 'var(--primary)' : 'var(--text-muted)',
              borderBottom: isRegister ? '2px solid var(--primary)' : 'none',
            }}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div style={{
            backgroundColor: 'var(--accent-rose-light)',
            color: 'var(--accent-rose)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.825rem',
            marginBottom: '1.25rem',
            border: '1px solid rgba(244, 63, 94, 0.2)',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              <div className="form-group">
                <label className="form-label">First Name</label>
                <input
                  type="text"
                  name="first_name"
                  className="form-control"
                  placeholder="Aarav"
                  value={form.first_name}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Last Name</label>
                <input
                  type="text"
                  name="last_name"
                  className="form-control"
                  placeholder="Sharma"
                  value={form.last_name}
                  onChange={handleChange}
                />
              </div>
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              name="username"
              required
              className="form-control"
              placeholder="e.g. aarav_sharma"
              value={form.username}
              onChange={handleChange}
            />
          </div>

          {isRegister && (
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input
                type="email"
                name="email"
                required
                className="form-control"
                placeholder="aarav@example.com"
                value={form.email}
                onChange={handleChange}
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              required
              className="form-control"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
            />
          </div>

          {isRegister && (
            <>
              <div className="form-group">
                <label className="form-label">Confirm Password</label>
                <input
                  type="password"
                  name="password_confirm"
                  required
                  className="form-control"
                  placeholder="••••••••"
                  value={form.password_confirm}
                  onChange={handleChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Preferred Currency</label>
                <select
                  name="preferred_currency"
                  className="form-control"
                  value={form.preferred_currency}
                  onChange={handleChange}
                >
                  <option value="INR">Indian Rupee (INR ₹)</option>
                  <option value="USD">US Dollar (USD $)</option>
                  <option value="EUR">Euro (EUR €)</option>
                  <option value="GBP">British Pound (GBP £)</option>
                  <option value="CAD">Canadian Dollar (CAD $)</option>
                  <option value="AUD">Australian Dollar (AUD $)</option>
                </select>
              </div>
            </>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem', padding: '0.75rem' }}
            disabled={loading}
          >
            <span>{loading ? 'Processing...' : isRegister ? 'Register Account' : 'Sign In to Dashboard'}</span>
            <ArrowRight size={16} />
          </button>
        </form>

        <div style={{
          marginTop: '1.75rem',
          paddingTop: '1.25rem',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.775rem',
          color: 'var(--text-muted)'
        }}>
          <ShieldCheck size={16} style={{ color: 'var(--accent-emerald)' }} />
          <span>Strict end-to-end data isolation & 256-bit encryption.</span>
        </div>
      </div>
    </div>
  );
}

