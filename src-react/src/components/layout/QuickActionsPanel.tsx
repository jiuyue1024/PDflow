import {
  Combine,
  Scissors,
  Minimize2,
  Droplets,
  CreditCard,
  Receipt,
  BarChart3,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface QuickAction {
  id: string
  label: string
  icon: LucideIcon
  color: string
}

const recentTools: QuickAction[] = [
  { id: 'merge', label: 'Merge', icon: Combine, color: '#4F8CFF' },
  { id: 'split', label: 'Split', icon: Scissors, color: '#22C55E' },
  { id: 'compress', label: 'Compress', icon: Minimize2, color: '#F59E0B' },
  { id: 'watermark', label: 'Watermark', icon: Droplets, color: '#A855F7' },
]

interface QuickActionsPanelProps {
  onActionClick: (id: string) => void
  currentPage?: string
}

export default function QuickActionsPanel({
  onActionClick,
  currentPage,
}: QuickActionsPanelProps) {
  return (
    <aside
      className="flex h-full w-[200px] flex-shrink-0 flex-col border-l"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      {/* Header */}
      <div className="px-4 pt-5 pb-3">
        <h2 className="text-[13px] font-semibold" style={{ color: 'var(--text-primary)' }}>
          Quick Actions
        </h2>
      </div>

      {/* Recent Tools */}
      <div className="px-4">
        <p
          className="mb-2 text-[10px] font-semibold uppercase tracking-wider"
          style={{ color: 'var(--text-secondary)' }}
        >
          Recent Tools
        </p>
        <div className="flex flex-col gap-0.5">
          {recentTools.map((tool) => {
            const Icon = tool.icon
            const isActive = currentPage === tool.id
            return (
              <button
                key={tool.id}
                onClick={() => onActionClick(tool.id)}
                className={`
                  flex w-full cursor-pointer items-start gap-2.5 rounded-md px-2.5 py-2
                  transition-colors duration-150
                  ${isActive ? 'shadow-sm' : ''}
                `}
                style={{ backgroundColor: isActive ? 'var(--bg-card)' : undefined }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'var(--bg-app)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.backgroundColor = 'var(--bg-app)'
                  }
                }}
              >
                <Icon size={15} strokeWidth={1.8} style={{ color: tool.color }} className="mt-0.5" />
                <span className="text-left text-[12.5px]" style={{ color: 'var(--text-primary)' }}>
                  {tool.label}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Separator */}
      <div className="mx-4 my-4 border-t" style={{ borderColor: 'var(--border)' }} />

      {/* Recent Templates */}
      <div className="px-4">
        <p
          className="mb-2 text-[10px] font-semibold uppercase tracking-wider"
          style={{ color: 'var(--text-secondary)' }}
        >
          Recent Templates
        </p>
        <div className="flex flex-col gap-0.5">
          {[
            { id: 'bc-modern', label: 'Business Card', icon: CreditCard, color: '#4F8CFF' },
            { id: 'inv-standard', label: 'Standard Invoice', icon: Receipt, color: '#F59E0B' },
            { id: 'rpt-quarterly', label: 'Quarterly Report', icon: BarChart3, color: '#A855F7' },
          ].map((tpl) => {
            const Icon = tpl.icon
            return (
              <button
                key={tpl.id}
                onClick={() => onActionClick(tpl.id)}
                className="
                  flex w-full cursor-pointer items-start gap-2.5 rounded-md px-2.5 py-2
                  transition-colors duration-150
                "
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--bg-app)'
                }}
              >
                <Icon size={15} strokeWidth={1.8} style={{ color: tpl.color }} className="mt-0.5" />
                <span className="text-left text-[12.5px]" style={{ color: 'var(--text-primary)' }}>
                  {tpl.label}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    </aside>
  )
}
