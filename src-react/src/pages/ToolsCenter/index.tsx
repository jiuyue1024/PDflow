import { useState, useCallback } from 'react'
import {
  Combine,
  Scissors,
  Minimize2,
  Search,
  UploadCloud,
  Download,
  Check,
  Loader2,
  FileText,
  Plus,
  Zap,
  Droplets,
} from 'lucide-react'

import PageHeader from '../../design-system-v1.3/components/PageHeader'
import StepIndicator from '../../design-system-v1.3/components/StepIndicator'
import UploadZone from '../../design-system-v1.3/components/UploadZone'
import FileList from '../../design-system-v1.3/components/FileList'
import type { FileItem } from '../../design-system-v1.3/components/FileList'
import PrimaryButton from '../../design-system-v1.3/components/PrimaryButton'
import EmptyState from '../../design-system-v1.3/components/EmptyState'
import ActionCard from '../../design-system-v1.3/components/ActionCard'

type ToolId = 'merge' | 'split' | 'optimize'

interface ToolDef {
  id: ToolId | string
  title: string
  description: string
  icon: typeof Combine
  color: string
  external?: boolean
}

const tools: ToolDef[] = [
  { id: 'merge', title: 'Merge', description: 'Combine multiple PDFs into one', icon: Combine, color: '#4F8CFF' },
  { id: 'split', title: 'Split', description: 'Extract pages from a document', icon: Scissors, color: '#22C55E' },
  { id: 'optimize', title: 'Optimize', description: 'Reduce file size with smart compression', icon: Minimize2, color: '#F59E0B' },
  { id: 'watermark', title: 'Watermark', description: 'Add text, image or pattern watermarks', icon: Droplets, color: '#A855F7', external: true },
]

const steps = [
  { label: 'Choose Action' },
  { label: 'Upload Files' },
  { label: 'Configure' },
  { label: 'Start Processing' },
  { label: 'Download Results' },
]

interface UploadedFile {
  name: string
  size: string
}

interface ToolsCenterProps {
  initialTool?: ToolId
  onNavigate?: (itemId: string) => void
}

export default function ToolsCenter({ initialTool, onNavigate }: ToolsCenterProps) {
  const [activeTool, setActiveTool] = useState<ToolId | null>(initialTool || null)
  const [step, setStep] = useState(0)
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDone, setIsDone] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [browseHovered, setBrowseHovered] = useState(false)
  const [downloadHovered, setDownloadHovered] = useState(false)
  const [ctaHovered, setCtaHovered] = useState(false)

  // Tool-specific config
  const [mergeOutputName, setMergeOutputName] = useState('merged_document')
  const [splitRange, setSplitRange] = useState('1-3, 5-10')
  const [splitMode, setSplitMode] = useState<'range' | 'every' | 'extract'>('range')
  const [splitEvery, setSplitEvery] = useState(5)
  const [optimizePreset, setOptimizePreset] = useState<'low' | 'balanced' | 'maximum'>('balanced')
  const currentStep = activeTool ? Math.min(step, 1) : 0

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const newFiles: UploadedFile[] = Array.from(e.dataTransfer.files).map((f) => ({
      name: f.name,
      size: `${(f.size / 1024).toFixed(0)} KB`,
    }))
    if (newFiles.length) {
      setFiles((prev) => [...prev, ...newFiles])
      setStep(2)
    }
  }, [])

  const handleBrowse = () => {
    const newFile: UploadedFile = {
      name: `document_${files.length + 1}.pdf`,
      size: `${(Math.random() * 5 + 0.5).toFixed(1)} MB`,
    }
    setFiles((prev) => [...prev, newFile])
    setStep(2)
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
    if (files.length <= 1) {
      setStep(1)
    }
  }

  const startProcessing = () => {
    setStep(3)
    setIsProcessing(true)
    setTimeout(() => {
      setIsProcessing(false)
      setStep(4)
      setIsDone(true)
    }, 2500)
  }

  const reset = () => {
    setActiveTool(initialTool || null)
    setStep(0)
    setFiles([])
    setIsDone(false)
    setIsProcessing(false)
  }

  const selectTool = (tool: ToolDef) => {
    setActiveTool(tool.id as ToolId)
    setStep(1)
    setFiles([])
    setIsDone(false)
    setIsProcessing(false)
  }

  const activeToolDef = tools.find((t) => t.id === activeTool)
  const ActiveIcon = activeToolDef?.icon || Combine

  // Convert UploadedFile[] to FileItem[] for FileList component
  const fileItems: FileItem[] = files.map((f, i) => ({
    id: `file-${i}`,
    name: f.name,
    // FileList expects size in bytes; parse the mock string back to approximate bytes
    size: f.size.includes('MB')
      ? parseFloat(f.size) * 1024 * 1024
      : f.size.includes('KB')
        ? parseFloat(f.size) * 1024
        : 0,
  }))

  return (
    <div style={{ maxWidth: '56rem', marginLeft: 'auto', marginRight: 'auto', paddingLeft: '2rem', paddingRight: '2rem', paddingTop: '1.5rem', paddingBottom: '1.5rem', display: 'flex', flexDirection: 'column' }}>
      {/* Header — PageHeader */}
      <PageHeader
        title="Tools Center"
        subtitle="Process, organize and optimize documents"
        actions={
          <div style={{ position: 'relative', width: '256px', flexShrink: 0 }}>
            <Search
              size={16}
              style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }}
            />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search actions..."
              style={{
                height: '36px',
                width: '100%',
                borderRadius: '8px',
                border: 'none',
                paddingLeft: '40px',
                paddingRight: '16px',
                fontSize: '13px',
                outline: 'none',
                backgroundColor: 'var(--bg-input-placeholder)',
                color: 'var(--text-primary)',
                boxSizing: 'border-box',
              }}
            />
          </div>
        }
      />

      {/* Tool Cards — ActionCard */}
      <div style={{ marginBottom: '24px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        {tools
          .filter((t) => !searchQuery || t.title.toLowerCase().includes(searchQuery.toLowerCase()))
          .map((tool) => {
            const isActive = activeTool === tool.id
            return (
              <ActionCard
                key={tool.id}
                icon={tool.icon}
                title={tool.title}
                description={tool.description}
                iconColor={tool.color}
                active={isActive}
                showArrow={isActive}
                onClick={() => tool.external ? onNavigate?.(tool.id) : selectTool(tool)}
              />
            )
          })}
      </div>

      {/* Workflow Stepper + Active Area */}
      {activeTool && (
        <div
          style={{
            borderRadius: '12px',
            border: '1px solid var(--border)',
            padding: '24px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
            backgroundColor: 'var(--bg-card)',
          }}
        >
          {/* Stepper — StepIndicator */}
          <div style={{ marginBottom: '24px' }}>
            <StepIndicator steps={steps} currentStep={currentStep} />
          </div>

          {/* Step Content */}
          {step === 1 && (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: '12px',
                border: '2px dashed var(--border)',
                borderWidth: '2px',
                borderStyle: 'dashed',
                transition: 'border-color 0.2s ease, background-color 0.2s ease',
                ...(dragOver
                  ? { borderColor: 'var(--primary)', backgroundColor: 'var(--bg-active)', minHeight: 200 }
                  : { borderColor: 'var(--border)', backgroundColor: 'var(--bg-app)', minHeight: 200 }),
              }}
            >
              <UploadCloud size={40} strokeWidth={1.2} style={{ marginBottom: '12px', transition: 'color 0.2s ease', color: dragOver ? 'var(--primary-text)' : 'var(--text-muted)' }} />
              <p style={{ marginBottom: '4px', fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)' }}>Drag & drop your files here</p>
              <p style={{ marginBottom: '16px', fontSize: '12px', color: 'var(--text-muted)' }}>PDF files only. Max 50MB per file.</p>
              <button
                type="button"
                onClick={handleBrowse}
                onMouseEnter={() => setBrowseHovered(true)}
                onMouseLeave={() => setBrowseHovered(false)}
                style={{
                  borderRadius: '8px',
                  border: 'none',
                  padding: '10px 16px',
                  fontSize: '13px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'background-color 0.15s ease',
                  backgroundColor: browseHovered ? 'var(--btn-primary-hover)' : 'var(--btn-primary)',
                  color: 'var(--btn-primary-text)',
                }}
              >
                Browse Files
              </button>
            </div>
          )}

          {/* Step 2: Configure */}
          {step === 2 && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* Left: File List */}
              <div
                style={{
                  borderRadius: '12px',
                  border: '1px solid var(--border)',
                  padding: '16px',
                  backgroundColor: 'var(--bg-app)',
                }}
              >
                <h4 style={{ marginBottom: '12px', fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Uploaded Files ({files.length})
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <FileList
                    files={fileItems}
                    onRemove={(id) => {
                      const index = parseInt(id.replace('file-', ''), 10)
                      removeFile(index)
                    }}
                  />
                  <button
                    type="button"
                    onClick={handleBrowse}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      cursor: 'pointer',
                      borderRadius: '8px',
                      border: '1px dashed var(--border)',
                      borderStyle: 'dashed',
                      padding: '8px',
                      fontSize: '12px',
                      transition: 'opacity 0.15s ease',
                      backgroundColor: 'transparent',
                      color: 'var(--text-secondary)',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.8' }}
                    onMouseLeave={(e) => { e.currentTarget.style.opacity = '1' }}
                  >
                    <Plus size={14} />
                    Add file
                  </button>
                </div>
              </div>

              {/* Right: Tool-specific config */}
              <div
                style={{
                  borderRadius: '12px',
                  border: '1px solid var(--border)',
                  padding: '16px',
                  backgroundColor: 'var(--bg-app)',
                }}
              >
                <h4 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  <ActiveIcon size={14} style={{ color: activeToolDef?.color }} strokeWidth={1.8} />
                  {activeToolDef?.title} Settings
                </h4>

                {activeTool === 'merge' && (
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Output File Name</label>
                    <input
                      type="text"
                      value={mergeOutputName}
                      onChange={(e) => setMergeOutputName(e.target.value)}
                      style={{
                        marginBottom: '12px',
                        height: '36px',
                        width: '100%',
                        borderRadius: '8px',
                        border: '1px solid var(--border)',
                        backgroundColor: 'var(--bg-card)',
                        paddingLeft: '12px',
                        paddingRight: '12px',
                        fontSize: '13px',
                        outline: 'none',
                        color: 'var(--text-primary)',
                        boxSizing: 'border-box',
                      }}
                    />
                    <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Drag files to reorder merge sequence</p>
                  </div>
                )}

                {activeTool === 'split' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      {(['range', 'every', 'extract'] as const).map((mode) => (
                        <button
                          key={mode}
                          onClick={() => setSplitMode(mode)}
                          style={{
                            flex: 1,
                            cursor: 'pointer',
                            borderRadius: '8px',
                            border: '1px solid var(--border)',
                            padding: '8px',
                            fontSize: '12px',
                            fontWeight: 500,
                            textTransform: 'capitalize',
                            transition: 'border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease',
                            ...(splitMode === mode
                              ? { borderColor: 'var(--primary)', backgroundColor: 'var(--bg-active)', color: 'var(--primary-text)' }
                              : { borderColor: 'var(--border)', backgroundColor: 'transparent', color: 'var(--text-secondary)' }),
                          }}
                        >
                          {mode}
                        </button>
                      ))}
                    </div>
                    {splitMode === 'range' && (
                      <div>
                        <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Page Range</label>
                        <input
                          type="text"
                          value={splitRange}
                          onChange={(e) => setSplitRange(e.target.value)}
                          placeholder="e.g. 1-3, 5-10"
                          style={{
                            height: '36px',
                            width: '100%',
                            borderRadius: '8px',
                            border: '1px solid var(--border)',
                            backgroundColor: 'var(--bg-card)',
                            paddingLeft: '12px',
                            paddingRight: '12px',
                            fontSize: '13px',
                            outline: 'none',
                            color: 'var(--text-primary)',
                            boxSizing: 'border-box',
                          }}
                        />
                      </div>
                    )}
                    {splitMode === 'every' && (
                      <div>
                        <label style={{ display: 'block', marginBottom: '6px', fontSize: '12px', color: 'var(--text-secondary)' }}>Split every N pages</label>
                        <input
                          type="number"
                          value={splitEvery}
                          onChange={(e) => setSplitEvery(Number(e.target.value))}
                          min={1}
                          style={{
                            height: '36px',
                            width: '100%',
                            borderRadius: '8px',
                            border: '1px solid var(--border)',
                            backgroundColor: 'var(--bg-card)',
                            paddingLeft: '12px',
                            paddingRight: '12px',
                            fontSize: '13px',
                            outline: 'none',
                            color: 'var(--text-primary)',
                            boxSizing: 'border-box',
                          }}
                        />
                      </div>
                    )}
                    {splitMode === 'extract' && (
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Select pages to extract from preview</p>
                    )}
                  </div>
                )}

                {activeTool === 'optimize' && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {(['low', 'balanced', 'maximum'] as const).map((preset) => (
                      <button
                        key={preset}
                        onClick={() => setOptimizePreset(preset)}
                        style={{
                          display: 'flex',
                          cursor: 'pointer',
                          alignItems: 'center',
                          gap: '12px',
                          borderRadius: '8px',
                          border: '1px solid var(--border)',
                          padding: '12px',
                          textAlign: 'left',
                          transition: 'border-color 0.15s ease, background-color 0.15s ease',
                          ...(optimizePreset === preset
                            ? { borderColor: 'var(--primary)', backgroundColor: 'var(--bg-active)' }
                            : { borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }),
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '32px', height: '32px', borderRadius: '8px', backgroundColor: 'var(--bg-card)' }}>
                          <Zap size={14} strokeWidth={1.8} style={{ color: optimizePreset === preset ? 'var(--primary-text)' : 'var(--text-muted)' }} />
                        </div>
                        <div>
                          <p style={{ fontSize: '12px', fontWeight: 500, color: optimizePreset === preset ? 'var(--primary-text)' : 'var(--text-primary)' }}>
                            {preset === 'low' ? 'Low Compression' : preset === 'balanced' ? 'Balanced' : 'Maximum Compression'}
                          </p>
                          <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            {preset === 'low' ? '~20% size reduction' : preset === 'balanced' ? '~50% size reduction' : '~70% size reduction'}
                          </p>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

              </div>
            </div>
          )}

          {/* Step 3: Processing */}
          {(step === 3 || (isProcessing && step < 4)) && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '32px 0' }}>
              <Loader2 size={32} className="animate-spin" style={{ color: 'var(--primary-text)' }} />
              <p style={{ marginTop: '16px', fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)' }}>Processing...</p>
              <p style={{ marginTop: '4px', fontSize: '12px', color: 'var(--text-muted)' }}>
                {(() => {
                  const msgs = ['Uploading files...', 'Parsing content...', 'Applying changes...', 'Saving results...']
                  return msgs[Math.floor(Math.random() * 2)]
                })()}
              </p>
              <div style={{ marginTop: '24px', height: '6px', width: '256px', borderRadius: '9999px', backgroundColor: 'var(--bg-input-placeholder)' }}>
                <div className="h-1.5 rounded-full animate-pulse" style={{ width: '60%', height: '6px', borderRadius: '9999px', backgroundColor: 'var(--primary)' }} />
              </div>
            </div>
          )}

          {/* Step 4: Done */}
          {step === 4 && isDone && (
            <div
              style={{
                borderRadius: '12px',
                border: '1px solid rgba(34, 197, 94, 0.2)',
                padding: '24px',
                backgroundColor: 'var(--success-bg)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '40px', height: '40px', borderRadius: '9999px', backgroundColor: 'var(--success-bg)' }}>
                  <Check size={20} style={{ color: 'var(--success)' }} />
                </div>
                <div>
                  <p style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {activeToolDef?.title} Complete
                  </p>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                    {files.length} file{files.length !== 1 ? 's' : ''} processed successfully
                  </p>
                </div>
              </div>
              <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
                <PrimaryButton
                  label="Download"
                  block
                  style={{ flex: 1 }}
                >
                  <Download size={15} />
                </PrimaryButton>
                <button
                  onClick={reset}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    cursor: 'pointer',
                    borderRadius: '8px',
                    border: 'none',
                    padding: '12px 16px',
                    fontSize: '13px',
                    fontWeight: 500,
                    transition: 'opacity 0.15s ease',
                    backgroundColor: 'var(--bg-input-placeholder)',
                    color: 'var(--text-secondary)',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.8' }}
                  onMouseLeave={(e) => { e.currentTarget.style.opacity = '1' }}
                >
                  Process Another
                </button>
              </div>
            </div>
          )}

          {/* CTA Button — only show in step 2 */}
          {step === 2 && (
            <div style={{ marginTop: '20px' }}>
              <button
                type="button"
                onClick={startProcessing}
                onMouseEnter={() => setCtaHovered(true)}
                onMouseLeave={() => setCtaHovered(false)}
                style={{
                  display: 'flex',
                  width: '100%',
                  cursor: 'pointer',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  borderRadius: '12px',
                  border: 'none',
                  padding: '12px 16px',
                  fontSize: '13px',
                  fontWeight: 500,
                  transition: 'background-color 0.2s ease',
                  backgroundColor: ctaHovered ? 'var(--btn-primary-hover)' : 'var(--btn-primary)',
                  color: 'var(--btn-primary-text)',
                  boxSizing: 'border-box',
                }}
              >
                <ActiveIcon size={16} strokeWidth={1.8} />
                {activeToolDef?.title === 'merge' && 'Merge PDF'}
                {activeToolDef?.title === 'split' && 'Start Split'}
                {activeToolDef?.title === 'optimize' && 'Optimize PDF'}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
