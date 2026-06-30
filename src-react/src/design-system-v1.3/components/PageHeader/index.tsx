import type { ReactNode } from 'react'

interface PageHeaderProps {
  title: string
  subtitle?: string
  badge?: ReactNode
  actions?: ReactNode
}

export default function PageHeader({ title, subtitle, badge, actions }: PageHeaderProps) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'space-between',
      marginBottom: '24px',
      gap: '16px',
      flexWrap: 'wrap',
    }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: subtitle ? '4px' : 0 }}>
          <h1 style={{
            fontSize: '20px',
            fontWeight: 600,
            color: 'var(--text-primary)',
            margin: 0,
            lineHeight: '28px',
          }}>
            {title}
          </h1>
          {badge}
        </div>
        {subtitle && (
          <p style={{
            fontSize: '14px',
            color: 'var(--text-secondary)',
            margin: 0,
            lineHeight: '20px',
          }}>
            {subtitle}
          </p>
        )}
      </div>
      {actions && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
          {actions}
        </div>
      )}
    </div>
  )
}
