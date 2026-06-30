import { useState, useCallback } from 'react'
import {
  Minimize2,
  Check,
  Loader2,
  Zap,
  ArrowDown,
} from 'lucide-react'
import PageHeader from '../../design-system-v1.3/components/PageHeader'
import StepIndicator from '../../design-system-v1.3/components/StepIndicator'
import UploadZone from '../../design-system-v1.3/components/UploadZone'
import FileList from '../../design-system-v1.3/components/FileList'
import type { FileItem } from '../../design-system-v1.3/components/FileList'
import PrimaryButton from '../../design-system-v1.3/components/PrimaryButton'

const STEPS = ['Upload File', 'Choose Preset', 'Processing', 'Complete']

type CompressionPreset = 'low' | 'balanced' | 'maximum'

interface PresetOption {
  id: CompressionPreset
  title: string
  description: string
  reduction: string
}

const PRESETS: PresetOption[] = [
  { id: 'low', title: 'Low Compression', description: 'Best quality', reduction: '~20% size reduction' },
  { id: 'balanced', title: 'Balanced', description: 'Good quality', reduction: '~50% size reduction' },
  { id: 'maximum', title: 'Maximum Compression', description: 'Smallest file', reduction: '~70% size reduction' },
]

export default function OptimizePage() {
  const [step, setStep] = useState(0)
  const [files, setFiles] = useState<FileItem[]>([])
  const [preset, setPreset] = useState<CompressionPreset>('balanced')
  const [isProcessing, setIsProcessing] = useState(false)
  const [originalSize, setOriginalSize] = useState('')
  const [optimizedSize, setOptimizedSize] = useState('')
  const [progress, setProgress] = useState(0)

  const handleFilesChange = useCallback((incoming: File[]) => {
    if (incoming.length === 0) return
    const first = incoming[0]
    const fileItem: FileItem = {
      id: crypto.randomUUID(),
      name: first.name.endsWith('.pdf') ? first.name : 'document.pdf',
      size: first.size,
    }
    setFiles([fileItem])
    setStep(1)
  }, [])

  const handleBrowse = useCallback(() => {
    const mockSize = Math.round(Math.random() * 80 + 5) * 1024 * 1024
    const fileItem: FileItem = {
      id: crypto.randomUUID(),
      name: 'presentation.pdf',
      size: mockSize,
    }
    setFiles([fileItem])
    setOriginalSize(formatFileSize(mockSize))
    setStep(1)
  }, [])

  const startProcessing = useCallback(() => {
    setIsProcessing(true)
    setStep(2)
    setProgress(0)

    const reductionMap: Record<CompressionPreset, number> = {
      low: 0.8,
      balanced: 0.5,
      maximum: 0.3,
    }
    const factor = reductionMap[preset]

    const totalSize = files[0]?.size ?? 10 * 1024 * 1024
    setOriginalSize(formatFileSize(totalSize))

    const newOptimized = Math.round(totalSize * factor)
    setOptimizedSize(formatFileSize(newOptimized))

    let p = 0
    const interval = setInterval(() => {
      p += Math.random() * 18 + 6
      if (p >= 100) {
        p = 100
        clearInterval(interval)
        setTimeout(() => {
          setIsProcessing(false)
          setStep(3)
        }, 300)
      }
      setProgress(Math.min(p, 99))
    }, 250)
  }, [files, preset])

  const handleRemove = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id))
    setStep(0)
    setOriginalSize('')
    setOptimizedSize('')
  }, [])

  const handleReset = useCallback(() => {
    setStep(0)
    setFiles([])
    setPreset('balanced')
    setIsProcessing(false)
    setOriginalSize('')
    setOptimizedSize('')
    setProgress(0)
  }, [])

  return (
    <div style={{
      maxWidth: '960px',
      margin: '0 auto',
      padding: '32px 24px',
    }}>
      {/* Step 0: Upload */}
      {step === 0 && (
        <>
          <PageHeader
            title="Optimize PDF"
            subtitle="Reduce file size with smart compression"
          />
          <UploadZone
            files={[]}
            onFilesChange={handleFilesChange}
            acceptLabel="PDF file only"
            maxSizeLabel="Max 100MB"
            multiple={false}
          />
          <div style={{ marginTop: '20px' }}>
            <PrimaryButton
              label="Browse Files"
              onClick={handleBrowse}
              block
            />
          </div>
        </>
      )}

      {/* Step 1: Configure */}
      {step === 1 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '8px',
          }}>
            <StepIndicator steps={STEPS.map((label) => ({ label }))} currentStep={1} />
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '24px',
            alignItems: 'start',
          }}>
            {/* Left: File List */}
            <div>
              <FileList files={files} onRemove={handleRemove} />
            </div>

            {/* Right: Preset Selection */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '4px',
              }}>
                <Zap size={16} strokeWidth={1.8} style={{ color: 'var(--primary-text)' }} />
                <span style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                }}>
                  Compression Level
                </span>
              </div>

              {PRESETS.map((p) => {
                const isSelected = preset === p.id
                return (
                  <button
                    key={p.id}
                    type="button"
                    onClick={() => setPreset(p.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '14px 16px',
                      borderRadius: '12px',
                      border: `1px solid ${isSelected ? 'var(--primary)' : 'var(--border)'}`,
                      backgroundColor: isSelected ? 'var(--bg-active)' : 'var(--bg-card)',
                      cursor: 'pointer',
                      transition: 'border-color 0.15s ease, background-color 0.15s ease',
                      textAlign: 'left',
                      width: '100%',
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.borderColor = 'var(--primary)'
                        e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) {
                        e.currentTarget.style.borderColor = 'var(--border)'
                        e.currentTarget.style.backgroundColor = 'var(--bg-card)'
                      }
                    }}
                  >
                    <Zap
                      size={20}
                      strokeWidth={1.5}
                      style={{
                        color: isSelected ? 'var(--primary-text)' : 'var(--text-muted)',
                        flexShrink: 0,
                        transition: 'color 0.15s ease',
                      }}
                    />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{
                        fontSize: '13px',
                        fontWeight: 600,
                        color: 'var(--text-primary)',
                        margin: 0,
                        marginBottom: '2px',
                      }}>
                        {p.title}
                      </p>
                      <p style={{
                        fontSize: '11px',
                        color: 'var(--text-secondary)',
                        margin: 0,
                      }}>
                        {p.reduction}, {p.description}
                      </p>
                    </div>
                    <div style={{
                      width: '18px',
                      height: '18px',
                      borderRadius: '50%',
                      border: `2px solid ${isSelected ? 'var(--primary)' : 'var(--border)'}`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      transition: 'border-color 0.15s ease',
                      backgroundColor: isSelected ? 'var(--primary)' : 'transparent',
                    }}>
                      {isSelected && (
                        <div style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          backgroundColor: 'var(--bg-card)',
                        }} />
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          <div>
            <PrimaryButton
              label="Optimize PDF"
              onClick={startProcessing}
              block
            />
          </div>
        </div>
      )}

      {/* Step 2: Processing */}
      {step === 2 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '8px',
          }}>
            <StepIndicator steps={STEPS.map((label) => ({ label }))} currentStep={2} />
          </div>

          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '64px 24px',
            gap: '20px',
          }}>
            <Loader2
              size={40}
              strokeWidth={1.5}
              style={{
                color: 'var(--primary-text)',
                animation: 'spin 1s linear infinite',
              }}
            />
            <p style={{
              fontSize: '15px',
              fontWeight: 500,
              color: 'var(--text-primary)',
              margin: 0,
            }}>
              Optimizing your PDF...
            </p>

            {/* Progress bar */}
            <div style={{
              width: '100%',
              maxWidth: '400px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
            }}>
              <div style={{
                width: '100%',
                height: '6px',
                borderRadius: '3px',
                backgroundColor: 'var(--bg-input-placeholder)',
                overflow: 'hidden',
              }}>
                <div style={{
                  width: `${progress}%`,
                  height: '100%',
                  borderRadius: '3px',
                  backgroundColor: 'var(--primary)',
                  transition: 'width 0.25s ease',
                }} />
              </div>
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '11px',
                color: 'var(--text-muted)',
              }}>
                <span>
                  {progress < 30 ? 'Analyzing PDF structure...' : progress < 60 ? 'Compressing images...' : progress < 90 ? 'Optimizing fonts...' : 'Finalizing...'}
                </span>
                <span>{Math.round(progress)}%</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Complete */}
      {step === 3 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '8px',
          }}>
            <StepIndicator steps={STEPS.map((label) => ({ label }))} currentStep={3} />
          </div>

          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            padding: '48px 24px',
            gap: '24px',
          }}>
            {/* Success card */}
            <div style={{
              width: '100%',
              maxWidth: '480px',
              borderRadius: '12px',
              border: '1px solid var(--border)',
              backgroundColor: 'var(--bg-card)',
              padding: '32px 24px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '16px',
            }}>
              {/* Success icon */}
              <div style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                backgroundColor: 'var(--success-bg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                <Check size={28} style={{ color: 'var(--success)' }} strokeWidth={2} />
              </div>

              <div style={{ textAlign: 'center' }}>
                <p style={{
                  fontSize: '16px',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  margin: 0,
                  marginBottom: '4px',
                }}>
                  Optimization Complete
                </p>
                <p style={{
                  fontSize: '13px',
                  color: 'var(--text-secondary)',
                  margin: 0,
                }}>
                  File size reduced by ~50%
                </p>
              </div>

              {/* Size comparison */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px 20px',
                borderRadius: '10px',
                backgroundColor: 'var(--bg-app)',
                width: '100%',
              }}>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  flex: 1,
                  gap: '4px',
                }}>
                  <span style={{
                    fontSize: '11px',
                    color: 'var(--text-muted)',
                  }}>
                    Original
                  </span>
                  <span style={{
                    fontSize: '18px',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                  }}>
                    {originalSize}
                  </span>
                </div>

                <ArrowDown size={20} style={{ color: 'var(--success)', flexShrink: 0 }} />

                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  flex: 1,
                  gap: '4px',
                }}>
                  <span style={{
                    fontSize: '11px',
                    color: 'var(--text-muted)',
                  }}>
                    Optimized
                  </span>
                  <span style={{
                    fontSize: '18px',
                    fontWeight: 600,
                    color: 'var(--success)',
                  }}>
                    {optimizedSize}
                  </span>
                </div>
              </div>

              {/* Action buttons */}
              <div style={{
                display: 'flex',
                gap: '12px',
                width: '100%',
                marginTop: '8px',
              }}>
                <PrimaryButton
                  label="Download"
                  onClick={() => {/* simulation: no-op */}}
                  block
                />
                <button
                  type="button"
                  onClick={handleReset}
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    padding: '10px 20px',
                    borderRadius: '8px',
                    border: '1px solid var(--border)',
                    backgroundColor: 'var(--bg-hover)',
                    color: 'var(--text-secondary)',
                    fontSize: '13px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--bg-active)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
                  }}
                >
                  <Minimize2 size={14} strokeWidth={1.8} />
                  Optimize Another
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}
