/**
 * PDFflow V1.3 Spacing Tokens
 * Based on a 4px base grid.
 * Use as: padding={spacing[4]} → 16px
 */

export const spacing = {
  0: '0px',
  0.5: '2px',
  1: '4px',
  1.5: '6px',
  2: '8px',
  2.5: '10px',
  3: '12px',
  3.5: '14px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
  20: '80px',
} as const

export type SpacingKey = keyof typeof spacing

/** Semantic spacing aliases */
export const space = {
  /** Section gap — between major content blocks */
  section: spacing[6],
  /** Card gap — spacing between cards in a grid */
  card: spacing[4],
  /** Inline gap — between label and value in a row */
  inline: spacing[2],
  /** Tight gap — between icon and text */
  tight: spacing[1.5],
  /** Icon gap — between icon and text in nav items */
  icon: spacing[3],
  /** Sidebar item px */
  sidebarItem: spacing[4],
  /** Card content px */
  cardContent: spacing[5],
  /** Page content px */
  pageContent: spacing[8],
} as const

/** Layout dimensions */
export const layout = {
  sidebarWidth: '240px',
  quickActionsWidth: '200px',
  headerHeight: '48px',
  maxContentWidth: '960px',
} as const
