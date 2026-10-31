import React, { useState, useRef, useEffect } from 'react';
import { assistantService } from '../services/api';
import { Bot, Send, Sparkles, User, ShieldCheck } from 'lucide-react';

const SUGGESTIONS = [
  'How much did I spend this month?',
  'Which category has the highest expenditure?',
  'What were my top five expenses?',
  'Compare my expenses this month with last month',
  'How much salary was credited?',
  'Show unusual transactions',
  'Summarize my financial activity',
  'How much did I save over the last three months?',
];

export default function AssistantPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I am **BankSense AI**, your intelligent financial assistant. I answer questions about your verified bank statements, spending categories, cash flow, and savings using deterministic math. Ask me anything about your finances!",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg = { role: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await assistantService.chat(textToSend);
      const aiMsg = {
        role: 'assistant',
        text: res.data.response,
        engine: res.data.engine,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        role: 'assistant',
        text: 'Sorry, I encountered an issue analyzing your financial query. Please try again.',
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const renderMarkdown = (content) => {
    // Basic Markdown Parser for bold, bullet points, headers, tables
    const lines = content.split('\n');
    const rendered = [];
    let inTable = false;
    let tableRows = [];

    lines.forEach((line, idx) => {
      if (line.startsWith('|') && line.endsWith('|')) {
        if (!inTable) inTable = true;
        tableRows.push(line);
      } else {
        if (inTable) {
          rendered.push(renderTable(tableRows, `table-${idx}`));
          inTable = false;
          tableRows = [];
        }

        if (line.startsWith('### ')) {
          rendered.push(
            <h4 key={idx} style={{ fontSize: '1rem', fontWeight: 700, margin: '0.6rem 0 0.3rem' }}>
              {line.replace('### ', '')}
            </h4>
          );
        } else if (line.startsWith('#### ')) {
          rendered.push(
            <h5 key={idx} style={{ fontSize: '0.9rem', fontWeight: 600, margin: '0.5rem 0 0.2rem' }}>
              {line.replace('#### ', '')}
            </h5>
          );
        } else if (line.startsWith('- ')) {
          rendered.push(
            <li key={idx} style={{ marginLeft: '1.25rem', marginBottom: '0.25rem' }}>
              {renderInline(line.substring(2))}
            </li>
          );
        } else if (line.trim() === '') {
          rendered.push(<div key={idx} style={{ height: '0.4rem' }} />);
        } else {
          rendered.push(
            <p key={idx} style={{ marginBottom: '0.35rem' }}>
              {renderInline(line)}
            </p>
          );
        }
      }
    });

    if (inTable) {
      rendered.push(renderTable(tableRows, 'table-end'));
    }

    return rendered;
  };

  const renderInline = (str) => {
    // Bold **text**
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  const renderTable = (rows, key) => {
    if (rows.length < 2) return null;
    const headerCells = rows[0].split('|').filter((c) => c.trim().length > 0);
    const bodyRows = rows.slice(2); // skip header and delimiter

    return (
      <div key={key} style={{ overflowX: 'auto', margin: '0.75rem 0' }}>
        <table className="banksense-table" style={{ fontSize: '0.8rem', backgroundColor: 'var(--bg-secondary)' }}>
          <thead>
            <tr>
              {headerCells.map((h, i) => (
                <th key={i}>{renderInline(h.trim())}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {bodyRows.map((r, rIdx) => {
              const cells = r.split('|').filter((c) => c.trim().length > 0);
              return (
                <tr key={rIdx}>
                  {cells.map((c, cIdx) => (
                    <td key={cIdx}>{renderInline(c.trim())}</td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div className="chat-window">
        {/* Chat Header */}
        <div style={{
          padding: '1rem 1.25rem',
          borderBottom: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-secondary)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div className="brand-icon" style={{ width: '32px', height: '32px', fontSize: '1rem' }}>
              <Bot size={18} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>BankSense Financial Intelligence</div>
              <div style={{ fontSize: '0.725rem', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <ShieldCheck size={12} />
                <span>Deterministic Grounded Analytics</span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.map((m, idx) => (
            <div key={idx} className={`chat-bubble ${m.role}`}>
              {m.role === 'assistant' ? renderMarkdown(m.text) : <p>{m.text}</p>}
              {m.engine && (
                <div style={{ fontSize: '0.675rem', color: 'var(--text-muted)', marginTop: '0.5rem', textAlign: 'right' }}>
                  Grounded Engine: {m.engine}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble assistant" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={16} style={{ color: 'var(--primary)', animation: 'spin 2s linear infinite' }} />
              <span>Querying verified financial database and calculating exact metrics...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Queries Chips */}
        <div style={{ padding: '0.5rem 1.25rem', backgroundColor: 'var(--bg-secondary)', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
            Suggested Questions:
          </div>
          <div className="prompt-chips">
            {SUGGESTIONS.map((s, idx) => (
              <button key={idx} className="prompt-chip" onClick={() => handleSend(s)}>
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <form
          className="chat-input-bar"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
        >
          <input
            type="text"
            className="form-control"
            placeholder="Ask anything about your spending, salary, top expenses, or savings..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={!input.trim() || loading}>
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}

