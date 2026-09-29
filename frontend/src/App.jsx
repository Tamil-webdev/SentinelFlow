import { useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, AlertTriangle, Bot, CircleDot, ClipboardList, Database, Eye, Radar, ShieldAlert, ShieldCheck, Terminal, Zap } from 'lucide-react'
import { api } from './services/api'

const icons = { incidents: ShieldAlert, critical: AlertTriangle, blocked: ShieldCheck, active: Radar }
const demos = [
  ['bruteforce', 'Simulate Brute Force', ShieldAlert],
  ['port-scan', 'Simulate Port Scan', Radar],
  ['container-attack', 'Simulate Container Attack', Terminal],
  ['normal-traffic', 'Normal Traffic', Activity],
]
const time = (value) => value ? new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'medium' }) : 'Awaiting events'

function Severity({ level }) { return <span className={`severity ${level?.toLowerCase()}`}>{level}</span> }

function App() {
  const [data, setData] = useState({ incidents: [], events: [], agents: [], metrics: {}, ai: {} })
  const [selected, setSelected] = useState(null)
  const [view, setView] = useState('dashboard')
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState('')
  const [error, setError] = useState('')
  const [toast, setToast] = useState('')

  const refresh = useCallback(async () => {
    try {
      const [incidents, events, agents, metrics, ai] = await Promise.all([api.incidents(), api.events(), api.agents(), api.metrics(), api.aiStatus()])
      setData({ incidents, events, agents, metrics, ai })
      setError('')
    } catch (problem) { setError('Backend unavailable. Start the FastAPI service on port 8000.') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { refresh(); const timer = setInterval(refresh, 5000); return () => clearInterval(timer) }, [refresh])
  const trigger = async (type) => {
    setRunning(type)
    try { const result = await api.demo(type); await refresh(); if (result?.id) setSelected(result); setToast(`${type.replace('-', ' ')} pipeline completed`) }
    catch (problem) { setError(problem.message) }
    finally { setRunning(''); setTimeout(() => setToast(''), 3200) }
  }
  const totals = [
    ['incidents', 'Total incidents', data.metrics.incidents_created_total || 0, 'Last 24 hours'],
    ['critical', 'Critical incidents', data.metrics.critical_incidents || 0, 'Requires containment'],
    ['blocked', 'Blocked IPs', data.metrics.blocked_ips || 0, 'Simulation mode'],
    ['active', 'Active threats', data.metrics.active_threats || 0, 'Open incidents'],
  ]

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><ShieldCheck size={22} /></div><div><strong>SentinelFlow</strong></div></div>
      <nav><button className={view === 'dashboard' ? 'nav active' : 'nav'} onClick={() => setView('dashboard')}><Radar size={18}/>Dashboard</button><button className={view === 'agents' ? 'nav active' : 'nav'} onClick={() => setView('agents')}><Bot size={18}/>Agent monitoring</button></nav>
      <div className="mode"><CircleDot size={15} /><span>DEMO MODE</span><small>Responses simulated</small></div>
    </aside>
    <main>
      <header><div><p className="eyebrow">SECURITY OPERATIONS CENTER</p><h1>{view === 'agents' ? 'Agent monitoring' : selected ? 'Incident command center' : 'Threat overview'}</h1></div><div className="live"><span></span>Live data <small>refreshes every 5s</small></div></header>
      {error && <div className="notice error">{error}<button onClick={refresh}>Retry</button></div>}
      {toast && <div className="toast"><ShieldCheck size={17}/>{toast}</div>}
      {view === 'agents' ? <Agents agents={data.agents} /> : selected ? <IncidentDetail incident={data.incidents.find((item) => item.id === selected.id) || selected} onClose={() => setSelected(null)} /> : <>
        <section className="metrics">{totals.map(([key, label, value, detail]) => { const Icon = icons[key]; return <article className="metric" key={key}><div className={`metric-icon ${key}`}><Icon size={20}/></div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></article> })}</section>
        <section className="workspace">
          <div className="panel simulator"><div className="panel-heading"><div><p className="eyebrow">CONTROLLED EXERCISES</p><h2>Demo attack simulator</h2></div><Zap size={20}/></div><div className="demo-grid">{demos.map(([type, label, Icon]) => <button key={type} className="demo-button" onClick={() => trigger(type)} disabled={Boolean(running)}><Icon size={18}/><span>{running === type ? 'Processing pipeline...' : label}</span></button>)}</div><p className="sim-note">All actions use generated events and allowlisted simulated responses.</p></div>
          <div className="panel pipeline"><div className="panel-heading"><div><p className="eyebrow">ORCHESTRATION</p><h2>Agent pipeline</h2></div><Bot size={20}/></div>{data.agents.map((agent, index) => <div className="agent-line" key={agent.name}><span className="line-icon"><ShieldCheck size={14}/></span><div><strong>{agent.name}</strong><small>{agent.last_decision}</small></div><span className="ready">READY</span>{index < data.agents.length - 1 && <i/>}</div>)}</div>
        </section>
        <section className="panel ai-panel"><div className="panel-heading"><div><p className="eyebrow">AI REASONING LAYER</p><h2>Gemini provider status</h2></div><Bot size={20}/></div><div className="ai-grid"><div><span>Mode</span><strong>{data.ai.mode || 'unavailable'}</strong></div><div><span>Model</span><strong>{data.ai.model || 'Not configured'}</strong></div><div><span>Healthy keys</span><strong>{data.ai.healthy || 0} / {data.ai.total_keys || 0}</strong></div><div><span>Requests</span><strong>{data.ai.requests || 0}</strong></div><div><span>Successful</span><strong>{data.ai.successes || 0}</strong></div><div><span>Failed</span><strong>{data.ai.failures || 0}</strong></div></div><p className="sim-note">Key identifiers and credentials remain backend-only. Multiple keys support reliability, not quota bypass.</p></section>
        <section className="panel table-panel"><div className="panel-heading"><div><p className="eyebrow">DETECTIONS</p><h2>Recent incidents</h2></div><ClipboardList size={20}/></div><IncidentTable incidents={data.incidents} onOpen={setSelected} loading={loading}/></section>
        <section className="panel feed"><div className="panel-heading"><div><p className="eyebrow">TELEMETRY</p><h2>Live event feed</h2></div><Database size={20}/></div>{data.events.slice(0, 6).map((event) => <div className="event" key={event.id}><span className="event-dot"></span><div><strong>{event.event_type.replaceAll('_', ' ')}</strong><p>{event.raw_message}</p></div><time>{time(event.timestamp)}</time></div>)}{!data.events.length && <Empty label="No events collected yet. Run a demo attack to populate the stream."/>}</section>
      </>}
    </main>
  </div>
}

function IncidentTable({ incidents, onOpen, loading }) { if (loading) return <div className="loading">Loading security telemetry...</div>; if (!incidents.length) return <Empty label="No incidents yet. Use the simulator to exercise the complete pipeline."/>; return <div className="table-wrap"><table><thead><tr><th>Incident</th><th>Threat</th><th>Source</th><th>Risk</th><th>Response</th><th></th></tr></thead><tbody>{incidents.slice(0, 10).map((incident) => <tr key={incident.id}><td><strong>{incident.id}</strong><small>{time(incident.created_at)}</small></td><td>{incident.threat_type.replaceAll('_', ' ')}</td><td className="mono">{incident.source_ip}</td><td><Severity level={incident.risk.level}/><small>{incident.risk.score}/100</small></td><td>{incident.response?.action.replaceAll('_', ' ') || 'MONITOR'}</td><td><button className="icon-button" title="Open incident" onClick={() => onOpen(incident)}><Eye size={17}/></button></td></tr>)}</tbody></table></div> }
function Empty({ label }) { return <div className="empty"><Radar size={24}/><p>{label}</p></div> }
function Agents({ agents }) { return <section className="panel agent-page"><div className="panel-heading"><div><p className="eyebrow">SIX SPECIALIZED AGENTS</p><h2>Pipeline health and recent decisions</h2></div><Bot size={20}/></div><div className="agent-cards">{agents.map((agent) => <article key={agent.name}><div><span className="agent-status"></span><strong>{agent.name}</strong><small>{agent.last_decision}</small></div><dl><div><dt>Status</dt><dd>READY</dd></div><div><dt>Runs</dt><dd>{agent.processed}</dd></div><div><dt>Average</dt><dd>{agent.average_duration_ms}ms</dd></div><div><dt>Last execution</dt><dd>{time(agent.last_execution)}</dd></div></dl></article>)}</div></section> }
function IncidentDetail({ incident, onClose }) { const stages = [['Log collection', 'Security events normalized'], ['Threat detection', `${incident.threat_type.replaceAll('_', ' ')} via ${incident.detection_method}`], ['Threat hunting', `${incident.timeline?.length || 0} related historical events`], ['Risk assessment', `${incident.risk.level} ${incident.risk.score}/100`], ['Response', incident.response?.action.replaceAll('_', ' ') || 'MONITOR'], ['Report generation', 'Structured report generated']]; return <><button className="back" onClick={onClose}>← Back to dashboard</button><section className="incident-hero"><div><p className="eyebrow">{incident.id}</p><h2>{incident.threat_type.replaceAll('_', ' ')}</h2><p>{incident.source_ip} targeting {incident.target}</p></div><div><Severity level={incident.risk.level}/><strong className="score">{incident.risk.score}<small>/100</small></strong></div></section><section className="detail-grid"><div className="panel"><div className="panel-heading"><h2>Decision pipeline</h2><Bot size={20}/></div><div className="stage-list">{stages.map(([title, note]) => <div className="stage" key={title}><span><ShieldCheck size={17}/></span><div><strong>{title}</strong><small>{note}</small></div></div>)}</div></div><div className="panel"><div className="panel-heading"><h2>Why this risk level?</h2><AlertTriangle size={20}/></div><ul className="factors">{incident.risk.factors.map((factor) => <li key={factor.factor}><ShieldCheck size={16}/><span>{factor.factor}</span><b>+{factor.weight}</b></li>)}</ul></div></section><section className="detail-grid"><div className="panel"><div className="panel-heading"><h2>Evidence & hunting</h2><Radar size={20}/></div><ul className="evidence">{[...incident.detection_evidence, ...incident.hunting_evidence].map((item, index) => <li key={index}>{item}</li>)}</ul></div><div className="panel"><div className="panel-heading"><h2>Response record</h2><ShieldCheck size={20}/></div><div className="response"><strong>{incident.response?.action.replaceAll('_', ' ')}</strong><span>{incident.response?.status} in {incident.response?.mode} mode</span><p>{incident.response?.reason}</p></div></div></section><section className="panel"><div className="panel-heading"><h2>Incident timeline</h2><Activity size={20}/></div>{incident.timeline?.slice(-12).map((event) => <div className="event" key={event.id}><span className="event-dot"></span><div><strong>{event.event_type.replaceAll('_', ' ')}</strong><p>{event.raw_message}</p></div><time>{time(event.timestamp)}</time></div>)}</section></> }

export default App
