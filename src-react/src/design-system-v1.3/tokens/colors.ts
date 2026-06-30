/**
 * PDFflow V1.3 Color Tokens
 * Light: Apple Productivity
 * Dark:  Linear × Raycast × Arc
 * 
 * SINGLE SOURCE OF TRUTH — all CSS variables are derived from these values.
 * Modify a color here → regenerate globals.css → all components update.
 */

export const colors = {
  light: {
    // ── Background ──
    bgApp: '#F7F8FA',
    bgSidebar: '#FFFFFF',
    bgCard: '#FFFFFF',
    bgCardHover: '#F7F8FA',
    bgInput: '#FFFFFF',
    bgInputPlaceholder: '#F3F4F6',
    bgActive: '#EEF2FF',
    bgHover: '#F3F4F6',

    // ── Border ──
    border: '#EAECEF',
    borderStrong: '#D1D5DB',
    borderActive: '#4F8CFF',

    // ── Primary ──
    primary: '#4F8CFF',
    primaryHover: '#3B7BF7',
    primarySubtle: 'rgba(79, 140, 255, 0.10)',
    primaryText: '#4F8CFF',

    // ── Button Primary ──
    btnPrimary: '#4F8CFF',
    btnPrimaryHover: '#3B7BF7',
    btnPrimaryText: '#FFFFFF',

    // ── Icon Preview ──
    iconPreviewBg: '#FFFFFF',

    // ── Text ──
    textPrimary: '#1F2937',
    textSecondary: '#6B7280',
    textMuted: '#9CA3AF',
    textOnPrimary: '#FFFFFF',

    // ── Sidebar ──
    sidebarText: '#374151',
    sidebarTextSecondary: '#6B7280',
    sidebarHover: '#F3F4F6',
    sidebarActiveBg: 'rgba(79, 140, 255, 0.10)',
    sidebarActiveText: '#4F8CFF',
    sidebarSectionTitle: '#9CA3AF',

    // ── Semantic ──
    success: '#22C55E',
    successBg: '#F0FDF4',
    warning: '#F59E0B',
    warningBg: '#FFFBEB',
    error: '#EF4444',
    errorBg: '#FEF2F2',
  },

  dark: {
    // ── Background ──
    bgApp: '#0F1115',
    bgSidebar: '#13161B',
    bgCard: '#171B21',
    bgCardHover: '#1D222B',
    bgInput: '#1B212B',
    bgInputPlaceholder: '#232935',
    bgActive: 'rgba(92, 156, 255, 0.14)',
    bgHover: '#1E2430',

    // ── Border ──
    border: '#272D38',
    borderStrong: '#303744',
    borderActive: '#5C9CFF',

    // ── Primary ──
    primary: '#5C9CFF',
    primaryHover: '#7AAEFF',
    primarySubtle: 'rgba(92, 156, 255, 0.14)',
    primaryText: '#7AAEFF',

    // ── Button Primary (softer for dark mode) ──
    btnPrimary: 'rgba(92, 156, 255, 0.18)',
    btnPrimaryHover: 'rgba(92, 156, 255, 0.28)',
    btnPrimaryText: '#7AAEFF',

    // ── Icon Preview ──
    iconPreviewBg: '#1E2430',

    // ── Text ──
    textPrimary: '#F5F7FA',
    textSecondary: '#A1A8B3',
    textMuted: '#727A88',
    textOnPrimary: '#FFFFFF',

    // ── Sidebar ──
    sidebarText: '#F5F7FA',
    sidebarTextSecondary: '#A1A8B3',
    sidebarHover: '#1E2430',
    sidebarActiveBg: 'rgba(92, 156, 255, 0.14)',
    sidebarActiveText: '#5C9CFF',
    sidebarSectionTitle: '#727A88',

    // ── Semantic ──
    success: '#36D98A',
    successBg: 'rgba(54, 217, 138, 0.10)',
    warning: '#FFB454',
    warningBg: 'rgba(255, 180, 84, 0.10)',
    error: '#FF6B6B',
    errorBg: 'rgba(255, 107, 107, 0.10)',
  },
} as const

/** Convenience type for theme-specific color lookups */
export type ThemeColorSet = typeof colors.light
export type ColorToken = keyof ThemeColorSet

/** CSS variable name mapping: token key → CSS custom property */
export const colorVarMap: Record<ColorToken, string> = {
  bgApp: '--bg-app',
  bgSidebar: '--bg-sidebar',
  bgCard: '--bg-card',
  bgCardHover: '--bg-card-hover',
  bgInput: '--bg-input',
  bgInputPlaceholder: '--bg-input-placeholder',
  bgActive: '--bg-active',
  bgHover: '--bg-hover',
  border: '--border',
  borderStrong: '--border-strong',
  borderActive: '--border-active',
  primary: '--primary',
  primaryHover: '--primary-hover',
  primarySubtle: '--primary-subtle',
  primaryText: '--primary-text',
  btnPrimary: '--btn-primary',
  btnPrimaryHover: '--btn-primary-hover',
  btnPrimaryText: '--btn-primary-text',
  iconPreviewBg: '--icon-preview-bg',
  textPrimary: '--text-primary',
  textSecondary: '--text-secondary',
  textMuted: '--text-muted',
  textOnPrimary: '--text-on-primary',
  sidebarText: '--sidebar-text',
  sidebarTextSecondary: '--sidebar-text-secondary',
  sidebarHover: '--sidebar-hover',
  sidebarActiveBg: '--sidebar-active-bg',
  sidebarActiveText: '--sidebar-active-text',
  sidebarSectionTitle: '--sidebar-section-title',
  success: '--success',
  successBg: '--success-bg',
  warning: '--warning',
  warningBg: '--warning-bg',
  error: '--error',
  errorBg: '--error-bg',
} as const

/** Get CSS variable reference for a color token */
export function cssVar(token: ColorToken): string {
  return `var(${colorVarMap[token]})`
}

/** Category icon colors (per-category accent, theme-independent) */
export const categoryColors = {
  'Business Cards': '#4F8CFF',
  'Contracts': '#22C55E',
  'Invoices & Receipts': '#F59E0B',
  'Analysis Reports': '#A855F7',
} as const
