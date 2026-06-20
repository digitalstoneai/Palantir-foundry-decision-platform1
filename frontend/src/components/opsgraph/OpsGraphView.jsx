import { useEffect, useState } from 'react'
import { apiFetch } from '../../api/client.js'
import DependencyGraph from './DependencyGraph.jsx'
import ImpactSummary from './ImpactSummary.jsx'
import ObjectPanel from './ObjectPanel.jsx'

export default function OpsGraphView() {
  const [objects, setObjects] = useState([])
  const [links, setLinks] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [impactResult, setImpactResult] = useState(null)

  useEffect(() => {
    apiFetch('/api/opsgraph/objects').then(setObjects)
    apiFetch('/api/opsgraph/links').then(setLinks)
  }, [])

  const handleSelect = (id) => {
    setSelectedId(id)
    setImpactResult(null)
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr 320px', gap: 16 }}>
      <ObjectPanel objects={objects} selectedId={selectedId} onSelect={handleSelect} />
      <DependencyGraph
        objects={objects}
        links={links}
        selectedId={selectedId}
        affectedIds={impactResult?.affected_objects ?? []}
      />
      <ImpactSummary objectId={selectedId} onResult={setImpactResult} />
    </div>
  )
}
