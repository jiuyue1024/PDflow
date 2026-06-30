import { useState, useMemo } from 'react'
import {
  CreditCard,
  FileText,
  Receipt,
  BarChart3,
  Search,
  type LucideIcon,
} from 'lucide-react'
import CategoryTabs from '@/components/workflow/CategoryTabs'
import TemplateCard from '@/components/cards/TemplateCard'
import PageHeader from '../../design-system-v1.3/components/PageHeader'
import EmptyState from '../../design-system-v1.3/components/EmptyState'

interface Template {
  id: string
  name: string
  description: string
  icon: LucideIcon
  category: string
  tags: string[]
}

const templates: Template[] = [
  {
    id: 'bc-modern',
    name: 'Modern Business Card',
    description: 'Clean, professional layout with contact info and logo placement',
    icon: CreditCard,
    category: 'Business Cards',
    tags: ['Popular'],
  },
  {
    id: 'bc-minimal',
    name: 'Minimal Business Card',
    description: 'Ultra-clean design with essential information only',
    icon: CreditCard,
    category: 'Business Cards',
    tags: ['New'],
  },
  {
    id: 'bc-corporate',
    name: 'Corporate Business Card',
    description: 'Traditional corporate style with multi-role layout',
    icon: CreditCard,
    category: 'Business Cards',
    tags: [],
  },
  {
    id: 'ct-service',
    name: 'Service Agreement',
    description: 'Standard service contract with signature blocks',
    icon: FileText,
    category: 'Contracts',
    tags: ['Legal'],
  },
  {
    id: 'ct-nda',
    name: 'NDA Template',
    description: 'Non-disclosure agreement for business partnerships',
    icon: FileText,
    category: 'Contracts',
    tags: ['Legal'],
  },
  {
    id: 'ct-lease',
    name: 'Lease Agreement',
    description: 'Property lease contract with terms and conditions',
    icon: FileText,
    category: 'Contracts',
    tags: ['Legal'],
  },
  {
    id: 'inv-standard',
    name: 'Standard Invoice',
    description: 'Professional invoice with itemized billing and totals',
    icon: Receipt,
    category: 'Invoices & Receipts',
    tags: ['Popular'],
  },
  {
    id: 'inv-receipt',
    name: 'Payment Receipt',
    description: 'Simple payment confirmation receipt template',
    icon: Receipt,
    category: 'Invoices & Receipts',
    tags: [],
  },
  {
    id: 'rpt-quarterly',
    name: 'Quarterly Report',
    description: 'Executive quarterly summary with charts and KPIs',
    icon: BarChart3,
    category: 'Analysis Reports',
    tags: ['Popular'],
  },
  {
    id: 'rpt-annual',
    name: 'Annual Analysis',
    description: 'Comprehensive annual report with data visualization',
    icon: BarChart3,
    category: 'Analysis Reports',
    tags: ['New'],
  },
  {
    id: 'rpt-financial',
    name: 'Financial Summary',
    description: 'Financial performance summary with key metrics',
    icon: BarChart3,
    category: 'Analysis Reports',
    tags: [],
  },
]

const categories = ['All', 'Business Cards', 'Contracts', 'Invoices & Receipts', 'Analysis Reports']

interface TemplatesPageProps {
  initialCategory?: string
}

export default function TemplatesPage({ initialCategory = 'All' }: TemplatesPageProps) {
  const [activeCategory, setActiveCategory] = useState(initialCategory)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredTemplates = useMemo(() => {
    let result = templates

    if (activeCategory !== 'All') {
      result = result.filter((t) => t.category === activeCategory)
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      result = result.filter(
        (t) =>
          t.name.toLowerCase().includes(query) ||
          t.description.toLowerCase().includes(query)
      )
    }

    return result
  }, [activeCategory, searchQuery])

  return (
    <div className="mx-auto max-w-5xl px-8 py-6">
      {/* Header Section */}
      <PageHeader
        title="Templates"
        subtitle="Choose a template to start your document workflow"
        actions={
          <div className="relative w-72">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search templates..."
              className="h-10 w-full rounded-lg border-none pl-10 pr-4 text-sm outline-none focus:ring-2"
              style={{ backgroundColor: 'var(--bg-input-placeholder)', color: 'var(--text-primary)', '--tw-ring-color': 'var(--primary-subtle)' } as React.CSSProperties}
            />
          </div>
        }
      />

      {/* Category Tabs */}
      <div className="mb-6">
        <CategoryTabs
          categories={categories}
          activeCategory={activeCategory}
          onCategoryChange={setActiveCategory}
        />
      </div>

      {/* Template Grid */}
      {filteredTemplates.length > 0 ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filteredTemplates.map((template) => (
            <TemplateCard
              key={template.id}
              name={template.name}
              description={template.description}
              icon={template.icon}
              tags={template.tags}
              category={template.category}
              onUse={() => console.log('Use:', template.id)}
              onPreview={() => console.log('Preview:', template.id)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FileText}
          title="No templates found"
          description="Try a different category or search term"
        />
      )}

      {/* Footer count */}
      <div className="mt-6 text-center text-xs" style={{ color: 'var(--text-muted)' }}>
        {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''} available
      </div>
    </div>
  )
}
