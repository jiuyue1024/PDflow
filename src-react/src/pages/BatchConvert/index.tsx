import { useState, useCallback } from 'react'
import {
  Table2,
  FileText,
  MonitorPlay,
  ImageIcon,
  UploadCloud,
  Download,
  Check,
  Loader2,
  X,
  File,
  FolderOpen,
  Clock,
  HardDrive,
  PackageOpen,
} from 'lucide-react'
import PageHeader from '../../design-system-v1.3/components/PageHeader'
import PrimaryButton from '../../design-system-v1.3/components/PrimaryButton'

type FormatId = 'excel' | 'word' | 'ppt' | 'images'

interface FormatDef {
  id: FormatId
  label: string
  ext: string
  icon: typeof Table2
  color: string
}

const formats: FormatDef[] = [
  { id: 'excel', label: 'Excel', ext: '.xlsx', icon: Table2, color: '#22C55E' },
  { id: 'word', label: 'Word', ext: '.docx', icon: FileText, color: '#4F8CFF' },
  { id: 'ppt', label: 'PowerPoint', ext: '.pptx', icon: MonitorPlay, color: '#F59E0B' },
  { id: 'images', label: 'Images', ext: '.png', icon: ImageIcon, color: '#A855F7' },
]

const steps = [
  { label: 'Choose Format', icon: '1' as const },
  { label: 'Upload Files', icon: '2' as const },
  { label: 'Convert', icon: '3' as const },
  { label: 'Download', icon: '4' as const },
]

interface UploadedFile {
  name: string
  size: string
  sizeNum: number
}

export default function BatchConvert() {
  const [selectedFormat, setSelectedFormat] = useState<FormatId | null>(null)
  const [step, setStep] = useState(0)
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDone, setIsDone] = useState(false)
  const [progress, setProgress] = useState(0)
  const [downloadHovered, setDownloadHovered] = useState(false)

  const totalSize = files.reduce((sum, f) => sum + f.sizeNum, 0)
  const selectedFormatDef = formats.find((f) => f.id === selectedFormat)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const newFiles: UploadedFile[] = Array.from(e.dataTransfer.files).map((f) => ({
      name: f.name,
      size: `${(f.size / 1024).toFixed(0)} KB`,
      sizeNum: f.size,
    }))
    if (newFiles.length) {
      setFiles((prev) => [...prev, ...newFiles])
      if (step < 1) setStep(1)
    }
  }, [step])

  const handleBrowse = () => {
    const names = ['report_q2.pdf', 'invoice_march.pdf', 'presentation.pdf', 'data_analysis.pdf', 'contract_2026.pdf']
    const name = names[files.length % names.length]
    const sizeNum = Math.floor(Math.random() * 4000 + 500)
    setFiles((prev) => [...prev, { name, size: `${(sizeNum / 1024).toFixed(1)} MB`, sizeNum }])
    if (step < 1) setStep(1)
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
    if (files.length <= 1) {
      setStep(selectedFormat ? 1 : 0)
    }
  }

  const startConversion = () => {
    setStep(2)
    setIsProcessing(true)
    setProgress(0)

    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + Math.random() * 15 + 5
      })
    }, 400)

    setTimeout(() => {
      clearInterval(interval)
      setProgress(100)
      setIsProcessing(false)
      setStep(3)
      setIsDone(true)
    }, 3000)
  }

  const reset = () => {
    setStep(0)
    setFiles([])
    setSelectedFormat(null)
    setIsDone(false)
    setIsProcessing(false)
    setProgress(0)
  }

  const canStart = selectedFormat && files.length > 0 && step >= 1 && !isProcessing
  const currentStep = step

  const FormatIcon = selectedFormatDef?.icon || Table2

  return (
    <div className="mx-auto max-w-4xl px-8 py-6">
      {/* Header */}
      <PageHeader title="Batch Convert" subtitle="Convert multiple documents into one target format." />

      {/* Stepper — kept as custom JSX for horizontal layout + Check icon on last step */}
      <div
        className="mb-8 flex items-center justify-between rounded-2xl border px-6 py-4"
        style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
      >
        {steps.map((s, i) => {
          const isActive = i <= currentStep
          const isCurrent = i === currentStep
          return (
            <div key={i} className="flex items-center">
              <div className="flex items-center gap-2.5">
                <div
                  className={`
                    flex h-8 w-8 items-center justify-center rounded-full text-[12px] font-semibold
                    transition-all duration-200
                    ${isCurrent ? 'scale-110' : ''}
                  `}
                  style={isCurrent
                    ? { backgroundColor: 'var(--primary)', color: 'white' }
                    : isActive
                      ? { backgroundColor: 'rgba(79, 140, 255, 0.15)', color: 'var(--primary-text)' }
                      : { backgroundColor: 'var(--stepper-inactive-bg)', color: 'var(--text-muted)' }
                  }
                >
                  {isDone && i === 3 ? <Check size={14} strokeWidth={2.5} /> : s.icon}
                </div>
                <span
                  className="text-[13px] font-medium whitespace-nowrap"
                  style={{
                    color: isCurrent ? 'var(--primary-text)' : isActive ? 'var(--text-primary)' : 'var(--text-muted)'
                  }}
                >
                  {s.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className="mx-4 h-px w-16"
                  style={{ backgroundColor: i < currentStep ? 'var(--primary)' : 'var(--border)' }}
                />
              )}
            </div>
          )
        })}
      </div>

      {/* Two-column layout */}
      {!isDone && (
        <div className="grid grid-cols-2 gap-4">
          {/* Left: Target Format */}
          <div
            className="rounded-2xl border p-6"
            style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
          >
            <h3 className="mb-5 text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>Target Format</h3>
            <div className="flex flex-col gap-3">
              {formats.map((fmt) => {
                const Icon = fmt.icon
                const isSelected = selectedFormat === fmt.id
                return (
                  <button
                    key={fmt.id}
                    onClick={() => {
                      setSelectedFormat(fmt.id)
                      if (files.length > 0 && step < 1) setStep(1)
                    }}
                    className="group flex cursor-pointer items-center gap-4 rounded-xl border-2 p-4 text-left transition-all duration-200"
                    style={isSelected
                      ? { borderColor: 'var(--primary)', backgroundColor: 'var(--bg-active)', boxShadow: '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)' }
                      : { borderColor: 'transparent', backgroundColor: 'var(--bg-app)', boxShadow: 'none' }
                    }
                  >
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-xl transition-colors duration-200"
                      style={{ backgroundColor: isSelected ? `${fmt.color}18` : 'var(--border)' }}
                    >
                      <Icon
                        size={20}
                        strokeWidth={1.5}
                        style={{ color: isSelected ? fmt.color : 'var(--text-secondary)' }}
                      />
                    </div>
                    <div className="min-w-0">
                      <p className="text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {fmt.label}
                      </p>
                      <p className="text-[12px]" style={{ color: isSelected ? 'var(--primary-text)' : 'var(--text-muted)' }}>
                        {fmt.ext}
                      </p>
                    </div>
                    {isSelected && (
                      <div className="ml-auto flex h-5 w-5 items-center justify-center rounded-full" style={{ backgroundColor: 'var(--primary)' }}>
                        <Check size={12} strokeWidth={3} className="text-white" />
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Right: Uploaded Files */}
          <div
            className="rounded-2xl border p-6"
            style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
          >
            <h3 className="mb-5 text-[14px] font-semibold" style={{ color: 'var(--text-primary)' }}>
              Uploaded Files
              {files.length > 0 && <span className="ml-2 text-[13px] font-normal" style={{ color: 'var(--text-muted)' }}>({files.length})</span>}
            </h3>

            {/* File list or upload area */}
            {files.length === 0 ? (
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed transition-all duration-200"
                style={dragOver
                  ? { borderColor: 'var(--primary)', backgroundColor: 'var(--bg-active)', minHeight: 220 }
                  : { borderColor: 'var(--border-strong)', backgroundColor: 'var(--bg-app)', minHeight: 220 }
                }
              >
                <UploadCloud size={36} strokeWidth={1.2} className="mb-3 transition-colors duration-200" style={{ color: dragOver ? 'var(--primary-text)' : 'var(--text-muted)' }} />
                <p className="mb-1 text-[14px] font-medium" style={{ color: 'var(--text-primary)' }}>Drag & drop your files here</p>
                <p className="mb-4 text-[12px]" style={{ color: 'var(--text-muted)' }}>PDF, DOCX, XLSX, PPTX supported</p>
                <PrimaryButton label="Browse Files" size="md" onClick={handleBrowse} />
              </div>
            ) : (
              <>
                <div className="flex flex-col gap-2 max-h-[280px] overflow-y-auto">
                  {files.map((file, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-3 rounded-xl border px-4 py-3 transition-colors hover:opacity-80"
                      style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-app)' }}
                    >
                      <File size={18} strokeWidth={1.5} className="flex-shrink-0" style={{ color: 'var(--error)' }} />
                      <div className="flex-1 min-w-0">
                        <p className="truncate text-[13px] font-medium" style={{ color: 'var(--text-primary)' }}>{file.name}</p>
                        <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>{file.size}</p>
                      </div>
                      <button
                        onClick={() => removeFile(i)}
                        className="cursor-pointer rounded-lg p-1.5 transition-colors hover:opacity-80"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        <X size={14} strokeWidth={2} />
                      </button>
                    </div>
                  ))}
                </div>

                <button
                  type="button"
                  onClick={handleBrowse}
                  className="mt-3 flex w-full cursor-pointer items-center justify-center gap-1.5 rounded-xl border border-dashed py-3 text-[12px] font-medium transition-colors hover:opacity-80"
                  style={{ borderColor: 'var(--border-strong)', color: 'var(--text-secondary)' }}
                >
                  <UploadCloud size={14} />
                  Add Files
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Processing state */}
      {isProcessing && (
        <div
          className="rounded-2xl border p-8"
          style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
        >
          <div className="flex flex-col items-center">
            <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary-text)' }} />
            <p className="mt-4 text-[16px] font-semibold" style={{ color: 'var(--text-primary)' }}>Converting files...</p>
            <p className="mt-1 text-[13px]" style={{ color: 'var(--text-muted)' }}>
              {progress < 30 ? 'Reading documents...' : progress < 60 ? 'Analyzing content...' : progress < 90 ? 'Generating output...' : 'Finalizing...'}
            </p>
            <div className="mt-6 w-full max-w-sm">
              <div className="h-2 rounded-full" style={{ backgroundColor: 'var(--bg-input-placeholder)' }}>
                <div
                  className="h-2 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${Math.min(progress, 100)}%`, backgroundColor: 'var(--primary)' }}
                />
              </div>
              <p className="mt-2 text-center text-[12px]" style={{ color: 'var(--text-muted)' }}>
                {Math.min(Math.round(progress), 100)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Completion state */}
      {isDone && (
        <div
          className="rounded-2xl border p-8"
          style={{ borderColor: 'rgba(34, 197, 94, 0.2)', backgroundColor: 'var(--success-bg)' }}
        >
          <div className="flex flex-col items-center text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl" style={{ backgroundColor: 'var(--success-bg)' }}>
              <Check size={28} style={{ color: 'var(--success)' }} strokeWidth={2.5} />
            </div>
            <p className="mt-4 text-[18px] font-semibold" style={{ color: 'var(--text-primary)' }}>Batch Conversion Complete</p>
            <p className="mt-1 text-[14px]" style={{ color: 'var(--text-secondary)' }}>
              {files.length} file{files.length !== 1 ? 's' : ''} converted to {selectedFormatDef?.label}
            </p>
            <div className="mt-6 flex gap-3">
              <PrimaryButton
                label="Download ZIP"
                size="md"
                onMouseEnter={() => setDownloadHovered(true)}
                onMouseLeave={() => setDownloadHovered(false)}
              >
                <Download size={16} strokeWidth={1.8} />
              </PrimaryButton>
              <button
                className="flex cursor-pointer items-center gap-2 rounded-xl border px-6 py-3 text-[14px] font-medium transition-colors hover:opacity-80"
                style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)', color: 'var(--text-primary)' }}
              >
                <FolderOpen size={16} strokeWidth={1.8} />
                Open Folder
              </button>
            </div>
            <button
              onClick={reset}
              className="mt-4 cursor-pointer text-[13px] font-medium transition-colors hover:opacity-80"
              style={{ color: 'var(--text-secondary)' }}
            >
              Convert Another Batch
            </button>
          </div>
        </div>
      )}

      {/* Batch Summary + CTA */}
      {!isDone && !isProcessing && (
        <div
          className="mt-5 rounded-2xl border p-5"
          style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2 text-[13px]">
                <File size={14} style={{ color: 'var(--text-muted)' }} />
                <span style={{ color: 'var(--text-secondary)' }}>Files:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{files.length}</span>
              </div>
              <div className="flex items-center gap-2 text-[13px]">
                <HardDrive size={14} style={{ color: 'var(--text-muted)' }} />
                <span style={{ color: 'var(--text-secondary)' }}>Total:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>
                  {totalSize < 1024 * 1024
                    ? `${(totalSize / 1024).toFixed(0)} KB`
                    : `${(totalSize / (1024 * 1024)).toFixed(1)} MB`}
                </span>
              </div>
              {selectedFormatDef && (
                <div className="flex items-center gap-2 text-[13px]">
                  <PackageOpen size={14} style={{ color: 'var(--text-muted)' }} />
                  <span style={{ color: 'var(--text-secondary)' }}>Format:</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{selectedFormatDef.label}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-[13px]">
                <Clock size={14} style={{ color: 'var(--text-muted)' }} />
                <span style={{ color: 'var(--text-secondary)' }}>Est:</span>
                <span className="font-medium" style={{ color: 'var(--text-primary)' }}>~{Math.max(3, files.length * 2)}s</span>
              </div>
            </div>

            <PrimaryButton
              label={canStart ? 'Start Batch Conversion' : 'Select format & files to start'}
              disabled={!canStart}
              loading={isProcessing}
              onClick={startConversion}
            >
              <FormatIcon size={16} strokeWidth={1.8} />
            </PrimaryButton>
          </div>
        </div>
      )}

      {/* Bottom spacer */}
      <div className="h-8" />
    </div>
  )
}
