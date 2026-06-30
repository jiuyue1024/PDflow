import { useState, type CSSProperties } from 'react'
import type { LucideIcon } from 'lucide-react'
import { ChevronRight } from 'lucide-react'

interface ActionCardProps {
  icon: LucideIcon
  title: string
  description?: string
  /** Icon color (theme-independent accent) */
  iconColor?: string
  /** Click handler */
  onClick?: () => void
  /** Show right arrow */
  showArrow?: boolean
  /** Active/selected state */
  active?: boolean
  /** Badge element in top-right corner */
  badge?: React.ReactNode
  /** Custom content area below the header (e.g. template preview) */
  children?: React.ReactNode
  /** Size variant */
  variant?: 'default' | 'compact'
}

export default function ActionCard({
  icon: Icon,
  title,
  description,
  iconColor = 'var(--primary)',
  onClick,
  showArrow = false,
  active = false,
  badge,
  children,
  variant = 'default',
}: ActionCardProps) {
  const [hovered, setHovered] = useState(false)

  const cardStyle: CSSProperties = {
    backgroundColor: 'var(--bg-card)',
    borderColor: active
      ? 'var(--border-active)'
      : hovered
        ? 'color-mix(in srgb, var(--primary) 40%, transparent)'
        : 'var(--border)',
    borderRadius: '12px',
    borderWidth: '1px',
    borderStyle: 'solid',
    boxShadow: hovered
      ? '0 4px 16px rgba(0,0,0,0.08)'
      : '0 2px 10px rgba(0,0,0,0.05)',
    cursor: onClick ? 'pointer' : 'default',
    transition: 'border-color 0.18s ease-out, box-shadow 0.18s ease-out, transform 0.18s ease-out',
    transform: hovered && onClick ? 'translateY(-2px)' : undefined,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
  }

  const isCompact = variant === 'compact'

  return (
    <div
      style={cardStyle}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Badge area */}
      {badge && (
        <div style={{ position: 'absolute', top: '12px', right: '12px', zIndex: 1 }}>
          {badge}
        </div>
      )}

      {/* Main content or just header */}
      {children ? (
        // Has custom children (e.g. template preview area)
        <>
          {children}
          {/* Header below children */}
          <div style={{ padding: isCompact ? '12px 16px' : '16px 20px', paddingTop: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: isCompact ? '32px' : '40px',
                height: isCompact ? '32px' : '40px',
                borderRadius: '10px',
                backgroundColor: 'var(--bg-hover)',
                flexShrink: 0,
              }}>
                <Icon size={isCompact ? 16 : 20} strokeWidth={1.5} style={{ color: iconColor }} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <h3 style={{
                  fontSize: isCompact ? '13px' : '14px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  margin: 0,
                  lineHeight: '20px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {title}
                </h3>
                {description && (
                  <p style={{
                    fontSize: '12px',
                    color: 'var(--text-muted)',
                    margin: '2px 0 0 0',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    {description}
                  </p>
                )}
              </div>
              {showArrow && (
                <ChevronRight size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
              )}
            </div>
          </div>
        </>
      ) : (
        // Simple card — just header
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: isCompact ? '10px 14px' : '14px 18px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: isCompact ? '32px' : '40px',
            height: isCompact ? '32px' : '40px',
            borderRadius: '10px',
            backgroundColor: 'var(--bg-hover)',
            flexShrink: 0,
          }}>
            <Icon size={isCompact ? 16 : 20} strokeWidth={1.5} style={{ color: iconColor }} />
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <h3 style={{
              fontSize: isCompact ? '13px' : '14px',
              fontWeight: 600,
              color: 'var(--text-primary)',
              margin: 0,
              lineHeight: '20px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {title}
            </h3>
            {description && (
              <p style={{
                fontSize: '12px',
                color: 'var(--text-muted)',
                margin: '2px 0 0 0',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}>
                {description}
              </p>
            )}
          </div>
          {showArrow && (
            <ChevronRight size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
          )}
        </div>
      )}
    </div>
  )
}
