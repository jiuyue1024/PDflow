/**
 * PDFflow V1.3 Radius Tokens
 */

export const radius = {
  none: '0px',
  sm: '4px',
  md: '6px',
  lg: '8px',      // buttons, inputs
  xl: '12px',     // cards
  '2xl': '16px',  // icon containers
  full: '9999px', // badges, pills, avatar
} as const

export type RadiusKey = keyof typeof radius
