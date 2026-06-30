import { useState, type ButtonHTMLAttributes, type CSSProperties } from 'react'

interface PrimaryButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Button label */
  label: string
  /** Size variant */
  size?: 'sm' | 'md'
  /** Show loading spinner */
  loading?: boolean
  /** Force disabled visual (greyed out) */
  disabled?: boolean
  /** Full-width button */
  block?: boolean
}

const sizeMap = {
  sm: { padding: '6px 16px', fontSize: '12px', height: '32px' },
  md: { padding: '10px 20px', fontSize: '13px', height: '36px' },
} as const

export default function PrimaryButton({ label, size = 'md', loading, disabled, block, style, children, ...rest }: PrimaryButtonProps) {
  const [hovered, setHovered] = useState(false)

  const bg = disabled
    ? 'var(--bg-hover)'
    : loading
      ? 'var(--btn-primary)'
      : hovered
        ? 'var(--btn-primary-hover)'
        : 'var(--btn-primary)'

  const color = disabled
    ? 'var(--text-muted)'
    : 'var(--btn-primary-text)'

  const cursor = disabled ? 'not-allowed' : loading ? 'wait' : 'pointer'

  const opacity = disabled ? 0.6 : 1

  const mergedStyle: CSSProperties = {
    ...sizeMap[size],
    backgroundColor: bg,
    color,
    borderRadius: 'var(--radius-lg, 8px)',
    border: 'none',
    fontWeight: 500,
    cursor,
    opacity,
    transition: 'background-color 0.15s ease, opacity 0.15s ease',
    display: block ? 'flex' : 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '6px',
    width: block ? '100%' : undefined,
    boxSizing: 'border-box' as const,
    ...style,
  }

  return (
    <button
      {...rest}
      disabled={disabled || loading}
      style={mergedStyle}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {loading && (
        <svg className="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
        </svg>
      )}
      {children}
      {label}
    </button>
  )
}
