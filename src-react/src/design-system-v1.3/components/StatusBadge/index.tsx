import type { CSSProperties } from 'react'

type BadgeVariant = 'active' | 'beta' | 'experimental' | 'offline' | 'success' | 'warning' | 'error' | 'default'

interface StatusBadgeProps {
  label: string
  variant?: BadgeVariant
}

const variantStyles: Record<BadgeVariant, CSSProperties> = {
  active: { backgroundColor: 'var(--success-bg)', color: 'var(--success)' },
  beta: { backgroundColor: 'var(--primary-subtle)', color: 'var(--primary)' },
  experimental: { backgroundColor: 'var(--warning-bg)', color: 'var(--warning)' },
  offline: { backgroundColor: 'var(--bg-hover)', color: 'var(--text-muted)' },
  success: { backgroundColor: 'var(--success-bg)', color: 'var(--success)' },
  warning: { backgroundColor: 'var(--warning-bg)', color: 'var(--warning)' },
  error: { backgroundColor: 'var(--error-bg)', color: 'var(--error)' },
  default: { backgroundColor: 'var(--bg-hover)', color: 'var(--text-secondary)' },
}

export default function StatusBadge({ label, variant = 'default' }: StatusBadgeProps) {
  return (
    <span
      style={{
        ...variantStyles[variant],
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 10px',
        borderRadius: '9999px',
        fontSize: '11px',
        fontWeight: 600,
        lineHeight: '16px',
        whiteSpace: 'nowrap' as const,
      }}
    >
      {label}
    </span>
  )
}
