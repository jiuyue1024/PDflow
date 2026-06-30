import type { ReactNode } from 'react'

interface SettingsRowProps {
  /** Row label (e.g. "Language") */
  label: string
  /** Optional description below label */
  description?: string
  /** Right-side control (toggle, dropdown, button) */
  children: ReactNode
}

export default function SettingsRow({ label, description, children }: SettingsRowProps) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 0',
      gap: '16px',
    }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{
          fontSize: '13px',
          fontWeight: 500,
          color: 'var(--text-primary)',
          margin: 0,
        }}>
          {label}
        </p>
        {description && (
          <p style={{
            fontSize: '12px',
            color: 'var(--text-muted)',
            margin: '4px 0 0 0',
          }}>
            {description}
          </p>
        )}
      </div>
      <div style={{ flexShrink: 0 }}>
        {children}
      </div>
    </div>
  )
}
