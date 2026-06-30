/**
 * PDFflow V1.3 Typography Tokens
 * Font: Inter, system-ui, -apple-system, sans-serif
 */

export const fontFamily = {
  sans: "'Inter', system-ui, -apple-system, sans-serif",
  mono: "'JetBrains Mono', 'Fira Code', monospace",
} as const

export const fontSize = {
  xs: ['11px', { lineHeight: '16px' }],     // 10px uppercase labels, badges
  sm: ['12.5px', { lineHeight: '18px' }],    // sidebar items, quick action items
  base: ['13px', { lineHeight: '20px' }],    // body text, button labels, descriptions
  md: ['14px', { lineHeight: '20px' }],      // card titles
  lg: ['16px', { lineHeight: '24px' }],      // section headings
  xl: ['20px', { lineHeight: '28px' }],      // page titles
  '2xl': ['24px', { lineHeight: '32px' }],    // hero headings
} as const

export type FontSizeKey = keyof typeof fontSize

export const fontWeight = {
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
} as const

export type FontWeightKey = keyof typeof fontWeight

/** Semantic typography presets */
export const textVariant = {
  /** Uppercase small labels — "RECENT TOOLS", "Quick Actions" */
  caption: {
    fontSize: fontSize.xs[0],
    fontWeight: fontWeight.semibold,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
  /** Sidebar items, quick action items */
  navItem: {
    fontSize: fontSize.sm[0],
    fontWeight: fontWeight.normal,
  },
  /** Body text, descriptions */
  body: {
    fontSize: fontSize.base[0],
    fontWeight: fontWeight.normal,
  },
  /** Card title */
  cardTitle: {
    fontSize: fontSize.md[0],
    fontWeight: fontWeight.semibold,
  },
  /** Section heading (h3) */
  sectionHeading: {
    fontSize: fontSize.lg[0],
    fontWeight: fontWeight.semibold,
  },
  /** Page title (h1) */
  pageTitle: {
    fontSize: fontSize.xl[0],
    fontWeight: fontWeight.semibold,
  },
  /** Hero heading */
  hero: {
    fontSize: fontSize['2xl'][0],
    fontWeight: fontWeight.bold,
  },
} as const
