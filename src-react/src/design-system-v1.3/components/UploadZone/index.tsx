import { useState, type CSSProperties, type DragEvent } from 'react'
import { CloudUpload, FileText } from 'lucide-react'

interface UploadZoneProps {
  /** Currently uploaded files */
  files?: { name: string; size?: number }[]
  /** Called when files are added */
  onFilesChange?: (files: File[]) => void
  /** Accepted formats string shown in helper text */
  acceptLabel?: string
  /** Max file size label */
  maxSizeLabel?: string
  /** Disabled/locked state */
  disabled?: boolean
  /** Multiple files allowed */
  multiple?: boolean
}

export default function UploadZone({
  files = [],
  onFilesChange,
  acceptLabel = 'PDF files only',
  maxSizeLabel = 'Max 50MB per file',
  disabled = false,
  multiple = true,
}: UploadZoneProps) {
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    if (disabled) return
    const dropped = Array.from(e.dataTransfer.files)
    if (dropped.length > 0) onFilesChange?.(dropped)
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (!disabled) setDragOver(true)
  }

  const handleDragLeave = () => setDragOver(false)

  const containerStyle: CSSProperties = {
    backgroundColor: 'var(--bg-card)',
    borderColor: 'var(--border)',
    borderRadius: '12px',
    borderWidth: '1px',
    borderStyle: 'solid',
    padding: '24px',
    opacity: disabled ? 0.6 : 1,
    pointerEvents: disabled ? 'none' : 'auto',
    transition: 'opacity 0.15s ease',
  }

  const dropZoneStyle: CSSProperties = {
    minHeight: '200px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '12px',
    borderWidth: '2px',
    borderStyle: 'dashed',
    borderColor: dragOver ? 'var(--primary)' : 'var(--border)',
    backgroundColor: dragOver ? 'var(--primary-subtle)' : 'var(--bg-input-placeholder)',
    transition: 'border-color 0.15s ease, background-color 0.15s ease',
    cursor: disabled ? 'default' : 'pointer',
  }

  return (
    <div style={containerStyle}>
      {/* Drop zone */}
      <div
        style={dropZoneStyle}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        {files.length > 0 ? (
          <div style={{ width: '100%', padding: '16px' }}>
            {files.map((f, i) => (
              <div key={i} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 0',
                borderBottom: i < files.length - 1 ? '1px solid var(--border)' : 'none',
              }}>
                <FileText size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
                <span style={{
                  fontSize: '13px',
                  color: 'var(--text-primary)',
                  flex: 1,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {f.name}
                </span>
                {f.size && (
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', flexShrink: 0 }}>
                    {(f.size / 1024).toFixed(1)} KB
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <>
            <CloudUpload size={48} style={{ color: 'var(--text-muted)', marginBottom: '12px' }} strokeWidth={1.5} />
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', margin: '0 0 4px 0' }}>
              Drag &amp; drop your files here
            </p>
          </>
        )}
      </div>

      {/* Helper text */}
      <p style={{
        fontSize: '12px',
        color: 'var(--text-muted)',
        textAlign: 'center',
        margin: '12px 0 0 0',
      }}>
        {acceptLabel}. {maxSizeLabel}.
      </p>
    </div>
  )
}
