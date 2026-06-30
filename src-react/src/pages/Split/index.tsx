import { useState, useCallback, useEffect } from 'react'
import {
  Scissors,
  UploadCloud,
  FileText,
  Trash2,
  Check,
  Loader2,
  Download,
  Layers,
} from 'lucide-react'

import PageHeader from '../../design-system-v1.3/components/PageHeader'
import StepIndicator from '../../design-system-v1.3/components/StepIndicator'
import UploadZone from '../../design-system-v1.3/components/UploadZone'
import FileList from '../../design-system-v1.3/components/FileList'
import type { FileItem } from '../../design-system-v1.3/components/FileList'
import PrimaryButton from '../../design-system-v1.3/components/PrimaryButton'
import EmptyState from '../../design-system-v1.3/components/EmptyState'

type SplitMode = 'range' | 'every' | 'extract'

const STEPS = ['Upload File', 'Configure Split', 'Processing', 'Complete']

export default function SplitPage() {
  const [step, setStep] = useState(0)
  const [files, setFiles] = useState<FileItem[]>([])
  const [splitMode, setSplitMode] = useState<SplitMode>('range')
  const [splitRange, setSplitRange] = useState('1-3, 5-10')
  const [splitEvery, setSplitEvery] = useState(5)
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [resultCount, setResultCount] = useState(0)

  // ── Step 0: Upload ──────────────────────────────────────────────

  const handleBrowse = useCallback(() => {
    const mockFile: FileItem = {
      id: 'split-1',
      name: 'document.pdf',
      size: 3_456_789,
      pages: 24,
    }
    setFiles([mockFile])
    setStep(1)
  }, [])

  const handleFilesChange = useCallback((incoming: File[]) => {
    if (incoming.length === 0) return
    const mapped: FileItem[] = incoming.map((f, i) => ({
      id: `split-${i}`,
      name: f.name,
      size: f.size,
    }))
    setFiles(mapped)
    setStep(1)
  }, [])

  // ── Step 1: Configure ──────────────────────────────────────────

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
    setStep(0)
  }, [])

  const startProcessing = useCallback(() => {
    setIsProcessing(true)
    setProgress(0)
    setStep(2)
  }, [])

  // ── Step 2: Processing simulation ──────────────────────────────

  useEffect(() => {
    if (step !== 2) return

    const total = 2500
    const interval = 50
    let elapsed = 0

    const timer = setInterval(() => {
      elapsed += interval
      const pct = Math.min(Math.round((elapsed / total) * 100), 100)
      setProgress(pct)

      if (elapsed >= total) {
        clearInterval(timer)
        setIsProcessing(false)
        setResultCount(splitMode === 'every' ? Math.ceil((files[0]?.pages ?? 24) / splitEvery) : splitMode === 'range' ? 2 : 1)
        setStep(3)
      }
    }, interval)

    return () => clearInterval(timer)
  }, [step, splitMode, splitEvery, files])

  // ── Step 3: Complete / reset ───────────────────────────────────

  const resetAll = useCallback(() => {
    setStep(0)
    setFiles([])
    setSplitMode('range')
    setSplitRange('1-3, 5-10')
    setSplitEvery(5)
    setIsProcessing(false)
    setProgress(0)
    setResultCount(0)
  }, [])

  // ── Split mode definitions ─────────────────────────────────────

  const splitModes: { id: SplitMode; label: string; icon: typeof Scissors }[] = [
    { id: 'range', label: 'By Page Range', icon: Scissors },
    { id: 'every', label: 'Split Every N', icon: Layers },
    { id: 'extract', label: 'Extract Pages', icon: FileText },
  ]

  // ── Render ─────────────────────────────────────────────────────

  return (
    <div style={{
      maxWidth: '960px',
      margin: '0 auto',
      padding: '32px 24px',
    }}>
      {/* ── Step 0: Upload ─────────────────────────────────────── */}
      {step === 0 && (
        <>
          <PageHeader
            title="Split PDF"
            subtitle="Extract pages or split a PDF into multiple documents"
            actions={<Scissors size={20} style={{ color: 'var(--text-muted)' }} strokeWidth={1.5} />}
          />
          <UploadZone
            acceptLabel="PDF file only"
            maxSizeLabel="Max 50MB"
            multiple={false}
            onFilesChange={handleFilesChange}
          />
          <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
            <button
              type="button"
              onClick={handleBrowse}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                height: '36px',
                fontSize: '13px',
                fontWeight: 500,
                color: 'var(--btn-primary-text)',
                backgroundColor: 'var(--btn-primary)',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                transition: 'background-color 0.15s ease',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--btn-primary-hover)' }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--btn-primary)' }}
            >
              <UploadCloud size={15} />
              Browse Files
            </button>
          </div>
        </>
      )}

      {/* ── Step 1: Configure ──────────────────────────────────── */}
      {step === 1 && (
        <>
          <div style={{ marginBottom: '32px' }}>
            <StepIndicator steps={STEPS.map((s) => ({ label: s }))} currentStep={1} />
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            alignItems: 'start',
          }}>
            {/* Left column: File list */}
            <div>
              <h3 style={{
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
              }}>
                Source File
              </h3>
              <FileList files={files} onRemove={removeFile} draggable={false} />
            </div>

            {/* Right column: Split configuration */}
            <div>
              <h3 style={{
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '8px',
                textTransform: 'uppercase',
                letterSpacing: '0.04em',
              }}>
                Split Configuration
              </h3>

              {/* Mode segmented control */}
              <div style={{
                display: 'flex',
                gap: '4px',
                padding: '4px',
                borderRadius: '10px',
                border: '1px solid var(--border)',
                backgroundColor: 'var(--bg-app)',
                marginBottom: '20px',
              }}>
                {splitModes.map((mode) => {
                  const Icon = mode.icon
                  const isActive = splitMode === mode.id
                  return (
                    <button
                      key={mode.id}
                      type="button"
                      onClick={() => setSplitMode(mode.id)}
                      style={{
                        flex: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px',
                        padding: '8px 4px',
                        fontSize: '12px',
                        fontWeight: 500,
                        borderRadius: '7px',
                        border: isActive ? '1px solid var(--primary)' : '1px solid transparent',
                        backgroundColor: isActive ? 'var(--bg-active)' : 'transparent',
                        color: isActive ? 'var(--primary-text)' : 'var(--text-secondary)',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                      }}
                    >
                      <Icon size={14} strokeWidth={1.8} />
                      <span>{mode.label}</span>
                    </button>
                  )
                })}
              </div>

              {/* Mode-specific configuration */}
              <div style={{
                backgroundColor: 'var(--bg-card)',
                border: '1px solid var(--border)',
                borderRadius: '12px',
                padding: '20px',
              }}>
                {splitMode === 'range' && (
                  <div>
                    <label style={{
                      display: 'block',
                      fontSize: '12px',
                      fontWeight: 500,
                      color: 'var(--text-secondary)',
                      marginBottom: '8px',
                    }}>
                      Page Range
                    </label>
                    <input
                      type="text"
                      value={splitRange}
                      onChange={(e) => setSplitRange(e.target.value)}
                      placeholder="e.g. 1-3, 5-10"
                      style={{
                        width: '100%',
                        height: '36px',
                        padding: '0 12px',
                        fontSize: '13px',
                        color: 'var(--text-primary)',
                        backgroundColor: 'var(--bg-app)',
                        border: '1px solid var(--border)',
                        borderRadius: '6px',
                        outline: 'none',
                        transition: 'border-color 0.15s ease',
                      }}
                      onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--primary)' }}
                      onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--border)' }}
                    />
                    <p style={{
                      fontSize: '11px',
                      color: 'var(--text-muted)',
                      marginTop: '6px',
                      lineHeight: '16px',
                    }}>
                      Separate ranges with commas. Each range creates a separate document.
                    </p>
                  </div>
                )}

                {splitMode === 'every' && (
                  <div>
                    <label style={{
                      display: 'block',
                      fontSize: '12px',
                      fontWeight: 500,
                      color: 'var(--text-secondary)',
                      marginBottom: '8px',
                    }}>
                      Split every
                    </label>
                    <input
                      type="number"
                      value={splitEvery}
                      onChange={(e) => setSplitEvery(Math.max(1, Number(e.target.value)))}
                      min={1}
                      style={{
                        width: '100%',
                        height: '36px',
                        padding: '0 12px',
                        fontSize: '13px',
                        color: 'var(--text-primary)',
                        backgroundColor: 'var(--bg-app)',
                        border: '1px solid var(--border)',
                        borderRadius: '6px',
                        outline: 'none',
                        transition: 'border-color 0.15s ease',
                      }}
                      onFocus={(e) => { e.currentTarget.style.borderColor = 'var(--primary)' }}
                      onBlur={(e) => { e.currentTarget.style.borderColor = 'var(--border)' }}
                    />
                    <p style={{
                      fontSize: '11px',
                      color: 'var(--text-muted)',
                      marginTop: '6px',
                      lineHeight: '16px',
                    }}>
                      Creates a new document every {splitEvery} page{splitEvery > 1 ? 's' : ''}.
                    </p>
                  </div>
                )}

                {splitMode === 'extract' && (
                  <div style={{ textAlign: 'center', padding: '24px 0' }}>
                    <FileText size={28} style={{ color: 'var(--text-muted)', marginBottom: '10px' }} strokeWidth={1.2} />
                    <p style={{
                      fontSize: '13px',
                      color: 'var(--text-secondary)',
                      margin: 0,
                      lineHeight: '20px',
                    }}>
                      Select individual pages to extract from the document.
                    </p>
                    <p style={{
                      fontSize: '11px',
                      color: 'var(--text-muted)',
                      marginTop: '4px',
                    }}>
                      Click on page thumbnails below to select.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action button */}
          <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'center' }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
              <Scissors size={15} strokeWidth={2} style={{ color: 'var(--btn-primary-text)' }} />
              <PrimaryButton
                label="Split PDF"
                onClick={startProcessing}
              />
            </div>
          </div>
        </>
      )}

      {/* ── Step 2: Processing ─────────────────────────────────── */}
      {step === 2 && (
        <>
          <div style={{ marginBottom: '40px' }}>
            <StepIndicator steps={STEPS.map((s) => ({ label: s }))} currentStep={2} />
          </div>

          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '64px 24px',
            textAlign: 'center',
          }}>
            <Loader2
              size={40}
              style={{ color: 'var(--primary)', marginBottom: '20px' }}
              strokeWidth={1.5}
              className="animate-spin"
            />
            <p style={{
              fontSize: '16px',
              fontWeight: 500,
              color: 'var(--text-primary)',
              margin: '0 0 8px 0',
            }}>
              Splitting your PDF...
            </p>
            <p style={{
              fontSize: '13px',
              color: 'var(--text-muted)',
              margin: '0 0 24px 0',
            }}>
              Please wait while we process your document
            </p>

            {/* Progress bar */}
            <div style={{
              width: '100%',
              maxWidth: '320px',
              height: '6px',
              backgroundColor: 'var(--bg-input-placeholder)',
              borderRadius: '3px',
              overflow: 'hidden',
            }}>
              <div style={{
                height: '100%',
                width: `${progress}%`,
                backgroundColor: 'var(--primary)',
                borderRadius: '3px',
                transition: 'width 0.1s linear',
              }} />
            </div>
            <p style={{
              fontSize: '12px',
              color: 'var(--text-muted)',
              marginTop: '8px',
            }}>
              {progress}%
            </p>
          </div>
        </>
      )}

      {/* ── Step 3: Complete ───────────────────────────────────── */}
      {step === 3 && (
        <>
          <div style={{ marginBottom: '40px' }}>
            <StepIndicator steps={STEPS.map((s) => ({ label: s }))} currentStep={3} />
          </div>

          <div style={{
            backgroundColor: 'var(--success-bg)',
            border: '1px solid var(--border)',
            borderRadius: '12px',
            padding: '32px 24px',
            textAlign: 'center',
          }}>
            {/* Success icon */}
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              backgroundColor: 'var(--success)',
              marginBottom: '16px',
            }}>
              <Check size={28} style={{ color: 'var(--btn-primary-text)' }} strokeWidth={2.5} />
            </div>

            <h2 style={{
              fontSize: '18px',
              fontWeight: 600,
              color: 'var(--text-primary)',
              margin: '0 0 4px 0',
            }}>
              Split Complete
            </h2>
            <p style={{
              fontSize: '14px',
              color: 'var(--text-secondary)',
              margin: '0 0 24px 0',
            }}>
              {resultCount} document{resultCount !== 1 ? 's' : ''} created
            </p>

            {/* Result file list */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              marginBottom: '24px',
            }}>
              {Array.from({ length: resultCount }).map((_, i) => (
                <div
                  key={i}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px 16px',
                    backgroundColor: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                  }}
                >
                  <FileText size={16} style={{ color: 'var(--primary-text)', flexShrink: 0 }} strokeWidth={1.5} />
                  <span style={{
                    flex: 1,
                    fontSize: '13px',
                    color: 'var(--text-primary)',
                    textAlign: 'left',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}>
                    document_part_{i + 1}.pdf
                  </span>
                  <button
                    type="button"
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '5px 12px',
                      fontSize: '11px',
                      fontWeight: 500,
                      color: 'var(--btn-primary-text)',
                      backgroundColor: 'var(--btn-primary)',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      transition: 'background-color 0.15s ease',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--btn-primary-hover)' }}
                    onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--btn-primary)' }}
                  >
                    <Download size={12} />
                    Download
                  </button>
                </div>
              ))}
            </div>

            {/* Action buttons */}
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '12px',
            }}>
              <PrimaryButton label="Split Another" onClick={resetAll} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
