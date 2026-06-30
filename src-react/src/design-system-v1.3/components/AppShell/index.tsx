import type { ReactNode } from 'react'

export interface NavItem {
  id: string
  label: string
  section?: string
}

interface AppShellProps {
  /** Left sidebar content */
  sidebar: ReactNode
  /** Top header content */
  header: ReactNode
  /** Main content area */
  children: ReactNode
  /** Right quick actions panel (optional) */
  quickActions?: ReactNode
  /** Show right panel */
  showQuickActions?: boolean
}

export default function AppShell({
  sidebar,
  header,
  children,
  quickActions,
  showQuickActions = true,
}: AppShellProps) {
  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      width: '100vw',
      overflow: 'hidden',
      backgroundColor: 'var(--bg-app)',
    }}>
      {/* Sidebar */}
      {sidebar}

      {/* Main area: header + content */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        flex: 1,
        overflow: 'hidden',
      }}>
        {header}

        {/* Content + Quick Actions */}
        <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          {/* Main content */}
          <main style={{
            flex: 1,
            overflowY: 'auto',
            padding: '0',
          }}>
            {children}
          </main>

          {/* Right Quick Actions */}
          {showQuickActions && quickActions && (
            quickActions
          )}
        </div>
      </div>
    </div>
  )
}
