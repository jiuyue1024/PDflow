import type { LucideIcon } from 'lucide-react'
import type { ReactNode } from 'react'

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: ReactNode
}

export default function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
      textAlign: 'center',
    }}>
      {Icon && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '56px',
          height: '56px',
          borderRadius: '16px',
          backgroundColor: 'var(--bg-hover)',
          marginBottom: '16px',
        }}>
          <Icon size={24} style={{ color: 'var(--text-muted)' }} strokeWidth={1.5} />
        </div>
      )}
      <p style={{
        fontSize: '14px',
        fontWeight: 600,
        color: 'var(--text-primary)',
        margin: 0,
        marginBottom: description ? '4px' : 0,
      }}>
        {title}
      </p>
      {description && (
        <p style={{
          fontSize: '13px',
          color: 'var(--text-muted)',
          margin: 0,
          marginBottom: action ? '16px' : 0,
          maxWidth: '280px',
        }}>
          {description}
        </p>
      )}
      {action}
    </div>
  )
}
