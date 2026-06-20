import { useState } from 'react'
import OpsGraphView from '../components/opsgraph/OpsGraphView.jsx'

const TABS = [
  { id: 'opsgraph', label: 'OpsGraph AI' },
  { id: 'decision', label: 'DecisionRoom AI' },
  { id: 'brief', label: 'MissionBrief AI' },
]

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('opsgraph')

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <h1 style={{ fontSize: 20, marginBottom: 16 }}>Palantir Foundry Operational Decision Platform</h1>
      <div style={{ display: 'flex', gap: 8, marginBottom: 20, borderBottom: '1px solid var(--border)' }}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              background: 'none',
              border: 'none',
              color: activeTab === tab.id ? 'var(--text)' : 'var(--text-muted)',
              borderBottom: activeTab === tab.id ? '2px solid var(--purple)' : '2px solid transparent',
              padding: '10px 4px',
              marginRight: 16,
              cursor: 'pointer',
              fontSize: 14,
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'opsgraph' && <OpsGraphView />}
      {activeTab === 'decision' && (
        <p style={{ color: 'var(--text-muted)' }}>DecisionRoom AI — coming in Phase 3.</p>
      )}
      {activeTab === 'brief' && (
        <p style={{ color: 'var(--text-muted)' }}>MissionBrief AI — coming in Phase 4.</p>
      )}
    </div>
  )
}
