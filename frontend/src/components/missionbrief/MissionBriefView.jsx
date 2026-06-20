import { useEffect, useState } from 'react'
import { apiFetch } from '../../api/client.js'
import ActionApproval from './ActionApproval.jsx'
import BriefingPanel from './BriefingPanel.jsx'
import RoleSelector from './RoleSelector.jsx'

export default function MissionBriefView() {
  const [role, setRole] = useState(null)
  const [briefing, setBriefing] = useState(null)
  const [loading, setLoading] = useState(false)
  const [objects, setObjects] = useState([])
  const [actions, setActions] = useState([])

  useEffect(() => {
    apiFetch('/api/opsgraph/objects').then(setObjects)
    refreshActions()
  }, [])

  const refreshActions = () => {
    apiFetch('/api/brief/actions').then(setActions)
  }

  const selectRole = (selectedRole) => {
    setRole(selectedRole)
    setLoading(true)
    apiFetch('/api/brief/generate', {
      method: 'POST',
      body: JSON.stringify({ role: selectedRole }),
    })
      .then(setBriefing)
      .finally(() => setLoading(false))
  }

  const proposeAction = (objectId, actionType) => {
    apiFetch('/api/brief/action', {
      method: 'POST',
      body: JSON.stringify({ type: actionType, object_id: objectId, requested_by: role ?? 'operations_manager' }),
    }).then(refreshActions)
  }

  const approveAction = (actionId, approved) => {
    apiFetch(`/api/brief/action/${actionId}/approve`, {
      method: 'POST',
      body: JSON.stringify({ action_id: actionId, approved_by: role ?? 'operations_manager', approved }),
    }).then(refreshActions)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr 1fr', gap: 16 }}>
      <RoleSelector selectedRole={role} onSelect={selectRole} />
      <BriefingPanel briefing={briefing} loading={loading} />
      <ActionApproval objects={objects} actions={actions} onPropose={proposeAction} onApprove={approveAction} />
    </div>
  )
}
