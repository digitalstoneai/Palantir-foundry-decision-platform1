import { useState } from 'react'

const ACTION_TYPES = ['reassign', 'escalate', 'schedule', 'notify', 'defer']

const STATUS_COLOR = {
  pending: 'var(--orange)',
  approved: 'var(--blue)',
  rejected: 'var(--red)',
  executed: 'var(--blue)',
}

export default function ActionApproval({ objects, actions, onPropose, onApprove }) {
  const [objectId, setObjectId] = useState(objects[0]?.id ?? '')
  const [actionType, setActionType] = useState(ACTION_TYPES[0])

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Governed Actions</h3>

      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <select
          value={objectId}
          onChange={(e) => setObjectId(e.target.value)}
          style={{ flex: 1, background: 'var(--surface-2)', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: 4, padding: 6 }}
        >
          {objects.map((o) => (
            <option key={o.id} value={o.id}>
              {o.name}
            </option>
          ))}
        </select>
        <select
          value={actionType}
          onChange={(e) => setActionType(e.target.value)}
          style={{ background: 'var(--surface-2)', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: 4, padding: 6 }}
        >
          {ACTION_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
        <button
          onClick={() => onPropose(objectId, actionType)}
          style={{ background: 'var(--surface-3)', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: 4, padding: '6px 12px', cursor: 'pointer' }}
        >
          Propose
        </button>
      </div>

      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {actions.map((a) => (
          <li key={a.action_id} className="panel" style={{ marginBottom: 8, padding: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span
                className="badge"
                style={{ background: `${STATUS_COLOR[a.status]}26`, color: STATUS_COLOR[a.status] }}
              >
                {a.status}
              </span>
            </div>
            <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '0 0 8px' }}>{a.ai_rationale}</p>
            {a.status === 'pending' && (
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  onClick={() => onApprove(a.action_id, true)}
                  style={{ background: 'var(--purple)', color: '#0d1117', border: 'none', borderRadius: 4, padding: '4px 10px', cursor: 'pointer', fontWeight: 600 }}
                >
                  Approve
                </button>
                <button
                  onClick={() => onApprove(a.action_id, false)}
                  style={{ background: 'var(--surface-3)', color: 'var(--text)', border: '1px solid var(--border)', borderRadius: 4, padding: '4px 10px', cursor: 'pointer' }}
                >
                  Reject
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
