const LEVELS = {
  low: { label: 'Low risk', icon: '✓' },
  medium: { label: 'Medium risk', icon: '!' },
  high: { label: 'High risk', icon: '▲' },
}

// The colour never carries the meaning on its own: every badge also has an
// icon and a written label.
export default function RiskBadge({ level }) {
  const { label, icon } = LEVELS[level]

  return (
    <span className={`risk-badge risk-${level}`}>
      <span className="risk-icon" aria-hidden="true">
        {icon}
      </span>
      {label}
    </span>
  )
}
