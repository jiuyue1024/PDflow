import { useState, type CSSProperties } from 'react'
import type { LucideIcon } from 'lucide-react'

interface TemplateCardProps {
  name: string
  description: string
  icon: LucideIcon
  tags: string[]
  category: string
  onUse: () => void
  onPreview: () => void
}

function getTagStyles(tag: string): CSSProperties {
  switch (tag) {
    case 'Popular':
      return { backgroundColor: 'var(--primary-subtle)', color: 'var(--primary)' }
    case 'New':
      return { backgroundColor: 'var(--success-bg)', color: 'var(--success)' }
    default:
      return { backgroundColor: 'var(--bg-hover)', color: 'var(--text-secondary)' }
  }
}

/** Category → icon color mapping */
const categoryIconColors: Record<string, string> = {
  'Business Cards': '#4F8CFF',
  'Contracts': '#22C55E',
  'Invoices & Receipts': '#F59E0B',
  'Analysis Reports': '#A855F7',
}

/** Icon thumbnail — large centered icon on uniform tinted background */
function IconPreview({ icon: Icon, category }: { icon: LucideIcon; category: string }) {
  const iconColor = categoryIconColors[category] || '#6B7280'

  return (
    <div className="flex w-full items-center justify-center aspect-[4/3]" style={{ backgroundColor: 'var(--bg-input-placeholder)' }}>
      <div
        className="flex h-20 w-20 items-center justify-center rounded-2xl shadow-sm"
        style={{ backgroundColor: 'var(--icon-preview-bg)', border: '1px solid var(--border)' }}
      >
        <Icon size={36} strokeWidth={1.5} style={{ color: iconColor }} />
      </div>
    </div>
  )
}

export default function TemplateCard({
  name,
  description,
  icon,
  tags,
  category,
  onUse,
  onPreview,
}: TemplateCardProps) {
  const [cardHovered, setCardHovered] = useState(false)
  const [btnHovered, setBtnHovered] = useState(false)
  const [previewHovered, setPreviewHovered] = useState(false)

  return (
    <div
      className="
        group
        rounded-xl
        border
        overflow-hidden
        transition-all duration-[180ms] ease-out
        hover:-translate-y-0.5
      "
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: cardHovered ? 'color-mix(in srgb, var(--primary) 40%, transparent)' : 'var(--border)',
        boxShadow: cardHovered ? '0 4px 16px rgba(0,0,0,0.08)' : '0 2px 10px rgba(0,0,0,0.05)',
      }}
      onMouseEnter={() => setCardHovered(true)}
      onMouseLeave={() => setCardHovered(false)}
    >
      {/* Icon thumbnail */}
      <IconPreview icon={icon} category={category} />

      {/* Title */}
      <div className="px-5 pt-4">
        <h3 className="text-base font-semibold leading-snug" style={{ color: 'var(--text-primary)' }}>
          {name}
        </h3>
      </div>

      {/* Description */}
      <p className="px-5 mt-1 text-[13px] truncate" style={{ color: 'var(--text-muted)' }}>
        {description}
      </p>

      {/* Tag badges */}
      {tags.length > 0 && (
        <div className="px-5 pt-3 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-block rounded-full px-2.5 py-0.5 text-[11px] font-medium"
              style={getTagStyles(tag)}
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Action area */}
      <div className="px-5 py-4 pt-3 flex justify-between items-center">
        <button
          type="button"
          onClick={onUse}
          className="rounded-lg px-4 py-2 text-[13px] font-medium transition-colors duration-150 border-none cursor-pointer"
          style={{ backgroundColor: btnHovered ? 'var(--btn-primary-hover)' : 'var(--btn-primary)', color: 'var(--btn-primary-text)' }}
          onMouseEnter={() => setBtnHovered(true)}
          onMouseLeave={() => setBtnHovered(false)}
        >
          Use Template
        </button>
        <button
          type="button"
          onClick={onPreview}
          className="text-[13px] bg-transparent border-none cursor-pointer transition-colors duration-150"
          style={{ color: previewHovered ? 'var(--primary-text)' : 'var(--text-secondary)' }}
          onMouseEnter={() => setPreviewHovered(true)}
          onMouseLeave={() => setPreviewHovered(false)}
        >
          Preview
        </button>
      </div>
    </div>
  )
}
