import React, { useState, useEffect } from 'react';
import { transactionService, accountService, reportService } from '../services/api';
import { Search, Filter, Download, ArrowUpDown, Tag, ChevronLeft, ChevronRight, Check } from 'lucide-react';

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  // Filters state
  const [search, setSearch] = useState('');
  const [accountFilter, setAccountFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [minAmount, setMinAmount] = useState('');
  const [maxAmount, setMaxAmount] = useState('');
  const [ordering, setOrdering] = useState('-date');
  const [page, setPage] = useState(1);

  // Inline editing state
  const [editingId, setEditingId] = useState(null);
  const [editCategory, setEditCategory] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {
        page,
        search: search || undefined,
        account: accountFilter || undefined,
        category: categoryFilter || undefined,
        type: typeFilter || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        min_amount: minAmount || undefined,
        max_amount: maxAmount || undefined,
        ordering,
      };

      const [txRes, catRes, accRes] = await Promise.all([
        transactionService.list(params),
        transactionService.getCategories(),
        accountService.list(),
      ]);

      const data = txRes.data;
      if (data.results) {
        setTransactions(data.results);
        setTotalCount(data.count);
      } else {
        setTransactions(data);
        setTotalCount(data.length);
      }
      setCategories(catRes.data);
      setAccounts(accRes.data.results || accRes.data);
    } catch (err) {
      console.error('Error fetching transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [page, accountFilter, categoryFilter, typeFilter, startDate, endDate, ordering]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadData();
  };

  const handleUpdateCategory = async (txId) => {
    try {
      await transactionService.updateCategory(txId, { category: editCategory });
      setEditingId(null);
      loadData();
    } catch (err) {
      alert('Failed to update category.');
    }
  };

  const handleExportCSV = () => {
    const params = {
      account: accountFilter || undefined,
      category: categoryFilter || undefined,
      type: typeFilter || undefined,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    };
    const url = reportService.getCSVUrl(params);
    window.open(url, '_blank');
  };

  const formatCurrency = (amt, curr = 'INR') => {
    const sym = curr === 'INR' ? '₹' : '$';
    return `${sym}${Number(amt || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
  };

  const totalPages = Math.ceil(totalCount / 20) || 1;

  return (
    <div>
      <div className="card" style={{ marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <h2 className="card-title">Transaction Explorer</h2>
            <p className="card-subtitle">Search, filter, categorize, and audit verified transactions ({totalCount} total)</p>
          </div>

          <button className="btn btn-secondary" onClick={handleExportCSV}>
            <Download size={16} />
            <span>Export Filtered CSV</span>
          </button>
        </div>

        {/* Filter Controls Bar */}
        <form onSubmit={handleSearchSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.85rem' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Search Description / Ref</label>
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  className="form-control"
                  placeholder="e.g. Swiggy, Salary, Amazon..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Account</label>
              <select
                className="form-control"
                value={accountFilter}
                onChange={(e) => { setAccountFilter(e.target.value); setPage(1); }}
              >
                <option value="">All Accounts</option>
                {accounts.map((acc) => (
                  <option key={acc.id} value={acc.id}>
                    {acc.name} ({acc.bank_name})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Category</label>
              <select
                className="form-control"
                value={categoryFilter}
                onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
              >
                <option value="">All Categories</option>
                {categories.map((c) => (
                  <option key={c.value} value={c.value}>
                    {c.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Type</label>
              <select
                className="form-control"
                value={typeFilter}
                onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
              >
                <option value="">All Types (Debit & Credit)</option>
                <option value="DEBIT">Debit (Expenses Only)</option>
                <option value="CREDIT">Credit (Income Only)</option>
              </select>
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Date From</label>
              <input
                type="date"
                className="form-control"
                value={startDate}
                onChange={(e) => { setStartDate(e.target.value); setPage(1); }}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Date To</label>
              <input
                type="date"
                className="form-control"
                value={endDate}
                onChange={(e) => { setEndDate(e.target.value); setPage(1); }}
              />
            </div>

            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Sort Order</label>
              <select
                className="form-control"
                value={ordering}
                onChange={(e) => { setOrdering(e.target.value); setPage(1); }}
              >
                <option value="-date">Date: Newest First</option>
                <option value="date">Date: Oldest First</option>
                <option value="-amount">Amount: Highest First</option>
                <option value="amount">Amount: Lowest First</option>
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Transactions Table */}
      <div className="card">
        <div className="table-responsive">
          <table className="banksense-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Ref No</th>
                <th>Account</th>
                <th>Category</th>
                <th>Type</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
                <th style={{ textAlign: 'right' }}>Balance After</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    Loading transactions...
                  </td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    No transactions match the selected filters.
                  </td>
                </tr>
              ) : (
                transactions.map((t) => (
                  <tr key={t.id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '0.825rem' }}>{t.date}</td>
                    <td style={{ fontWeight: 500, maxWidth: '280px' }}>
                      <div>{t.description}</div>
                      {t.notes && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t.notes}</div>}
                    </td>
                    <td style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>{t.reference_number || '-'}</td>
                    <td style={{ fontSize: '0.825rem', whiteSpace: 'nowrap' }}>
                      {t.account_name}
                      <span style={{ display: 'block', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        {t.account_number_masked}
                      </span>
                    </td>
                    <td>
                      {editingId === t.id ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <select
                            className="form-control"
                            value={editCategory}
                            onChange={(e) => setEditCategory(e.target.value)}
                            style={{ padding: '0.2rem 0.4rem', fontSize: '0.775rem' }}
                          >
                            {categories.map((c) => (
                              <option key={c.value} value={c.value}>
                                {c.label}
                              </option>
                            ))}
                          </select>
                          <button
                            className="btn btn-primary btn-sm"
                            style={{ padding: '0.2rem 0.4rem' }}
                            onClick={() => handleUpdateCategory(t.id)}
                          >
                            <Check size={12} />
                          </button>
                        </div>
                      ) : (
                        <span
                          className="badge badge-category"
                          title="Click to edit category"
                          onClick={() => {
                            setEditingId(t.id);
                            setEditCategory(t.category);
                          }}
                        >
                          <Tag size={10} />
                          <span>{t.category}</span>
                        </span>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${t.transaction_type === 'CREDIT' ? 'badge-credit' : 'badge-debit'}`}>
                        {t.transaction_type}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <span className={t.transaction_type === 'CREDIT' ? 'amount-credit' : 'amount-debit'}>
                        {t.transaction_type === 'CREDIT' ? '+' : '-'}
                        {formatCurrency(t.amount, t.currency)}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '0.825rem' }}>
                      {t.balance_after ? formatCurrency(t.balance_after, t.currency) : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.825rem', color: 'var(--text-muted)' }}>
              Page <strong>{page}</strong> of <strong>{totalPages}</strong>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                className="btn btn-secondary btn-sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(p - 1, 1))}
              >
                <ChevronLeft size={16} />
                <span>Previous</span>
              </button>
              <button
                className="btn btn-secondary btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => Math.min(p + 1, totalPages))}
              >
                <span>Next</span>
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

