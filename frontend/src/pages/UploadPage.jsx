import React, { useState, useEffect, useRef } from 'react';
import { statementService, accountService } from '../services/api';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, FileSpreadsheet, ArrowRight } from 'lucide-react';

export default function UploadPage({ setCurrentPage, setPendingReviewId }) {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState({ type: '', text: '' });
  const fileInputRef = useRef(null);

  useEffect(() => {
    accountService.list().then((res) => {
      const list = res.data.results || res.data;
      setAccounts(list);
      if (list.length > 0) {
        setSelectedAccountId(list[0].id);
      }
    });
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (selected) => {
    if (!selected) return;
    const ext = selected.name.split('.').pop().toLowerCase();
    if (!['pdf', 'csv', 'xlsx', 'xls'].includes(ext)) {
      setStatusMessage({
        type: 'error',
        text: `Invalid file format (.${ext}). BankSense AI supports PDF (.pdf), CSV (.csv), and Excel (.xlsx, .xls) statements.`,
      });
      return;
    }
    if (selected.size > 10 * 1024 * 1024) {
      setStatusMessage({
        type: 'error',
        text: 'File exceeds 10MB maximum upload limit.',
      });
      return;
    }
    setFile(selected);
    setStatusMessage({ type: '', text: '' });
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedAccountId) {
      setStatusMessage({ type: 'error', text: 'Please select a bank account to associate this statement.' });
      return;
    }
    if (!file) {
      setStatusMessage({ type: 'error', text: 'Please select a statement file to upload.' });
      return;
    }

    setUploading(true);
    setStatusMessage({ type: 'info', text: 'Uploading and parsing statement tables using transaction extraction engine...' });

    const formData = new FormData();
    formData.append('account', selectedAccountId);
    formData.append('file', file);

    try {
      const res = await statementService.upload(formData);
      const statement = res.data;
      setStatusMessage({
        type: 'success',
        text: `Statement parsed successfully! Found ${statement.total_transactions_count || 0} transactions. Redirecting to validation review...`,
      });

      // Navigate to review screen
      setTimeout(() => {
        setPendingReviewId(statement.id);
        setCurrentPage('review');
      }, 900);
    } catch (err) {
      const errMsg =
        err.response?.data?.error ||
        err.response?.data?.detail ||
        'Failed to parse statement. Please check the file formatting.';
      setStatusMessage({ type: 'error', text: errMsg });
      setUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: '780px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Upload Bank Statement</h2>
            <p className="card-subtitle">
              Securely extract, normalize, and reconcile transactions from PDF, CSV, or Excel
            </p>
          </div>
        </div>

        {accounts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
              You don't have any connected accounts yet. Please add a bank account before uploading statements.
            </p>
            <button className="btn btn-primary" onClick={() => setCurrentPage('accounts')}>
              Go to Accounts Portfolio
            </button>
          </div>
        ) : (
          <form onSubmit={handleUpload}>
            <div className="form-group">
              <label className="form-label">Associate with Bank Account</label>
              <select
                className="form-control"
                value={selectedAccountId}
                onChange={(e) => setSelectedAccountId(e.target.value)}
                required
              >
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name} ({acc.bank_name} • {acc.masked_account_number})
                  </option>
                ))}
              </select>
            </div>

            <div
              className={`dropzone ${dragActive ? 'active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current.click()}
              style={{ margin: '1.5rem 0' }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.csv,.xlsx,.xls"
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
              <UploadCloud size={44} style={{ color: 'var(--primary)', margin: '0 auto 0.75rem' }} />
              <div style={{ fontWeight: 600, fontSize: '1rem', marginBottom: '0.25rem' }}>
                {file ? file.name : 'Click to browse or drag & drop bank statement'}
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Supports standard PDF statements, CSV exports, or Excel spreadsheets (Max 10MB)
              </p>

              {file && (
                <div style={{ marginTop: '1rem' }}>
                  <span className="badge badge-credit">
                    {(file.size / 1024).toFixed(1)} KB &nbsp;•&nbsp; Ready to Parse
                  </span>
                </div>
              )}
            </div>

            {statusMessage.text && (
              <div
                style={{
                  padding: '0.85rem 1.15rem',
                  borderRadius: 'var(--radius-md)',
                  marginBottom: '1.25rem',
                  fontSize: '0.85rem',
                  fontWeight: 500,
                  backgroundColor:
                    statusMessage.type === 'error'
                      ? 'var(--accent-rose-light)'
                      : statusMessage.type === 'success'
                      ? 'var(--accent-emerald-light)'
                      : 'var(--primary-light)',
                  color:
                    statusMessage.type === 'error'
                      ? 'var(--accent-rose)'
                      : statusMessage.type === 'success'
                      ? 'var(--accent-emerald)'
                      : 'var(--primary-text)',
                }}
              >
                {statusMessage.text}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={!file || uploading}
                style={{ padding: '0.75rem 1.75rem' }}
              >
                <span>{uploading ? 'Extracting Transactions...' : 'Parse & Preview Statement'}</span>
                <ArrowRight size={16} />
              </button>
            </div>
          </form>
        )}
      </div>

      <div className="card">
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem' }}>
          💡 Testing with Sample Statements
        </h3>
        <p style={{ fontSize: '0.825rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          Realistic synthetic statements have been prepared in your workspace folder <code>sample_statements/</code>.
          You can test with <code>sample_bank_statement.csv</code>, <code>sample_salary_account.xlsx</code>, or{' '}
          <code>sample_premium_statement.pdf</code>.
        </p>
      </div>
    </div>
  );
}

