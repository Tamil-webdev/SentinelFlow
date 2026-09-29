const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options) {
  const response = await fetch(`${API}${path}`, options)
  if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail || 'Request failed')
  return response.json()
}

export const api = {
  health: () => request('/api/health'),
  incidents: () => request('/api/incidents'),
  events: () => request('/api/events'),
  agents: () => request('/api/agents/status'),
  aiStatus: () => request('/api/ai/status'),
  metrics: () => request('/api/metrics'),
  demo: (type) => request(`/api/demo/${type}`, { method: 'POST' }),
}
