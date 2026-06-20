const ROLES = [
  { id: 'operations_manager', label: 'Operations Manager' },
  { id: 'planner', label: 'Planner' },
  { id: 'maintenance_lead', label: 'Maintenance Lead' },
  { id: 'logistics_lead', label: 'Logistics Lead' },
]

export default function RoleSelector({ selectedRole, onSelect }) {
  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Role</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {ROLES.map((role) => (
          <button
            key={role.id}
            onClick={() => onSelect(role.id)}
            style={{
              textAlign: 'left',
              background: role.id === selectedRole ? 'var(--surface-3)' : 'var(--surface-2)',
              border: '1px solid var(--border)',
              borderRadius: 4,
              color: 'var(--text)',
              padding: '8px 10px',
              cursor: 'pointer',
            }}
          >
            {role.label}
          </button>
        ))}
      </div>
    </div>
  )
}
