import { useState, useCallback } from 'react'
import {
  UploadCloud,
  Table2,
  FileDown,
  MonitorPlay,
  Download,
  Check,
  Loader2,
  FileText,
  Trash2,
  AlertCircle,
} from 'lucide-react'
import PageHeader from '../../design-system-v1.3/components/PageHeader'
import PrimaryButton from '../../design-system-v1.3/components/PrimaryButton'

type ConvertMode = 'pdf-excel' | 'pdf-word' | 'pdf-ppt'

interface UploadedFile {
  name: string
  size: string
  status: 'pending' | 'processing' | 'done' | 'error'
  progress: number
}

const modeLabels: Record<ConvertMode, string> = {
  'pdf-excel': 'PDF → Excel',
  'pdf-word': 'PDF → Word',
  'pdf-ppt': 'PDF → PPT',
}

const modeIcons: Record<ConvertMode, typeof Table2> = {
  'pdf-excel': Table2,
  'pdf-word': FileDown,
  'pdf-ppt': MonitorPlay,
}

interface ConvertPageProps {
  initialMode?: ConvertMode
}

export default function ConvertPage({ initialMode = 'pdf-excel' }: ConvertPageProps) {
  const [activeMode, setActiveMode] = useState<ConvertMode>(initialMode)
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  // Mode-specific settings
  const [ocrEnabled, setOcrEnabled] = useState(false)
  const [tableDetection, setTableDetection] = useState(true)
  const [preserveLayout, setPreserveLayout] = useState(true)
  const [editableText, setEditableText] = useState(false)
  const [slideSensitivity, setSlideSensitivity] = useState(50)
  const [autoLayout, setAutoLayout] = useState(true)

  const hasFiles = files.length > 0
  const allDone = files.length > 0 && files.every((f) => f.status === 'done')
  const isProcessing = files.some((f) => f.status === 'processing')

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const newFiles: UploadedFile[] = Array.from(e.dataTransfer.files).map((f) => ({
      name: f.name,
      size: `${(f.size / 1024).toFixed(0)} KB`,
      status: 'pending' as const,
      progress: 0,
    }))
    if (newFiles.length) {
      setFiles((prev) => [...prev, ...newFiles])
      setShowSettings(true)
    }
  }, [])

  const handleBrowse = () => {
    const newFile: UploadedFile = {
      name: 'document_sample.pdf',
      size: '1.2 MB',
      status: 'pending',
      progress: 0,
    }
    setFiles((prev) => [...prev, newFile])
    setShowSettings(true)
  }

  const startConversion = () => {
    setFiles((prev) =>
      prev.map((f) =>
        f.status === 'pending' ? { ...f, status: 'processing', progress: 0 } : f
      )
    )

    // Simulate conversion progress
    let progress = 0
    const interval = setInterval(() => {
      progress += Math.random() * 15 + 5
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        setFiles((prev) =>
          prev.map((f) =>
            f.status === 'processing' ? { ...f, status: 'done', progress: 100 } : f
          )
        )
      } else {
        setFiles((prev) =>
          prev.map((f) =>
            f.status === 'processing' ? { ...f, progress: Math.min(progress, 99) } : f
          )
        )
      }
    }, 400)
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
    if (files.length <= 1) setShowSettings(false)
  }

  const ModeIcon = modeIcons[activeMode]

  return (
    <div className="mx-auto max-w-3xl px-8 py-6">
      {/* Header */}
      <PageHeader title="PDF Conversion" subtitle="Convert your documents with high accuracy and speed" />

      {/* Mode Tabs */}
      <div
        className="mb-6 flex gap-1 rounded-lg border p-1"
        style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-app)' }}
      >
        {(Object.keys(modeLabels) as ConvertMode[]).map((mode) => {
          const Icon = modeIcons[mode]
          const isActive = activeMode === mode
          return (
            <button
              key={mode}
              onClick={() => {
                setActiveMode(mode)
                setFiles([])
                setShowSettings(false)
              }}
              className={`
                flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-md py-2.5 text-[13px] font-medium
                transition-all duration-150
                ${isActive
                  ? 'shadow-sm'
                  : 'hover:opacity-80'
                }
              `}
              style={isActive
                ? { backgroundColor: 'var(--bg-card)', color: 'var(--primary-text)' }
                : { color: 'var(--text-secondary)' }
              }
            >
              <Icon size={15} strokeWidth={1.8} />
              <span>{modeLabels[mode]}</span>
            </button>
          )
        })}
      </div>

      {/* Upload Area — hidden when files exist */}
      {!hasFiles && (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`
            flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10
            transition-all duration-200
          `}
          style={{
            minHeight: 260,
            ...(dragOver
              ? { borderColor: 'var(--primary)', backgroundColor: 'var(--bg-active)' }
              : { borderColor: 'var(--border-strong)', backgroundColor: 'var(--bg-app)' }
            ),
          }}
        >
          <UploadCloud
            size={48}
            strokeWidth={1.2}
            className="mb-4 transition-colors duration-200"
            style={{ color: dragOver ? 'var(--primary-text)' : 'var(--text-muted)' }}
          />
          <p
            className="mb-1 text-[14px] font-medium"
            style={{ color: 'var(--text-primary)' }}
          >
            Drag & drop your files here
          </p>
          <p
            className="mb-5 text-[12px]"
            style={{ color: 'var(--text-muted)' }}
          >
            PDF supported. Max 50MB per file
          </p>
          <PrimaryButton label="Browse Files" size="md" onClick={handleBrowse} />
        </div>
      )}

      {/* File List + Actions */}
      {hasFiles && (
        <div className="space-y-4">
          {/* Uploaded files card */}
          <div
            className="rounded-xl border p-5 shadow-sm"
            style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
          >
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>Uploaded Files</h3>
              <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{files.length} file{files.length !== 1 ? 's' : ''}</span>
            </div>

            <div className="flex flex-col gap-2">
              {files.map((file, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 rounded-lg border px-4 py-3"
                  style={{ borderColor: 'var(--bg-input-placeholder)' }}
                >
                  <FileText size={18} strokeWidth={1.5} className="flex-shrink-0" style={{ color: 'var(--error)' }} />
                  <div className="flex-1 min-w-0">
                    <p className="text-[13px] font-medium truncate" style={{ color: 'var(--text-primary)' }}>{file.name}</p>
                    <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{file.size}</p>
                  </div>

                  {/* Status */}
                  {file.status === 'pending' && (
                    <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>Ready</span>
                  )}
                  {file.status === 'processing' && (
                    <div className="flex items-center gap-2">
                      <Loader2 size={14} className="animate-spin" style={{ color: 'var(--primary-text)' }} />
                      <span className="text-[12px]" style={{ color: 'var(--primary-text)' }}>{Math.round(file.progress)}%</span>
                    </div>
                  )}
                  {file.status === 'done' && (
                    <div className="flex items-center gap-1">
                      <Check size={14} style={{ color: 'var(--success)' }} />
                      <span className="text-[12px]" style={{ color: 'var(--success)' }}>Done</span>
                    </div>
                  )}
                  {file.status === 'error' && (
                    <div className="flex items-center gap-1">
                      <AlertCircle size={14} style={{ color: 'var(--error)' }} />
                      <span className="text-[12px]" style={{ color: 'var(--error)' }}>Failed</span>
                    </div>
                  )}

                  {!isProcessing && (
                    <button
                      onClick={() => removeFile(i)}
                      className="cursor-pointer rounded p-1 transition-colors hover:opacity-80"
                      style={{ color: 'var(--text-muted)' }}
                    >
                      <Trash2 size={14} />
                    </button>
                  )}
                </div>
              ))}

              {/* Progress bar for processing */}
              {isProcessing && (
                <div className="mt-2">
                  <div className="h-1.5 w-full rounded-full" style={{ backgroundColor: 'var(--bg-input-placeholder)' }}>
                    <div
                      className="h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${files.find(f => f.status === 'processing')?.progress || 0}%`, backgroundColor: 'var(--primary)' }}
                    />
                  </div>
                  <div className="mt-1.5 flex justify-between text-[11px]" style={{ color: 'var(--text-muted)' }}>
                    <span>Converting...</span>
                    <span>
                      {(() => {
                        const p = files.find(f => f.status === 'processing')?.progress || 0
                        if (p < 30) return 'Uploading → OCR'
                        if (p < 60) return 'Parsing content'
                        if (p < 90) return 'Generating output'
                        return 'Finalizing...'
                      })()}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Add more files */}
            <div className="mt-3 flex items-center gap-2">
              <button
                type="button"
                onClick={handleBrowse}
                className="text-[12px] hover:underline cursor-pointer bg-transparent border-none"
                style={{ color: 'var(--primary-text)' }}
              >
                + Add more files
              </button>
            </div>
          </div>

          {/* Settings Panel */}
          {showSettings && !allDone && (
            <div
              className="rounded-xl border p-5 shadow-sm"
              style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
            >
              <div className="mb-4 flex items-center gap-2">
                <ModeIcon size={16} strokeWidth={1.8} style={{ color: 'var(--primary-text)' }} />
                <h3 className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {modeLabels[activeMode]} Settings
                </h3>
              </div>

              <div className="flex flex-col gap-4">
                {activeMode === 'pdf-excel' && (
                  <>
                    <ToggleSetting label="OCR Extraction" description="Extract text from scanned PDFs" enabled={ocrEnabled} onToggle={setOcrEnabled} />
                    <ToggleSetting label="Table Detection" description="Auto-detect and structure tables" enabled={tableDetection} onToggle={setTableDetection} />
                  </>
                )}
                {activeMode === 'pdf-word' && (
                  <>
                    <ToggleSetting label="Preserve Layout" description="Keep original formatting and layout" enabled={preserveLayout} onToggle={setPreserveLayout} />
                    <ToggleSetting label="Editable Text Mode" description="Convert to fully editable text" enabled={editableText} onToggle={setEditableText} />
                  </>
                )}
                {activeMode === 'pdf-ppt' && (
                  <>
                    <SliderSetting label="Slide Segmentation" value={slideSensitivity} onChange={setSlideSensitivity} />
                    <ToggleSetting label="Auto Layout Detection" description="Automatically detect slide boundaries" enabled={autoLayout} onToggle={setAutoLayout} />
                  </>
                )}
              </div>
            </div>
          )}

          {/* CTA Button */}
          <div>
            {allDone ? (
              <div
                className="rounded-xl border p-5"
                style={{ borderColor: 'rgba(34, 197, 94, 0.2)', backgroundColor: 'var(--success-bg)' }}
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full" style={{ backgroundColor: 'var(--success-bg)' }}>
                    <Check size={20} style={{ color: 'var(--success)' }} />
                  </div>
                  <div className="flex-1">
                    <p className="text-[14px] font-medium" style={{ color: 'var(--text-primary)' }}>Conversion Complete</p>
                    <p className="text-[12px]" style={{ color: 'var(--text-secondary)' }}>{files.length} file{files.length !== 1 ? 's' : ''} ready to download</p>
                  </div>
                </div>
                <div className="mt-4 flex gap-3">
                  {files.map((file, i) => (
                    <div key={i} className="flex flex-1 items-center gap-2 rounded-lg border px-3 py-2.5" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}>
                      <FileText size={14} style={{ color: 'var(--primary-text)' }} className="flex-shrink-0" />
                      <span className="flex-1 truncate text-[12px]" style={{ color: 'var(--text-primary)' }}>{file.name.replace('.pdf', '')}.xlsx</span>
                      <PrimaryButton label="Download" size="sm" />
                    </div>
                  ))}
                </div>
                <div className="mt-3 flex justify-center">
                  <button
                    className="cursor-pointer rounded-lg px-4 py-2 text-[12px] font-medium transition-colors hover:opacity-80"
                    style={{ backgroundColor: 'var(--bg-input-placeholder)', color: 'var(--text-secondary)' }}
                  >
                    Convert More Files
                  </button>
                </div>
              </div>
            ) : (
              <PrimaryButton
                block
                label={isProcessing ? 'Processing...' : 'Start Conversion'}
                loading={isProcessing}
                disabled={!hasFiles}
                onClick={startConversion}
              >
                {!isProcessing && <ModeIcon size={16} strokeWidth={1.8} />}
              </PrimaryButton>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

/* Toggle Setting Component */
function ToggleSetting({
  label,
  description,
  enabled,
  onToggle,
}: {
  label: string
  description: string
  enabled: boolean
  onToggle: (v: boolean) => void
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <p className="text-[13px] font-medium" style={{ color: 'var(--text-primary)' }}>{label}</p>
        <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{description}</p>
      </div>
      <button
        type="button"
        onClick={() => onToggle(!enabled)}
        className="relative h-6 w-11 cursor-pointer rounded-full transition-colors duration-200"
        style={{ backgroundColor: enabled ? 'var(--primary)' : 'var(--border)' }}
      >
        <span
          className={`absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform duration-200 ${
            enabled ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  )
}

/* Slider Setting Component */
function SliderSetting({
  label,
  value,
  onChange,
}: {
  label: string
  value: number
  onChange: (v: number) => void
}) {
  return (
    <div>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-[13px] font-medium" style={{ color: 'var(--text-primary)' }}>{label}</p>
        <span className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{value}%</span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full"
        style={{ backgroundColor: 'var(--bg-input-placeholder)', accentColor: 'var(--primary)' }}
      />
      <div className="mt-1 flex justify-between text-[11px]" style={{ color: 'var(--text-muted)' }}>
        <span>Less sensitive</span>
        <span>More sensitive</span>
      </div>
    </div>
  )
}
