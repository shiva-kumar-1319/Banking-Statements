import React, { useState, useEffect } from 'react';
import { accountService, reportService } from '../services/api';
import { FileText, Download, Calendar, Landmark, CheckCircle2 } from 'lucide-react';

export default function ReportsPage() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    accountService.list().then((res) => {
      setAccounts(res.data.results || res.data);
    });
  }, []);

  const handleDownloadPDF = () => {
    const params = {
      account: selectedAccount || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    };
    const url = reportService.getPDFUrl(params);
    window.open(url, '_blank');
  };

  const handleDownloadCSV = () => {
    const params = {
      account: selectedAccount || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    };
    const url = reportService.getCSVUrl(params);
    window.open(url, '_blank');
  };

  return (
    <div style={{ maxWidth: '820px', margin: '0 auto' }}>
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Financial Reports & Exports</h2>
            <p className="card-subtitle">
              Generate executive-ready PDF audit reports and raw CSV transaction records
            </p>
          </div>
          <FileText size={24} style={{ color: 'var(--primary)' }} />
        </div>

        {/* Filter Selection */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Scope by Account</label>
            <select
              className="form-control"
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
            >
              <option value="">All Connected Accounts</option>
              {accounts.map((acc) => (
                <option key={acc.id} value={acc.id}>
                  {acc.name} ({acc.bank_name})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Start Date (Optional)</label>
            <input
              type="date"
              className="form-control"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>

          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">End Date (Optional)</label>
            <input
              type="date"
              className="form-control"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>

        {/* Export Options Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
          {/* PDF Report Option */}
          <div
            style={{
              padding: '1.25rem',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-tertiary)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <FileText size={20} style={{ color: 'var(--accent-rose)' }} />
                <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Official PDF Statement Report</h3>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.25rem', lineHeight: 1.5 }}>
                Includes executive summary, balance sheet metrics, category spending distributions, and transaction audit tables formatted for printing or filing.
              </p>
            </div>

            <button className="btn btn-primary" onClick={handleDownloadPDF} style={{ width: '100%' }}>
              <Download size={16} />
              <span>Download PDF Summary Report</span>
            </button>
          </div>

          {/* CSV Export Option */}
          <div
            style={{
              padding: '1.25rem',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-tertiary)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Download size={20} style={{ color: 'var(--accent-emerald)' }} />
                <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Raw Transaction Data (CSV)</h3>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.25rem', lineHeight: 1.5 }}>
                Exports all filtered transactions with reference numbers, classifications, and exact Decimal amounts for spreadsheet analysis in Excel or Google Sheets.
              </p>
            </div>

            <button className="btn btn-secondary" onClick={handleDownloadCSV} style={{ width: '100%' }}>
              <Download size={16} />
              <span>Download Raw CSV File</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

