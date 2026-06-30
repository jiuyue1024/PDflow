import { useState, useCallback } from 'react'
import {
  Combine,
  UploadCloud,
  FileText,
  GripVertical,
  Trash2,
  Check,
  Loader2,
  Download,
  Plus,
  ArrowUpDown,
} from 'lucide-react'
import PageHeader from '../../design-system-v1.3/components/PageHeader'
import StepIndicator from '../../design-system-v1.3/components/StepIndicator'
import UploadZone from '../../design-system-v1.3/components/UploadZone'
import FileList, { type FileItem } from '../../design-system-v1.3/components/FileList'
import PrimaryButton from '../../design-system-v1.3/components/PrimaryButton'
import EmptyState from '../../design-system-v1.3/components/EmptyState'
import StatusBadge from '../../design-system-v1.3/components/StatusBadge'
import ActionCard from '../../design-system-v1.3/components/ActionCard'

const STEPS = [
  { label: 'Upload Files' },
  { label: 'Configure' },
  { label: 'Processing' },
  { label: 'Complete' },
]

function randomSize(): number {
  return Math.round((Math.random() * 4.5 + 0.5) * 100) / 100 // 0.5 ~ 5.0 MB
}

export default function MergePage() {
  const [step, setStep] = useState(0)
  const [files, setFiles] = useState<FileItem[]>([])
  const [outputName, setOutputName] = useState('merged_document')
  const [isProcessing, setIsProcessing] = useState(false)

  const handleBrowse = useCallback(() => {
    const count = files.length + 1
    const newFile: FileItem = {
      id: crypto.randomUUID(),
      name: `document_${count}.pdf`,
      size: Math.round(randomSize() * 1024 * 1024), // bytes
    }
    setFiles((prev) => [...prev, newFile])
    if (step === 0) setStep(1)
  }, [files.length, step])

  const handleUploadZoneFiles = useCallback(() => {
    handleBrowse()
  }, [handleBrowse])

  const removeFile = useCallback((id: string) => {
    setFiles((prev) => {
      const next = prev.filter((f) => f.id !== id)
      if (next.length === 0) {
        setStep(0)
      }
      return next
    })
  }, [])

  const startProcessing = useCallback(() => {
    if (files.length < 2) return
    setStep(2)
    setIsProcessing(true)
    setTimeout(() => {
      setIsProcessing(false)
      setStep(3)
    }, 2500)
  }, [files.length])

  const reset = useCallback(() => {
    setStep(0)
    setFiles([])
    setOutputName('merged_document')
    setIsProcessing(false)
  }, [])

  // ─── Step 0: Upload ─────────────────────────────────────────
  if (step === 0) {
    return (
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 32px' }}>
        <PageHeader
          title="Merge PDF"
          subtitle="Combine multiple PDF files into a single document"
        />

        {/* ActionCard grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: 16,
          marginBottom: 24,
        }}>
          <ActionCard
            icon={Combine}
            title="Merge All Pages"
            description="Combine every page from all uploaded PDFs into one document"
            iconColor="var(--primary)"
            active
          />
        </div>

        {/* Upload zone */}
        <UploadZone
          files={[]}
          onFilesChange={handleUploadZoneFiles}
          acceptLabel="PDF files only"
          maxSizeLabel="Max 50MB per file"
          multiple
        />
      </div>
    )
  }

  // ─── Step 2: Processing ─────────────────────────────────────
  if (step === 2) {
    return (
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 32px' }}>
        <div style={{ marginBottom: 32 }}>
          <StepIndicator steps={STEPS} currentStep={2} />
        </div>

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '80px 24px',
        }}>
          <Loader2
            size={40}
            style={{ color: 'var(--primary)', marginBottom: 20 }}
            strokeWidth={1.5}
            className="animate-spin"
          />
          <p style={{
            fontSize: 16,
            fontWeight: 500,
            color: 'var(--text-primary)',
            margin: '0 0 16px 0',
          }}>
            Merging your PDFs...
          </p>

          {/* Progress bar */}
          <div style={{
            width: '100%',
            maxWidth: 400,
            height: 6,
            borderRadius: 3,
            backgroundColor: 'var(--bg-hover)',
            overflow: 'hidden',
          }}>
            <div style={{
              width: '60%',
              height: '100%',
              borderRadius: 3,
              backgroundColor: 'var(--primary)',
              animation: 'merge-progress 2.5s ease-in-out',
            }} />
          </div>
          <style>{`
            @keyframes merge-progress {
              0% { width: 0%; }
              80% { width: 85%; }
              100% { width: 100%; }
            }
          `}</style>

          <p style={{
            fontSize: 13,
            color: 'var(--text-muted)',
            marginTop: 12,
          }}>
            Processing {files.length} files...
          </p>
        </div>
      </div>
    )
  }

  // ─── Step 3: Complete ───────────────────────────────────────
  if (step === 3) {
    return (
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 32px' }}>
        <div style={{ marginBottom: 32 }}>
          <StepIndicator steps={STEPS} currentStep={3} />
        </div>

        {/* Success card */}
        <div style={{
          backgroundColor: 'var(--success-bg)',
          borderColor: 'rgba(34, 197, 94, 0.2)',
          borderWidth: 1,
          borderStyle: 'solid',
          borderRadius: 12,
          padding: '32px',
        }}>
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}>
            {/* Check icon circle */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: 56,
              height: 56,
              borderRadius: '50%',
              backgroundColor: 'var(--success-bg)',
              marginBottom: 16,
            }}>
              <Check size={28} style={{ color: 'var(--success)' }} strokeWidth={2} />
            </div>

            <p style={{
              fontSize: 18,
              fontWeight: 600,
              color: 'var(--text-primary)',
              margin: '0 0 6px 0',
            }}>
              Merge Complete
            </p>
            <p style={{
              fontSize: 14,
              color: 'var(--text-secondary)',
              margin: '0 0 24px 0',
            }}>
              {files.length} files merged successfully
            </p>

            {/* Output file info */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '12px 20px',
              borderRadius: 10,
              backgroundColor: 'var(--bg-card)',
              borderColor: 'var(--border)',
              borderWidth: 1,
              borderStyle: 'solid',
              marginBottom: 24,
            }}>
              <FileText size={18} style={{ color: 'var(--primary)', flexShrink: 0 }} strokeWidth={1.5} />
              <span style={{
                fontSize: 13,
                fontWeight: 500,
                color: 'var(--text-primary)',
              }}>
                {outputName}.pdf
              </span>
              <StatusBadge label="Ready" variant="success" />
            </div>

            {/* Action buttons */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 12,
            }}>
              <PrimaryButton
                label="Download"
                size="md"
                style={{ width: 'auto' }}
              >
                <Download size={16} />
                {''}
              </PrimaryButton>
              <button
                onClick={reset}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 6,
                  padding: '10px 20px',
                  height: 36,
                  borderRadius: 8,
                  border: '1px solid var(--border)',
                  borderStyle: 'solid',
                  backgroundColor: 'var(--bg-card)',
                  color: 'var(--text-secondary)',
                  fontSize: 13,
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'background-color 0.15s ease, border-color 0.15s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
                  e.currentTarget.style.borderColor = 'var(--border-strong)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--bg-card)'
                  e.currentTarget.style.borderColor = 'var(--border)'
                }}
              >
                Merge Another
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ─── Step 1: Configure ──────────────────────────────────────
  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '24px 32px' }}>
      <div style={{ marginBottom: 32 }}>
        <StepIndicator steps={STEPS} currentStep={1} />
      </div>

      {/* Two-column layout */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 24,
        marginBottom: 24,
      }}>
        {/* Left column: File list */}
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: 12,
          }}>
            <h3 style={{
              fontSize: 14,
              fontWeight: 600,
              color: 'var(--text-primary)',
              margin: 0,
              display: 'flex',
              alignItems: 'center',
              gap: 8,
            }}>
              <ArrowUpDown size={16} style={{ color: 'var(--text-muted)' }} strokeWidth={1.5} />
              Uploaded Files
            </h3>
            <span style={{
              fontSize: 12,
              color: 'var(--text-muted)',
            }}>
              {files.length} file{files.length !== 1 ? 's' : ''}
            </span>
          </div>

          <FileList
            files={files}
            onRemove={removeFile}
            draggable
            emptyMessage="No files uploaded yet"
          />

          {/* Add more files button */}
          <button
            onClick={handleBrowse}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              marginTop: 12,
              padding: '8px 16px',
              border: '1px dashed var(--border)',
              borderStyle: 'dashed',
              borderRadius: 8,
              backgroundColor: 'transparent',
              color: 'var(--primary)',
              fontSize: 13,
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background-color 0.15s ease, border-color 0.15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--bg-hover)'
              e.currentTarget.style.borderColor = 'var(--primary)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent'
              e.currentTarget.style.borderColor = 'var(--border)'
            }}
          >
            <Plus size={14} strokeWidth={2} />
            Add more files
          </button>
        </div>

        {/* Right column: Configuration */}
        <div style={{
          backgroundColor: 'var(--bg-card)',
          borderColor: 'var(--border)',
          borderWidth: 1,
          borderStyle: 'solid',
          borderRadius: 12,
          padding: '20px',
        }}>
          <h3 style={{
            fontSize: 14,
            fontWeight: 600,
            color: 'var(--text-primary)',
            margin: '0 0 16px 0',
          }}>
            Configuration
          </h3>

          {/* Output file name */}
          <div style={{ marginBottom: 16 }}>
            <label style={{
              display: 'block',
              fontSize: 12,
              fontWeight: 500,
              color: 'var(--text-secondary)',
              marginBottom: 6,
            }}>
              Output File Name
            </label>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 0,
            }}>
              <input
                type="text"
                value={outputName}
                onChange={(e) => setOutputName(e.target.value)}
                style={{
                  flex: 1,
                  height: 36,
                  padding: '0 12px',
                  borderRadius: '8px 0 0 8px',
                  border: '1px solid var(--border)',
                  borderRight: 'none',
                  borderStyle: 'solid',
                  backgroundColor: 'var(--bg-app)',
                  color: 'var(--text-primary)',
                  fontSize: 13,
                  outline: 'none',
                  transition: 'border-color 0.15s ease',
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = 'var(--primary)'
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border)'
                }}
              />
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                height: 36,
                padding: '0 12px',
                borderRadius: '0 8px 8px 0',
                border: '1px solid var(--border)',
                borderStyle: 'solid',
                backgroundColor: 'var(--bg-hover)',
                color: 'var(--text-muted)',
                fontSize: 13,
                flexShrink: 0,
              }}>
                .pdf
              </span>
            </div>
          </div>

          {/* Merge order helper */}
          <div style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: 8,
            padding: '12px 14px',
            borderRadius: 8,
            backgroundColor: 'var(--bg-app)',
            border: '1px solid var(--border)',
            borderStyle: 'solid',
          }}>
            <GripVertical size={16} style={{ color: 'var(--text-muted)', flexShrink: 0, marginTop: 1 }} strokeWidth={1.5} />
            <p style={{
              fontSize: 12,
              color: 'var(--text-muted)',
              margin: 0,
              lineHeight: '18px',
            }}>
              <span style={{ fontWeight: 500, color: 'var(--text-secondary)' }}>Merge Order:</span>{' '}
              Drag to reorder. First file = first pages.
            </p>
          </div>

          {/* Summary */}
          <div style={{
            marginTop: 16,
            padding: '12px 14px',
            borderRadius: 8,
            backgroundColor: 'var(--bg-app)',
            border: '1px solid var(--border)',
            borderStyle: 'solid',
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: 6,
            }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Total files</span>
              <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-primary)' }}>
                {files.length}
              </span>
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
            }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Total size</span>
              <span style={{ fontSize: 12, fontWeight: 500, color: 'var(--text-primary)' }}>
                {(files.reduce((acc, f) => acc + (f.size ?? 0), 0) / (1024 * 1024)).toFixed(1)} MB
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Merge button */}
      <PrimaryButton
        label="Merge PDF"
        size="md"
        onClick={startProcessing}
        disabled={files.length < 2}
        loading={isProcessing}
        style={{ width: '100%' }}
      >
        <Combine size={16} strokeWidth={1.8} />
        {''}
      </PrimaryButton>
    </div>
  )
}
