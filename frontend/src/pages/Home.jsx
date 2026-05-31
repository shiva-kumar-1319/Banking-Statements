const customers = [
  {
    name: 'Aarav Sharma',
    accountNumber: 'SB-10248',
    openedOn: '12 Jan 2022',
    balance: 84500,
    credited: 32000,
    debited: 12500,
    details: [
      { date: '24 May 2026', type: 'Credited', amount: 18000, note: 'Salary deposit' },
      { date: '26 May 2026', type: 'Debited', amount: 4500, note: 'Online shopping' },
      { date: '29 May 2026', type: 'Credited', amount: 14000, note: 'Client payment' },
    ],
  },
  {
    name: 'Meera Patel',
    accountNumber: 'SB-11893',
    openedOn: '04 Aug 2021',
    balance: 126750,
    credited: 47500,
    debited: 9800,
    details: [
      { date: '20 May 2026', type: 'Credited', amount: 42000, note: 'Business income' },
      { date: '23 May 2026', type: 'Debited', amount: 6800, note: 'Loan EMI' },
      { date: '30 May 2026', type: 'Credited', amount: 5500, note: 'Refund received' },
    ],
  },
  {
    name: 'Rohan Verma',
    accountNumber: 'SB-13420',
    openedOn: '19 Mar 2023',
    balance: 58200,
    credited: 22000,
    debited: 15200,
    details: [
      { date: '18 May 2026', type: 'Credited', amount: 22000, note: 'Freelance payout' },
      { date: '21 May 2026', type: 'Debited', amount: 7200, note: 'Rent transfer' },
      { date: '28 May 2026', type: 'Debited', amount: 8000, note: 'Card payment' },
    ],
  },
];

const formatMoney = (amount) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);

function Home() {
  const totalBalance = customers.reduce((total, customer) => total + customer.balance, 0);
  const totalCredited = customers.reduce((total, customer) => total + customer.credited, 0);
  const totalDebited = customers.reduce((total, customer) => total + customer.debited, 0);

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <p className="eyebrow">Bank Dashboard</p>
          <h1>Customer Banking Statement</h1>
          <p>Account balances, credit activity, debit activity, and recent details.</p>
        </div>
      </header>

      <main className="app-main">
        <section className="summary-grid" aria-label="Bank summary">
          <article className="summary-tile">
            <span>Total Balance</span>
            <strong>{formatMoney(totalBalance)}</strong>
          </article>
          <article className="summary-tile">
            <span>Total Credited</span>
            <strong className="positive">{formatMoney(totalCredited)}</strong>
          </article>
          <article className="summary-tile">
            <span>Total Debited</span>
            <strong className="negative">{formatMoney(totalDebited)}</strong>
          </article>
        </section>

        <section className="customer-grid" aria-label="Customer account details">
          {customers.map((customer) => (
            <article className="customer-card" key={customer.accountNumber}>
              <div className="customer-header">
                <div>
                  <h2>{customer.name}</h2>
                  <p>{customer.accountNumber}</p>
                </div>
                <span className="opened-date">Opened {customer.openedOn}</span>
              </div>

              <div className="money-grid">
                <div>
                  <span>Bank Balance</span>
                  <strong>{formatMoney(customer.balance)}</strong>
                </div>
                <div>
                  <span>Credited</span>
                  <strong className="positive">{formatMoney(customer.credited)}</strong>
                </div>
                <div>
                  <span>Debited</span>
                  <strong className="negative">{formatMoney(customer.debited)}</strong>
                </div>
              </div>

              <div className="transaction-list">
                <h3>Recent Details</h3>
                {customer.details.map((transaction) => (
                  <div className="transaction-row" key={`${customer.accountNumber}-${transaction.date}-${transaction.note}`}>
                    <div>
                      <span className="transaction-date">{transaction.date}</span>
                      <p>{transaction.note}</p>
                    </div>
                    <strong className={transaction.type === 'Credited' ? 'positive' : 'negative'}>
                      {transaction.type === 'Credited' ? '+' : '-'}
                      {formatMoney(transaction.amount)}
                    </strong>
                  </div>
                ))}
              </div>
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}

export default Home;
