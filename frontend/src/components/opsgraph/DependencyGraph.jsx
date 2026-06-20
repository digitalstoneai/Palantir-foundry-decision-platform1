import * as d3 from 'd3'
import { useEffect, useRef } from 'react'

const WIDTH = 480
const HEIGHT = 420

export default function DependencyGraph({ objects, links, selectedId, affectedIds = [] }) {
  const svgRef = useRef(null)

  useEffect(() => {
    if (!objects.length) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    const nodes = objects.map((o) => ({ ...o }))
    const nodeById = new Map(nodes.map((n) => [n.id, n]))
    const edges = links
      .filter((l) => nodeById.has(l.source_id) && nodeById.has(l.target_id))
      .map((l) => ({ source: l.source_id, target: l.target_id, type: l.type }))

    const simulation = d3
      .forceSimulation(nodes)
      .force('link', d3.forceLink(edges).id((d) => d.id).distance(90))
      .force('charge', d3.forceManyBody().strength(-220))
      .force('center', d3.forceCenter(WIDTH / 2, HEIGHT / 2))

    const link = svg
      .append('g')
      .selectAll('line')
      .data(edges)
      .join('line')
      .attr('stroke', 'var(--border)')
      .attr('stroke-width', 1.5)

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(nodes)
      .join('circle')
      .attr('r', 14)
      .attr('fill', (d) => {
        if (d.id === selectedId) return 'var(--purple)'
        if (affectedIds.includes(d.id)) return 'var(--orange)'
        return 'var(--blue)'
      })
      .attr('stroke', 'var(--surface)')
      .attr('stroke-width', 2)

    const label = svg
      .append('g')
      .selectAll('text')
      .data(nodes)
      .join('text')
      .text((d) => d.name)
      .attr('font-size', 10)
      .attr('fill', 'var(--text-muted)')
      .attr('text-anchor', 'middle')
      .attr('dy', 26)

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y)
      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y)
      label.attr('x', (d) => d.x).attr('y', (d) => d.y)
    })

    return () => simulation.stop()
  }, [objects, links, selectedId, affectedIds])

  return (
    <div className="panel">
      <h3 style={{ marginTop: 0 }}>Dependency Graph</h3>
      <svg ref={svgRef} width={WIDTH} height={HEIGHT} />
    </div>
  )
}
