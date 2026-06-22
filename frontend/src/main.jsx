import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity,
  Brain,
  CheckCircle2,
  ShieldCheck,
  Zap,
  RefreshCw,
  TerminalSquare,
} from 'lucide-react';
import './styles.css';

const API = 'http://localhost:8000';

function statusClass(status) {
  if (status === 'RESOLVED') return 'resolved';
  if (status === 'AWAITING_APPROVAL') return 'approval';
  if (status === 'BLOCKED') return 'blocked';
  return 'active';
}

function logLevelClass(level) {
  if (level === 'ERROR') return 'error';
  if (level === 'WARN') return 'warn';
  return 'info';
}

function App() {
  const [incidents, setIncidents] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [logs, setLogs] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(false);

  async function loadIncidents() {
    try {
      const res = await fetch(`${API}/incidents`);
      const data = await res.json();

      setIncidents(data);

      if (!selectedId && data.length > 0) {
        setSelectedId(data[0].id);
      }
    } catch (error) {
      console.error('Failed to load incidents:', error);
    }
  }

  async function loadMetrics() {
    try {
      const res = await fetch(`${API}/metrics`);
      const data = await res.json();

      setMetrics(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load metrics:', error);
    }
  }

  async function loadLogs() {
    try {
      const res = await fetch(`${API}/logs`);
      const data = await res.json();

      setLogs(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load logs:', error);
    }
  }

  async function inject(path) {
    try {
      setLoading(true);

      const res = await fetch(`${API}${path}`, { method: 'POST' });
      const createdIncident = await res.json();

      await refreshAll();

      setSelectedId(createdIncident.id);
    } catch (error) {
      console.error('Failed to inject incident:', error);
    } finally {
      setLoading(false);
    }
  }

  async function runObserverScan() {
    try {
      setLoading(true);

      const res = await fetch(`${API}/observer/scan`, { method: 'POST' });
      const data = await res.json();

      await refreshAll();

      if (data.created_incidents && data.created_incidents.length > 0) {
        setSelectedId(data.created_incidents[0].id);
      }
    } catch (error) {
      console.error('Failed to run observer scan:', error);
    } finally {
      setLoading(false);
    }
  }

  async function approve(id) {
    try {
      setLoading(true);

      await fetch(`${API}/incidents/${id}/approve`, { method: 'POST' });

      await refreshAll();

      setSelectedId(id);
    } catch (error) {
      console.error('Failed to approve incident:', error);
    } finally {
      setLoading(false);
    }
  }

  async function refreshAll() {
    await loadIncidents();
    await loadMetrics();
    await loadLogs();
  }

  useEffect(() => {
    refreshAll();

    const timer = setInterval(() => {
      refreshAll();
    }, 3000);

    return () => clearInterval(timer);
  }, []);

  const selected = incidents.find((incident) => incident.id === selectedId) || incidents[0];

  const selectedServiceLogs = selected
    ? logs.find((item) => item.service === selected.service)
    : null;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">
            <Zap size={20} />
          </div>

          <div>
            <h1>Infra Swarm</h1>
            <p>Self-Healing Infrastructure Agents</p>
          </div>
        </div>

        <div className="actions">
          <button disabled={loading} onClick={runObserverScan}>
            Run Observer Scan
          </button>

          <button disabled={loading} onClick={() => inject('/simulate/memory-leak')}>
            Inject Memory Leak
          </button>

          <button disabled={loading} onClick={() => inject('/simulate/cpu-spike')}>
            Inject CPU Spike
          </button>

          <button className="ghost" disabled={loading} onClick={refreshAll}>
            <RefreshCw size={16} /> Refresh
          </button>
        </div>

        <h2>Incidents</h2>

        <div className="incident-list">
          {incidents.length === 0 && (
            <p className="empty">No incidents yet. Inject a test failure.</p>
          )}

          {incidents.map((incident) => (
            <button
              key={incident.id}
              className={`incident-item ${selected?.id === incident.id ? 'selected' : ''}`}
              onClick={() => setSelectedId(incident.id)}
            >
              <span>{incident.id}</span>
              <strong>{incident.title}</strong>
              <small className={statusClass(incident.status)}>{incident.status}</small>
            </button>
          ))}
        </div>
      </aside>

      <main className="main">
        <section className="metrics-section">
          <div className="section-header">
            <h2>Live Service Metrics</h2>
            <p>Simulated infrastructure health signals from backend services.</p>
          </div>

          <div className="metrics-grid">
            {metrics.map((metric) => (
              <div className="metric-card" key={metric.service}>
                <div className="metric-card-header">
                  <h3>{metric.service}</h3>

                  <span className={`metric-status ${metric.status}`}>
                    {metric.status}
                  </span>
                </div>

                <div className="metric-values">
                  <p>
                    CPU: <strong>{metric.cpu}%</strong>
                  </p>

                  <p>
                    Memory: <strong>{metric.memory}%</strong>
                  </p>

                  <p>
                    Latency: <strong>{metric.latency_ms}ms</strong>
                  </p>

                  <p>
                    Error Rate: <strong>{metric.error_rate}%</strong>
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {!selected ? (
          <div className="hero-card">
            <h2>No active incidents</h2>
            <p>Start by injecting a failure scenario from the left panel.</p>
          </div>
        ) : (
          <>
            <section className="top-card">
              <div>
                <p className="eyebrow">{selected.severity}</p>
                <h2>{selected.title}</h2>

                <p className="muted">
                  Affected: {(selected.affected_services ?? [selected.service]).join(', ')}
                </p>
              </div>

              <div className={`status-pill ${statusClass(selected.status)}`}>
                {selected.status}
              </div>
            </section>

            <section className="grid">
              <div className="card">
                <div className="card-title">
                  <Activity size={18} /> Signals
                </div>

                <div className="chips">
                  {(selected.signals ?? []).map((signal) => (
                    <span key={signal}>{signal}</span>
                  ))}
                </div>
              </div>

              <div className="card">
                <div className="card-title">
                  <Brain size={18} /> Diagnosis
                </div>

                {selected.diagnosis ? (
                  <>
                    <h3>{selected.diagnosis.root_cause}</h3>

                    <p>
                      Confidence:{' '}
                      {selected.diagnosis.confidence
                        ? `${(selected.diagnosis.confidence * 100).toFixed(0)}%`
                        : 'N/A'}
                    </p>

                    <ul>
                      {(selected.diagnosis.evidence ?? []).map((evidence) => (
                        <li key={evidence}>{evidence}</li>
                      ))}
                    </ul>
                  </>
                ) : (
                  <p className="muted">Waiting for diagnosis...</p>
                )}
              </div>

              <div className="card">
                <div className="card-title">
                  <ShieldCheck size={18} /> Safety Review
                </div>

                {selected.safety ? (
                  <>
                    <p>{selected.safety.decision}</p>
                    <p className="muted">Risk: {selected.safety.risk}</p>

                    {selected.status === 'AWAITING_APPROVAL' && (
                      <button disabled={loading} onClick={() => approve(selected.id)}>
                        Approve Remediation
                      </button>
                    )}
                  </>
                ) : (
                  <p className="muted">No safety decision yet.</p>
                )}
              </div>

              <div className="card">
                <div className="card-title">
                  <CheckCircle2 size={18} /> Remediation
                </div>

                {selected.remediation ? (
                  <>
                    <h3>{selected.remediation.action}</h3>
                    <p>{selected.remediation.reason}</p>
                    <code>{selected.remediation.command}</code>
                  </>
                ) : (
                  <p className="muted">No plan yet.</p>
                )}
              </div>
            </section>

            <section className="logs-panel card">
              <div className="card-title">
                <TerminalSquare size={18} /> Service Logs
              </div>

              <p className="muted">
                Recent simulated logs for {selected.service}.
              </p>

              <div className="logs-list">
                {(selectedServiceLogs?.logs ?? []).length === 0 && (
                  <p className="empty">No logs available for this service.</p>
                )}

                {(selectedServiceLogs?.logs ?? []).map((log, index) => (
                  <div className="log-row" key={`${log.timestamp}-${index}`}>
                    <span className="log-time">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>

                    <span className={`log-level ${logLevelClass(log.level)}`}>
                      {log.level}
                    </span>

                    <span className="log-message">{log.message}</span>
                  </div>
                ))}
              </div>
            </section>

            <section className="timeline card">
              <div className="card-title">Agent Timeline</div>

              {(selected.timeline ?? []).map((event, index) => (
                <div className="timeline-row" key={`${event.agent}-${index}`}>
                  <div className="dot"></div>

                  <div>
                    <strong>{event.agent}</strong>
                    <p>{event.message}</p>

                    {event.created_at && (
                      <small>{new Date(event.created_at).toLocaleString()}</small>
                    )}
                  </div>
                </div>
              ))}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);