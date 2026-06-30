import { useState } from 'react'
import {
  Globe,
  Sun,
  Moon,
  Monitor,
  FolderOpen,
  FileOutput,
  Zap,
  AlertTriangle,
  RefreshCw,
  MessageSquare,
  ExternalLink,
  Github,
  ChevronRight,
  Trash2,
} from 'lucide-react'
import PageHeader from '../../design-system-v1.3/components/PageHeader'

/* ─── Toggle Switch ─── */
function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="relative h-5 w-9 cursor-pointer rounded-full transition-colors duration-200"
      style={{ backgroundColor: checked ? 'var(--primary)' : 'var(--border)' }}
    >
      <span
        className={`absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200 ${
          checked ? 'translate-x-4' : 'translate-x-0'
        }`}
      />
    </button>
  )
}

/* ─── Radio Pill ─── */
function RadioPill({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string; icon?: typeof Sun }[]
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div
      className="flex gap-1.5 rounded-lg border p-1"
      style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-app)' }}
    >
      {options.map((opt) => {
        const Icon = opt.icon
        const isActive = value === opt.value
        return (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value)}
            className={`flex flex-1 cursor-pointer items-center justify-center gap-1.5 rounded-md py-2 text-[12px] font-medium transition-all duration-150 ${
              isActive ? 'shadow-sm' : 'hover:opacity-80'
            }`}
            style={isActive
              ? { backgroundColor: 'var(--bg-card)', color: 'var(--primary-text)' }
              : { color: 'var(--text-secondary)' }
            }
          >
            {Icon && <Icon size={13} strokeWidth={1.8} />}
            <span>{opt.label}</span>
          </button>
        )
      })}
    </div>
  )
}

/* ─── Setting Row ─── */
function SettingRow({
  title,
  description,
  children,
}: {
  title: string
  description?: string
  children: React.ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div className="min-w-0">
        <p className="text-[14px] font-medium" style={{ color: 'var(--text-primary)' }}>{title}</p>
        {description && <p className="mt-0.5 text-[12px]" style={{ color: 'var(--text-muted)' }}>{description}</p>}
      </div>
      <div className="flex-shrink-0">{children}</div>
    </div>
  )
}

/* ─── Section Card ─── */
function SectionCard({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div
      className="rounded-2xl border p-6"
      style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
    >
      <h3 className="mb-5 text-[12px] font-bold uppercase tracking-[1.5px]" style={{ color: 'var(--text-muted)' }}>
        {title}
      </h3>
      <div className="flex flex-col gap-4">{children}</div>
    </div>
  )
}

/* ─── Main Settings Page ─── */
interface SettingsPageProps {
  developerMode: boolean
  onDeveloperModeChange: (enabled: boolean) => void
  theme: 'light' | 'dark'
  onThemeChange: (theme: 'light' | 'dark') => void
}

export default function SettingsPage({ developerMode, onDeveloperModeChange, theme, onThemeChange }: SettingsPageProps) {
  // General
  const [language, setLanguage] = useState('en-US')
  const [launchOnStartup, setLaunchOnStartup] = useState(false)

  // Files
  const [outputFolder] = useState('Same as source')
  const [filenamePattern, setFilenamePattern] = useState('{input}_out')

  // Performance
  const [perfMode, setPerfMode] = useState('balanced')
  const [lazyLoading, setLazyLoading] = useState(true)
  const [localProcessing, setLocalProcessing] = useState(true)

  // Privacy
  const [offlineMode, setOfflineMode] = useState(true)
  const [analytics, setAnalytics] = useState(false)
  const [crashReports, setCrashReports] = useState('ask')

  // Developer
  const [debugLogs, setDebugLogs] = useState(false)
  const [showExperimental, setShowExperimental] = useState(false)

  // Toast
  const [toast, setToast] = useState<string | null>(null)

  const showToast = (msg: string) => {
    setToast(msg)
    setTimeout(() => setToast(null), 3000)
  }

  const handleLanguageChange = (lang: string) => {
    setLanguage(lang)
    showToast('Restart required to apply language changes.')
  }

  const handleThemeChange = (value: string) => {
    // "system" falls back to 'light' for now (no OS-level detection in prototype)
    onThemeChange(value === 'dark' ? 'dark' : 'light')
  }

  return (
    <div className="mx-auto max-w-3xl px-8 py-6">
      {/* Toast */}
      <div
        className={`fixed top-6 left-1/2 z-50 -translate-x-1/2 rounded-xl border px-5 py-3 shadow-lg transition-all duration-300 ${
          toast ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0 pointer-events-none'
        }`}
        style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
      >
        <div className="flex items-center gap-3">
          <div className="flex h-7 w-7 items-center justify-center rounded-full" style={{ backgroundColor: 'var(--warning-bg)' }}>
            <AlertTriangle size={14} style={{ color: 'var(--warning)' }} />
          </div>
          <p className="text-[13px] font-medium" style={{ color: 'var(--text-primary)' }}>{toast || ' '}</p>
        </div>
      </div>

      {/* Header */}
      <PageHeader
        title="Settings"
        subtitle="Customize PDFflow to fit your workflow."
      />

      <div className="flex flex-col gap-4">
        {/* ── General ── */}
        <SectionCard title="General">
          {/* Language */}
          <SettingRow title="Language" description="Choose your preferred display language">
            <div className="relative">
              <Globe size={14} className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
              <select
                value={language}
                onChange={(e) => handleLanguageChange(e.target.value)}
                className="h-9 cursor-pointer appearance-none rounded-lg border pl-9 pr-8 text-[13px] outline-none transition-colors"
                style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
              >
                <option value="en-US">English (United States)</option>
                <option value="zh-CN">中文（简体）</option>
              </select>
              <ChevronRight size={12} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
            </div>
          </SettingRow>

          {/* Appearance */}
          <div className="flex flex-col gap-2">
            <p className="text-[14px] font-medium" style={{ color: 'var(--text-primary)' }}>Appearance</p>
            <RadioPill
              value={theme}
              onChange={handleThemeChange}
              options={[
                { value: 'light', label: 'Light', icon: Sun },
                { value: 'dark', label: 'Dark', icon: Moon },
                { value: 'system', label: 'System', icon: Monitor },
              ]}
            />
          </div>

          {/* Launch on Startup */}
          <SettingRow
            title="Launch on Startup"
            description="Start PDFflow when you log in"
          >
            <Toggle checked={launchOnStartup} onChange={setLaunchOnStartup} />
          </SettingRow>
        </SectionCard>

        {/* ── Files ── */}
        <SectionCard title="Files">
          <SettingRow
            title="Default Output Folder"
            description="Where processed files are saved"
          >
            <div className="flex items-center gap-2">
              <span
                className="max-w-[180px] truncate rounded-lg border px-3 py-2 text-[12px]"
                style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-app)', color: 'var(--text-secondary)' }}
              >
                {outputFolder}
              </span>
              <button
                className="flex cursor-pointer items-center gap-1.5 rounded-lg border px-3 py-2 text-[12px] font-medium transition-colors hover:opacity-80"
                style={{ borderColor: 'var(--border)', color: 'var(--primary-text)' }}
              >
                <FolderOpen size={13} />
                Browse
              </button>
            </div>
          </SettingRow>

          <SettingRow
            title="Filename Pattern"
            description="Variables: {'{input}'}, {'{date}'}, {'{tool}'}
"
          >
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={filenamePattern}
                onChange={(e) => setFilenamePattern(e.target.value)}
                className="h-9 w-40 rounded-lg border px-3 text-[13px] outline-none transition-colors"
                style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
              />
              <FileOutput size={14} style={{ color: 'var(--text-muted)' }} />
            </div>
          </SettingRow>

          <SettingRow
            title="Recent Files History"
            description="Clear list of recently processed files"
          >
            <button
              className="flex cursor-pointer items-center gap-1.5 rounded-lg px-3 py-2 text-[12px] font-medium transition-colors hover:opacity-80"
              style={{ color: 'var(--text-secondary)' }}
            >
              <Trash2 size={13} />
              Clear History
            </button>
          </SettingRow>
        </SectionCard>

        {/* ── Performance ── */}
        <SectionCard title="Performance">
          <div className="flex flex-col gap-2">
            <p className="text-[14px] font-medium" style={{ color: 'var(--text-primary)' }}>Document Processing</p>
            <RadioPill
              value={perfMode}
              onChange={setPerfMode}
              options={[
                { value: 'speed', label: 'Max Speed' },
                { value: 'balanced', label: 'Balanced' },
                { value: 'memory', label: 'Low Memory' },
              ]}
            />
          </div>

          <SettingRow
            title="Lazy Loading"
            description="Load features only when needed"
          >
            <Toggle checked={lazyLoading} onChange={setLazyLoading} />
          </SettingRow>

          <SettingRow
            title="OCR Engine"
            description="RapidOCR — Ready"
          >
            <div
              className="flex items-center gap-1.5 rounded-lg border px-3 py-2"
              style={{ borderColor: 'var(--border)', backgroundColor: 'var(--success-bg)' }}
            >
              <div className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: 'var(--success)' }} />
              <span className="text-[12px] font-medium" style={{ color: 'var(--success)' }}>Ready</span>
            </div>
          </SettingRow>

          <SettingRow
            title="Local Processing"
            description="All files remain on your device"
          >
            <div className="flex items-center gap-2">
              <Toggle checked={localProcessing} onChange={setLocalProcessing} />
              {localProcessing && (
                <span style={{ color: 'var(--success)' }}>
                  <Zap size={12} strokeWidth={2} className="mr-0.5 inline" />
                  Enabled
                </span>
              )}
            </div>
          </SettingRow>
        </SectionCard>

        {/* ── Privacy ── */}
        <SectionCard title="Privacy">
          <SettingRow
            title="Offline Mode"
            description="All operations run locally, no internet required"
          >
            <Toggle checked={offlineMode} onChange={setOfflineMode} />
          </SettingRow>

          <SettingRow
            title="Anonymous Analytics"
            description="Help improve PDFflow with anonymous usage data"
          >
            <Toggle checked={analytics} onChange={setAnalytics} />
          </SettingRow>

          <SettingRow
            title="Crash Reports"
            description="Send error reports to help fix bugs"
          >
            <div
              className="flex gap-1.5 rounded-lg border p-1"
              style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-app)' }}
            >
              {[
                { value: 'always', label: 'Always' },
                { value: 'ask', label: 'Ask' },
                { value: 'never', label: 'Never' },
              ].map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setCrashReports(opt.value)}
                  className={`flex-1 cursor-pointer rounded-md py-1.5 text-[12px] font-medium transition-all duration-150 ${
                    crashReports === opt.value ? 'shadow-sm' : 'hover:opacity-80'
                  }`}
                  style={crashReports === opt.value
                    ? { backgroundColor: 'var(--bg-card)', color: 'var(--primary-text)' }
                    : { color: 'var(--text-secondary)' }
                  }
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </SettingRow>
        </SectionCard>

        {/* ── Developer (only when enabled) ── */}
        {developerMode && (
          <SectionCard title="Developer">
            <SettingRow
              title="Enable AI Labs"
              description="Unlock experimental AI features in sidebar"
            >
              <Toggle checked={developerMode} onChange={onDeveloperModeChange} />
            </SettingRow>

            <SettingRow
              title="Show Experimental Features"
              description="Display unfinished features in the interface"
            >
              <Toggle checked={showExperimental} onChange={setShowExperimental} />
            </SettingRow>

            <SettingRow
              title="Debug Logging"
              description="Write detailed logs to disk for troubleshooting"
            >
              <Toggle checked={debugLogs} onChange={setDebugLogs} />
            </SettingRow>
          </SectionCard>
        )}

        {/* ── About ── */}
        <SectionCard title="About">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl" style={{ backgroundColor: 'var(--primary)' }}>
              <span className="text-lg font-bold text-white">P</span>
            </div>
            <div className="flex-1">
              <p className="text-[16px] font-semibold" style={{ color: 'var(--text-primary)' }}>PDFflow</p>
              <p className="mt-0.5 text-[12px]" style={{ color: 'var(--text-muted)' }}>Document Workflow Platform</p>
              <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-[12px]" style={{ color: 'var(--text-secondary)' }}>
                <span>Version: <span className="font-medium" style={{ color: 'var(--text-primary)' }}>1.3.0</span></span>
                <span style={{ color: 'var(--text-muted)' }}>|</span>
                <span>Built with PySide6, PyMuPDF, RapidOCR</span>
              </div>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            {[
              { label: 'Check Updates', icon: RefreshCw },
              { label: 'Feedback', icon: MessageSquare },
              { label: 'Open Website', icon: ExternalLink },
              { label: 'GitHub', icon: Github },
            ].map((btn) => {
              const Icon = btn.icon
              return (
                <button
                  key={btn.label}
                  className="flex cursor-pointer items-center gap-1.5 rounded-lg border px-3 py-2 text-[12px] font-medium transition-colors hover:opacity-80"
                  style={{ borderColor: 'var(--border)', color: 'var(--text-primary)' }}
                >
                  <Icon size={13} strokeWidth={1.8} />
                  {btn.label}
                </button>
              )
            })}
          </div>
        </SectionCard>
      </div>

      {/* Bottom spacer */}
      <div className="h-12" />
    </div>
  )
}
