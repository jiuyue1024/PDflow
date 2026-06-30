import { useState, useCallback } from 'react'
import {
  Type,
  ImageIcon,
  Grid3X3,
  Download,
  Check,
  Loader2,
  FileText,
  Droplets,
} from 'lucide-react'

import PageHeader from '../../design-system-v1.3/components/PageHeader'
import StepIndicator from '../../design-system-v1.3/components/StepIndicator'
import UploadZone from '../../design-system-v1.3/components/UploadZone'
import FileList, { type FileItem } from '../../design-system-v1.3/components/FileList'
import PrimaryButton from '../../design-system-v1.3/components/PrimaryButton'
import EmptyState from '../../design-system-v1.3/components/EmptyState'
import SettingsRow from '../../design-system-v1.3/components/SettingsRow'

type WatermarkType = 'text' | 'image' | 'pattern'

type Position =
  | 'top-left' | 'top-center' | 'top-right'
  | 'center-left' | 'center' | 'center-right'
  | 'bottom-left' | 'bottom-center' | 'bottom-right'
  | 'diagonal'

const positions: { id: Position; label: string; row: number; col: number }[] = [
  { id: 'top-left', label: 'TL', row: 0, col: 0 },
  { id: 'top-center', label: 'TC', row: 0, col: 1 },
  { id: 'top-right', label: 'TR', row: 0, col: 2 },
  { id: 'center-left', label: 'CL', row: 1, col: 0 },
  { id: 'center', label: 'C', row: 1, col: 1 },
  { id: 'center-right', label: 'CR', row: 1, col: 2 },
  { id: 'bottom-left', label: 'BL', row: 2, col: 0 },
  { id: 'bottom-center', label: 'BC', row: 2, col: 1 },
  { id: 'bottom-right', label: 'BR', row: 2, col: 2 },
]

interface UploadedFile {
  name: string
  size: string
}

const STEPS = ['Upload File', 'Configure Watermark', 'Processing', 'Complete']

export default function WatermarkPage() {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [watermarkType, setWatermarkType] = useState<WatermarkType>('text')
  const [position, setPosition] = useState<Position>('center')
  const [tileMode, setTileMode] = useState<'off' | 'diagonal' | 'fullpage'>('off')
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDone, setIsDone] = useState(false)

  // Text watermark settings
  const [watermarkText, setWatermarkText] = useState('CONFIDENTIAL')
  const [fontSize, setFontSize] = useState(36)
  const [fontColor, setFontColor] = useState('#000000')
  const [textOpacity, setTextOpacity] = useState(20)

  // Image watermark settings
  const [imageOpacity, setImageOpacity] = useState(30)
  const [imageScale, setImageScale] = useState(50)

  // Global settings
  const [applyMode, setApplyMode] = useState<'over' | 'behind'>('over')
  const [rotation, setRotation] = useState(-30)
  const [scale, setScale] = useState(80)
  const [browseHovered, setBrowseHovered] = useState(false)
  const [downloadHovered, setDownloadHovered] = useState(false)
  const [applyHovered, setApplyHovered] = useState(false)

  const hasFiles = files.length > 0

  // Determine current step based on state
  const currentStep = isDone ? 3 : isProcessing ? 2 : hasFiles ? 1 : 0

  // Bridge: convert native File[] from UploadZone into UploadedFile[]
  const handleFilesChange = useCallback((newFiles: File[]) => {
    const uploaded: UploadedFile[] = newFiles.map((f) => ({
      name: f.name,
      size: `${(f.size / 1024).toFixed(0)} KB`,
    }))
    if (uploaded.length) {
      setFiles((prev) => [...prev, ...uploaded])
      setIsDone(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const newFiles: UploadedFile[] = Array.from(e.dataTransfer.files).map((f) => ({
      name: f.name,
      size: `${(f.size / 1024).toFixed(0)} KB`,
    }))
    if (newFiles.length) {
      setFiles((prev) => [...prev, ...newFiles])
      setIsDone(false)
    }
  }, [])

  const handleBrowse = () => {
    const newFile: UploadedFile = {
      name: 'presentation.pdf',
      size: '3.4 MB',
    }
    setFiles((prev) => [...prev, newFile])
    setIsDone(false)
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleRemoveFile = (id: string) => {
    const index = Number(id)
    if (!Number.isNaN(index)) {
      removeFile(index)
    }
  }

  const applyWatermark = () => {
    setIsProcessing(true)
    setTimeout(() => {
      setIsProcessing(false)
      setIsDone(true)
    }, 2500)
  }

  const reset = () => {
    setFiles([])
    setIsDone(false)
    setWatermarkText('CONFIDENTIAL')
    setPosition('center')
    setTileMode('off')
    setFontSize(36)
    setFontColor('#000000')
    setTextOpacity(20)
    setImageOpacity(30)
    setImageScale(50)
    setApplyMode('over')
    setRotation(-30)
    setScale(80)
  }

  const watermarkTypes: { id: WatermarkType; label: string; icon: typeof Type }[] = [
    { id: 'text', label: 'Text', icon: Type },
    { id: 'image', label: 'Image', icon: ImageIcon },
    { id: 'pattern', label: 'Pattern', icon: Grid3X3 },
  ]

  // Convert internal files to FileItem format for design-system FileList
  const fileListItems: FileItem[] = files.map((f, i) => ({
    id: String(i),
    name: f.name,
  }))

  // Watermark preview style
  const getPreviewWatermarkStyle = () => {
    const base: React.CSSProperties = {
      position: 'absolute' as const,
      color: fontColor,
      opacity: textOpacity / 100,
      fontSize: `${Math.min(fontSize, 28)}px`,
      fontWeight: 600,
      pointerEvents: 'none' as const,
      whiteSpace: 'nowrap' as const,
      transform: `rotate(${rotation}deg)`,
      letterSpacing: '2px',
    }

    if (tileMode !== 'off') {
      return {
        ...base,
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
        fontSize: `${Math.min(fontSize, 20)}px`,
        transform: 'none',
      }
    }

    const positionMap: Record<string, React.CSSProperties> = {
      'top-left': { top: '15%', left: '10%' },
      'top-center': { top: '15%', left: '50%', transform: `translateX(-50%) rotate(${rotation}deg)` },
      'top-right': { top: '15%', right: '10%' },
      'center-left': { top: '50%', left: '10%', transform: `translateY(-50%) rotate(${rotation}deg)` },
      center: { top: '50%', left: '50%', transform: `translate(-50%, -50%) rotate(${rotation}deg)` },
      'center-right': { top: '50%', right: '10%', transform: `translateY(-50%) rotate(${rotation}deg)` },
      'bottom-left': { bottom: '15%', left: '10%' },
      'bottom-center': { bottom: '15%', left: '50%', transform: `translateX(-50%) rotate(${rotation}deg)` },
      'bottom-right': { bottom: '15%', right: '10%' },
    }
    return { ...base, ...positionMap[position] }
  }

  // Reusable card container style
  const cardStyle: React.CSSProperties = {
    backgroundColor: 'var(--bg-card)',
    borderColor: 'var(--border)',
    borderWidth: '1px',
    borderStyle: 'solid',
    borderRadius: '12px',
    padding: '20px',
  }

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', padding: '24px 32px' }}>
      {/* ===== Header ===== */}
      <PageHeader
        title="Watermark"
        subtitle="Add text or image watermarks to your PDF documents"
      />

      {/* ===== Step Indicator ===== */}
      <div style={{ marginBottom: '24px' }}>
        <StepIndicator
          steps={STEPS.map((label) => ({ label }))}
          currentStep={currentStep}
        />
      </div>

      {/* ===== Step 0: Upload File ===== */}
      {currentStep === 0 && (
        <div>
          <UploadZone
            files={[]}
            onFilesChange={handleFilesChange}
            acceptLabel="PDF files only"
            maxSizeLabel="Max 50MB per file. Multi-file support."
            multiple={true}
          />
          <div style={{ marginTop: '16px', textAlign: 'center' }}>
            <PrimaryButton label="Browse Files" onClick={handleBrowse} />
          </div>
        </div>
      )}

      {/* ===== Step 1: Configure Watermark ===== */}
      {currentStep === 1 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* File List */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                Uploaded Files
              </h3>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {files.length} file{files.length !== 1 ? 's' : ''}
              </span>
            </div>
            <FileList files={fileListItems} onRemove={handleRemoveFile} />
            <div style={{ marginTop: '8px' }}>
              <button
                type="button"
                onClick={handleBrowse}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.textDecoration = 'underline' }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.textDecoration = 'none' }}
                style={{
                  fontSize: '12px',
                  color: 'var(--primary-text)',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  padding: 0,
                }}
              >
                + Add more files
              </button>
            </div>
          </div>

          {/* Watermark Type Tabs */}
          <div style={{
            ...cardStyle,
            padding: '4px',
            display: 'flex',
            gap: '4px',
          }}>
            {watermarkTypes.map((type) => {
              const Icon = type.icon
              const isActive = watermarkType === type.id
              return (
                <button
                  key={type.id}
                  onClick={() => setWatermarkType(type.id)}
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    padding: '10px',
                    borderRadius: '8px',
                    fontSize: '13px',
                    fontWeight: 500,
                    cursor: 'pointer',
                    border: 'none',
                    transition: 'background-color 0.15s ease, color 0.15s ease',
                    backgroundColor: isActive ? 'var(--bg-card)' : 'transparent',
                    color: isActive ? 'var(--primary-text)' : 'var(--text-secondary)',
                    boxShadow: isActive ? '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)' : 'none',
                  }}
                >
                  <Icon size={15} strokeWidth={1.8} />
                  <span>{type.label} Watermark</span>
                </button>
              )
            })}
          </div>

          {/* Configuration + Preview side by side */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
          }}>
            {/* Left: Configuration panels */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Text Watermark Config */}
              {watermarkType === 'text' && (
                <div style={cardStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                    <Type size={16} strokeWidth={1.8} style={{ color: 'var(--primary-text)' }} />
                    <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>Text Watermark</h3>
                  </div>

                  {/* Text Input */}
                  <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                      Watermark Text
                    </label>
                    <input
                      type="text"
                      value={watermarkText}
                      onChange={(e) => setWatermarkText(e.target.value)}
                      style={{
                        height: '40px',
                        width: '100%',
                        borderRadius: '8px',
                        border: '1px solid var(--border)',
                        backgroundColor: 'var(--bg-app)',
                        color: 'var(--text-primary)',
                        padding: '0 12px',
                        fontSize: '13px',
                        outline: 'none',
                        boxSizing: 'border-box',
                      }}
                    />
                  </div>

                  {/* Font Size */}
                  <SliderControl label="Font Size" value={fontSize} min={12} max={120} onChange={setFontSize} suffix="px" />

                  {/* Color */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '16px' }}>
                    <div>
                      <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', margin: '0 0 2px 0' }}>Color</p>
                      <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>Watermark text color</p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {['#000000', '#4F8CFF', '#EF4444', '#22C55E'].map((c) => (
                        <button
                          key={c}
                          onClick={() => setFontColor(c)}
                          style={{
                            width: '28px',
                            height: '28px',
                            borderRadius: '50%',
                            border: `2px solid ${fontColor === c ? 'var(--primary)' : 'transparent'}`,
                            backgroundColor: c,
                            cursor: 'pointer',
                            transform: fontColor === c ? 'scale(1.1)' : 'scale(1)',
                            transition: 'transform 0.15s ease',
                            padding: 0,
                          }}
                        />
                      ))}
                    </div>
                  </div>

                  {/* Opacity */}
                  <div style={{ marginTop: '16px' }}>
                    <SliderControl label="Opacity" value={textOpacity} min={0} max={100} onChange={setTextOpacity} suffix="%" />
                  </div>
                </div>
              )}

              {/* Image Watermark Config */}
              {watermarkType === 'image' && (
                <div style={cardStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                    <ImageIcon size={16} strokeWidth={1.8} style={{ color: 'var(--primary-text)' }} />
                    <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>Image Watermark</h3>
                  </div>
                  <EmptyState
                    icon={ImageIcon}
                    title="No image selected"
                    description="Upload a PNG or JPG to use as watermark"
                    action={<PrimaryButton label="Upload Image" size="sm" />}
                  />
                  <div style={{ marginTop: '16px' }}>
                    <SliderControl label="Scale" value={imageScale} min={10} max={100} onChange={setImageScale} suffix="%" />
                  </div>
                  <div style={{ marginTop: '16px' }}>
                    <SliderControl label="Opacity" value={imageOpacity} min={0} max={100} onChange={setImageOpacity} suffix="%" />
                  </div>
                </div>
              )}

              {/* Pattern Watermark Config */}
              {watermarkType === 'pattern' && (
                <div style={cardStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                    <Grid3X3 size={16} strokeWidth={1.8} style={{ color: 'var(--primary-text)' }} />
                    <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>Pattern Watermark</h3>
                  </div>
                  <div style={{ marginBottom: '16px' }}>
                    <label style={{ display: 'block', fontSize: '12px', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                      Pattern Text
                    </label>
                    <input
                      type="text"
                      value={watermarkText}
                      onChange={(e) => setWatermarkText(e.target.value)}
                      style={{
                        height: '40px',
                        width: '100%',
                        borderRadius: '8px',
                        border: '1px solid var(--border)',
                        backgroundColor: 'var(--bg-app)',
                        color: 'var(--text-primary)',
                        padding: '0 12px',
                        fontSize: '13px',
                        outline: 'none',
                        boxSizing: 'border-box',
                      }}
                    />
                  </div>
                  <SliderControl label="Font Size" value={fontSize} min={12} max={120} onChange={setFontSize} suffix="px" />
                  <div style={{ marginTop: '16px' }}>
                    <SliderControl label="Opacity" value={textOpacity} min={0} max={100} onChange={setTextOpacity} suffix="%" />
                  </div>
                </div>
              )}

              {/* Position Grid */}
              <div style={cardStyle}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <Droplets size={16} strokeWidth={1.8} style={{ color: 'var(--primary-text)' }} />
                  <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>Position</h3>
                </div>
                {/* Tile mode selector */}
                <div style={{ display: 'flex', gap: '6px', marginBottom: '12px' }}>
                  {(['off', 'diagonal', 'fullpage'] as const).map((mode) => (
                    <button
                      key={mode}
                      onClick={() => {
                        setTileMode(mode)
                        if (mode !== 'off') setPosition('center')
                      }}
                      style={{
                        flex: 1,
                        padding: '8px',
                        borderRadius: '8px',
                        border: 'none',
                        fontSize: '12px',
                        fontWeight: 500,
                        cursor: 'pointer',
                        transition: 'background-color 0.15s ease',
                        backgroundColor: tileMode === mode ? 'var(--primary)' : 'var(--bg-input-placeholder)',
                        color: tileMode === mode ? 'white' : 'var(--text-secondary)',
                      }}
                    >
                      {mode === 'off' ? 'Single' : mode === 'diagonal' ? 'Diagonal' : 'Full Coverage'}
                    </button>
                  ))}
                </div>
                {tileMode === 'off' ? (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '6px' }}>
                    {positions.map((pos) => (
                      <button
                        key={pos.id}
                        onClick={() => setPosition(pos.id)}
                        style={{
                          height: '40px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          borderRadius: '8px',
                          border: `1px solid ${position === pos.id ? 'var(--primary)' : 'var(--border)'}`,
                          backgroundColor: position === pos.id ? 'var(--bg-active)' : 'var(--bg-app)',
                          color: position === pos.id ? 'var(--primary-text)' : 'var(--text-muted)',
                          fontSize: '12px',
                          fontWeight: 500,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        {pos.label}
                      </button>
                    ))}
                  </div>
                ) : tileMode === 'diagonal' ? (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '8px',
                    border: '2px dashed var(--border-strong)',
                    padding: '24px',
                    backgroundColor: 'var(--bg-app)',
                    color: 'var(--text-secondary)',
                    fontSize: '12px',
                  }}>
                    Diagonal repeat tiling
                  </div>
                ) : (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderRadius: '8px',
                    border: '1px solid rgba(79, 140, 255, 0.2)',
                    padding: '24px',
                    backgroundColor: 'var(--bg-active)',
                    color: 'var(--primary-text)',
                    fontSize: '12px',
                  }}>
                    Full page coverage enabled
                  </div>
                )}
              </div>

              {/* Output Settings */}
              <div style={cardStyle}>
                <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: '0 0 16px 0' }}>Output Settings</h3>
                {/* Apply Mode */}
                <div style={{ marginBottom: '16px' }}>
                  <SettingsRow label="Apply Mode" description="Place watermark over or behind content">
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => setApplyMode('over')}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '8px',
                          border: `1px solid ${applyMode === 'over' ? 'var(--primary)' : 'var(--border)'}`,
                          backgroundColor: applyMode === 'over' ? 'var(--bg-active)' : 'transparent',
                          color: applyMode === 'over' ? 'var(--primary-text)' : 'var(--text-secondary)',
                          fontSize: '12px',
                          fontWeight: 500,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        Over Content
                      </button>
                      <button
                        onClick={() => setApplyMode('behind')}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '8px',
                          border: `1px solid ${applyMode === 'behind' ? 'var(--primary)' : 'var(--border)'}`,
                          backgroundColor: applyMode === 'behind' ? 'var(--bg-active)' : 'transparent',
                          color: applyMode === 'behind' ? 'var(--primary-text)' : 'var(--text-secondary)',
                          fontSize: '12px',
                          fontWeight: 500,
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        Behind Content
                      </button>
                    </div>
                  </SettingsRow>
                </div>
                <SliderControl label="Rotation" value={rotation} min={-180} max={180} onChange={setRotation} suffix="°" />
                <div style={{ marginTop: '16px' }}>
                  <SliderControl label="Scale" value={scale} min={20} max={150} onChange={setScale} suffix="%" />
                </div>
              </div>
            </div>

            {/* Right: Live Preview */}
            <div style={cardStyle}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <FileText size={16} strokeWidth={1.8} style={{ color: 'var(--primary-text)' }} />
                <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>Live Preview</h3>
              </div>
              <div
                style={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                  borderRadius: '8px',
                  aspectRatio: '3/4',
                  border: '1px solid var(--border)',
                  backgroundColor: 'var(--bg-app)',
                }}
              >
                {/* Fake document content — white PDF page stays white */}
                <div style={{ width: '85%', borderRadius: '8px', backgroundColor: 'var(--bg-card)', padding: '16px' }}>
                  <div style={{ height: '12px', width: '75%', borderRadius: '2px', backgroundColor: 'var(--border)', marginBottom: '8px' }} />
                  <div style={{ height: '8px', width: '100%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)', marginBottom: '6px' }} />
                  <div style={{ height: '8px', width: '100%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)', marginBottom: '6px' }} />
                  <div style={{ height: '8px', width: '90%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)', marginBottom: '12px' }} />
                  <div style={{ height: '1px', width: '100%', backgroundColor: 'var(--border)', marginBottom: '12px' }} />
                  <div style={{ height: '8px', width: '100%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)', marginBottom: '6px' }} />
                  <div style={{ height: '8px', width: '100%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)', marginBottom: '6px' }} />
                  <div style={{ height: '8px', width: '80%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)', marginBottom: '12px' }} />
                  <div style={{ height: '1px', width: '100%', backgroundColor: 'var(--border)', marginBottom: '12px' }} />
                  <div style={{ height: '8px', width: '100%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)', marginBottom: '6px' }} />
                  <div style={{ height: '8px', width: '70%', borderRadius: '2px', backgroundColor: 'var(--bg-input-placeholder)' }} />
                </div>

                {/* Watermark Overlay */}
                {tileMode === 'fullpage' ? (
                  /* Full page coverage: dense tiling */
                  <div
                    style={{
                      position: 'absolute',
                      inset: 0,
                      overflow: 'hidden',
                      opacity: textOpacity / 100,
                      transform: `rotate(${rotation}deg)`,
                      transformOrigin: 'center center',
                    }}
                  >
                    {Array.from({ length: 12 }).map((_, i) =>
                      Array.from({ length: 6 }).map((_, j) => (
                        <div
                          key={`${i}-${j}`}
                          style={{
                            position: 'absolute',
                            fontWeight: 600,
                            whiteSpace: 'nowrap',
                            color: fontColor,
                            fontSize: `${Math.min(fontSize, 12)}px`,
                            left: `${j * 20 - 10}%`,
                            top: `${i * 10 - 5}%`,
                          }}
                        >
                          {watermarkText}
                        </div>
                      ))
                    )}
                  </div>
                ) : tileMode === 'diagonal' ? (
                  /* Diagonal: sparse repeat */
                  <div style={{
                    position: 'absolute',
                    inset: 0,
                    overflow: 'hidden',
                    opacity: textOpacity / 100,
                    transform: `rotate(${rotation}deg)`,
                  }}>
                    {Array.from({ length: 6 }).map((_, i) =>
                      Array.from({ length: 4 }).map((_, j) => (
                        <div
                          key={`${i}-${j}`}
                          style={{
                            position: 'absolute',
                            fontSize: '14px',
                            fontWeight: 600,
                            whiteSpace: 'nowrap',
                            color: fontColor,
                            left: `${j * 30 - 10}%`,
                            top: `${i * 25 - 10}%`,
                          }}
                        >
                          {watermarkText}
                        </div>
                      ))
                    )}
                  </div>
                ) : (
                  <div style={getPreviewWatermarkStyle()}>
                    {watermarkText}
                  </div>
                )}
              </div>
              <p style={{ marginTop: '8px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)' }}>
                Preview updates in real-time
              </p>
            </div>
          </div>

          {/* CTA: Apply Watermark */}
          <PrimaryButton
            label="Apply Watermark"
            onClick={applyWatermark}
            disabled={!hasFiles}
          />
        </div>
      )}

      {/* ===== Step 2: Processing ===== */}
      {currentStep === 2 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* File list (read-only) */}
          <div style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                Uploaded Files
              </h3>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {files.length} file{files.length !== 1 ? 's' : ''}
              </span>
            </div>
            <FileList files={fileListItems} />
          </div>

          {/* Processing card */}
          <div style={{
            ...cardStyle,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '32px 24px',
            textAlign: 'center',
          }}>
            <Loader2 size={32} style={{ color: 'var(--primary-text)', marginBottom: '16px' }} className="animate-spin" />
            <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', margin: '0 0 4px 0' }}>
              Applying Watermark...
            </p>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>
              Processing {files.length} file{files.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      )}

      {/* ===== Step 3: Complete ===== */}
      {currentStep === 3 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Success card */}
          <div style={{
            backgroundColor: 'var(--success-bg)',
            borderColor: 'rgba(34, 197, 94, 0.2)',
            borderWidth: '1px',
            borderStyle: 'solid',
            borderRadius: '12px',
            padding: '20px',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                backgroundColor: 'var(--success-bg)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}>
                <Check size={20} style={{ color: 'var(--success)' }} />
              </div>
              <div>
                <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', margin: '0 0 2px 0' }}>Watermark Applied</p>
                <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: 0 }}>
                  {files.length} file{files.length !== 1 ? 's' : ''} ready to download
                </p>
              </div>
            </div>

            {/* Download items */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap' }}>
              {files.map((file, i) => (
                <div key={i} style={{
                  flex: 1,
                  minWidth: '200px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  borderRadius: '8px',
                  border: '1px solid var(--border)',
                  backgroundColor: 'var(--bg-card)',
                  padding: '10px 12px',
                }}>
                  <FileText size={14} style={{ color: 'var(--primary-text)', flexShrink: 0 }} />
                  <span style={{
                    flex: 1,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    fontSize: '12px',
                    color: 'var(--text-primary)',
                  }}>
                    {file.name.replace('.pdf', '')}_watermarked.pdf
                  </span>
                  <button
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      borderRadius: '8px',
                      padding: '6px 12px',
                      fontSize: '12px',
                      fontWeight: 500,
                      border: 'none',
                      cursor: 'pointer',
                      backgroundColor: downloadHovered ? 'var(--btn-primary-hover)' : 'var(--btn-primary)',
                      color: 'var(--btn-primary-text)',
                      transition: 'background-color 0.15s ease',
                      flexShrink: 0,
                    }}
                    onMouseEnter={() => setDownloadHovered(true)}
                    onMouseLeave={() => setDownloadHovered(false)}
                  >
                    <Download size={12} />
                    <span>Download</span>
                  </button>
                </div>
              ))}
            </div>

            {/* Reset button */}
            <div style={{ marginTop: '12px', display: 'flex', justifyContent: 'center' }}>
              <button
                onClick={reset}
                style={{
                  borderRadius: '8px',
                  padding: '8px 16px',
                  fontSize: '12px',
                  fontWeight: 500,
                  cursor: 'pointer',
                  backgroundColor: 'var(--bg-input-placeholder)',
                  color: 'var(--text-secondary)',
                  border: 'none',
                  transition: 'opacity 0.15s ease',
                }}
                onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.opacity = '0.8' }}
                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.opacity = '1' }}
              >
                Watermark More Files
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

/* Slider Control Component */
function SliderControl({
  label,
  value,
  min,
  max,
  onChange,
  suffix = '',
}: {
  label: string
  value: number
  min: number
  max: number
  onChange: (v: number) => void
  suffix?: string
}) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <p style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', margin: 0 }}>{label}</p>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{value}{suffix}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{
          height: '6px',
          width: '100%',
          cursor: 'pointer',
          appearance: 'none',
          borderRadius: '9999px',
          backgroundColor: 'var(--bg-input-placeholder)',
          accentColor: 'var(--primary)',
        }}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '11px', color: 'var(--text-muted)' }}>
        <span>{min}{suffix}</span>
        <span>{max}{suffix}</span>
      </div>
    </div>
  )
}
