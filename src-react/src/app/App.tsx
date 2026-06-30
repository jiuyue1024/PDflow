import { useState, useEffect } from 'react'
import Sidebar from '@/components/layout/Sidebar'
import Header from '@/components/layout/Header'
import QuickActionsPanel from '@/components/layout/QuickActionsPanel'
import HomePage from '@/pages/Home'
import TemplatesPage from '@/pages/Templates'
import ConvertPage from '@/pages/Convert'
import WatermarkPage from '@/pages/Watermark'
import ToolsCenter from '@/pages/ToolsCenter'
import SettingsPage from '@/pages/Settings'
import BatchConvertPage from '@/pages/BatchConvert'

// Map sidebar item id → initial category for TemplatesPage
const templateCategoryMap: Record<string, string> = {
  templates: 'All',
  'business-cards': 'Business Cards',
  contracts: 'Contracts',
  invoices: 'Invoices & Receipts',
  reports: 'Analysis Reports',
}

// Map sidebar item id → initial convert mode
const convertModeMap: Record<string, 'pdf-excel' | 'pdf-word' | 'pdf-ppt'> = {
  'pdf-excel': 'pdf-excel',
  'pdf-word': 'pdf-word',
  'pdf-ppt': 'pdf-ppt',
}

const convertItems = new Set(Object.keys(convertModeMap))

// TOOLS items → all route to ToolsCenter
const toolsCenterIds = new Set(['merge', 'split', 'optimize'])

// Dedicated standalone pages
const standalonePages = new Set(['watermark'])

// Map quick action ids to sidebar ids for navigation
const quickActionToNav: Record<string, string> = {
  merge: 'merge',
  split: 'split',
  compress: 'optimize',
  watermark: 'watermark',
  'bc-modern': 'business-cards',
  'inv-standard': 'invoices',
  'rpt-quarterly': 'reports',
}

// Pages that hide the right Quick Actions panel
const noQuickActionsIds = new Set(['batch-convert'])

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex h-full items-center justify-center">
      <p style={{ color: 'var(--text-muted)' }}>{title} — Coming soon</p>
    </div>
  )
}

export default function App() {
  const [activeItem, setActiveItem] = useState('dashboard')
  const [developerMode, setDeveloperMode] = useState(false)
  const [theme, setTheme] = useState<'light' | 'dark'>('light')

  // Sync data-theme attribute to <html>
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const isTemplatePage = activeItem in templateCategoryMap
  const isConvertPage = convertItems.has(activeItem)
  const isToolsCenter = toolsCenterIds.has(activeItem)

  const initialCategory = isTemplatePage
    ? templateCategoryMap[activeItem]
    : undefined

  const initialConvertMode = isConvertPage
    ? convertModeMap[activeItem]
    : undefined

  const handleQuickAction = (id: string) => {
    const navId = quickActionToNav[id]
    if (navId) {
      setActiveItem(navId)
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ backgroundColor: 'var(--bg-app)' }}>
      <Sidebar activeItem={activeItem} onItemClick={setActiveItem} developerMode={developerMode} onDeveloperModeChange={setDeveloperMode} />

      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <div className="flex flex-1 overflow-hidden">
          {/* Main content */}
          <main className="flex-1 overflow-y-auto">
            {activeItem === 'dashboard' && <HomePage />}
            {activeItem === 'settings' && <SettingsPage developerMode={developerMode} onDeveloperModeChange={setDeveloperMode} theme={theme} onThemeChange={setTheme} />}
            {activeItem === 'batch-convert' && <BatchConvertPage />}
            {isTemplatePage && (
              <TemplatesPage key={activeItem} initialCategory={initialCategory} />
            )}
            {isConvertPage && (
              <ConvertPage key={activeItem} initialMode={initialConvertMode} />
            )}
            {isToolsCenter && (
              <ToolsCenter key={activeItem} initialTool={activeItem as 'merge' | 'split' | 'optimize'} onNavigate={setActiveItem} />
            )}
            {standalonePages.has(activeItem) && activeItem === 'watermark' && (
              <WatermarkPage key={activeItem} />
            )}
            {!isTemplatePage && !isConvertPage && !isToolsCenter && !standalonePages.has(activeItem) && activeItem !== 'dashboard' && (
              <PlaceholderPage
                title={activeItem
                  .split('-')
                  .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                  .join(' ')}
              />
            )}
          </main>

          {/* Right Quick Actions Panel */}
          {!noQuickActionsIds.has(activeItem) && (
            <QuickActionsPanel
              onActionClick={handleQuickAction}
              currentPage={activeItem}
            />
          )}
        </div>
      </div>
    </div>
  )
}
