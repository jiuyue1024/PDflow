import { FileText, X } from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

export interface FileItem {
  id: string
  name: string
  size?: number
  /** Page count for PDFs */
  pages?: number
}

interface FileListProps {
  files: FileItem[]
  onRemove?: (id: string) => void
  /** Show drag handle for reordering */
  draggable?: boolean
  /** Custom empty message */
  emptyMessage?: string
  /** Icon override */
  icon?: LucideIcon
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

export default function FileList({
  files,
  onRemove,
  emptyMessage = 'No files selected',
  icon: FileIcon,
}: FileListProps) {
  const Icon = FileIcon || FileText

  if (files.length === 0) {
    return (
      <div style={{
        padding: '32px 16px',
        textAlign: 'center',
        fontSize: '13px',
        color: 'var(--text-muted)',
      }}>
        {emptyMessage}
      </div>
    )
  }

  return (
    <div style={{
      backgroundColor: 'var(--bg-card)',
      borderColor: 'var(--border)',
      borderWidth: '1px',
      borderStyle: 'solid',
      borderRadius: '12px',
      overflow: 'hidden',
    }}>
      {files.map((file, index) => (
        <div key={file.id} style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '10px 16px',
          borderBottom: index < files.length - 1 ? '1px solid var(--border)' : 'none',
          backgroundColor: 'var(--bg-card)',
        }}>
          <Icon size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} strokeWidth={1.5} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <p style={{
              fontSize: '13px',
              fontWeight: 500,
              color: 'var(--text-primary)',
              margin: 0,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {file.name}
            </p>
            <div style={{ display: 'flex', gap: '8px', marginTop: '2px' }}>
              {file.size && (
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {formatSize(file.size)}
                </span>
              )}
              {file.pages && (
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {file.pages} page{file.pages > 1 ? 's' : ''}
                </span>
              )}
            </div>
          </div>
          {onRemove && (
            <button
              onClick={() => onRemove(file.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: '24px',
                height: '24px',
                borderRadius: '6px',
                border: 'none',
                backgroundColor: 'transparent',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                transition: 'background-color 0.15s ease, color 0.15s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--error-bg)'
                e.currentTarget.style.color = 'var(--error)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent'
                e.currentTarget.style.color = 'var(--text-muted)'
              }}
            >
              <X size={14} />
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
