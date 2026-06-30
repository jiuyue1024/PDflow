/**
 * PDFflow V1.3 — useTheme hook
 * Read the current resolved theme from CSS variables.
 * This is a read-only hook; writing theme state stays in App.tsx.
 */

export type Theme = 'light' | 'dark'

/** Get the current theme as declared on <html data-theme="..."> */
export function useTheme(): Theme {
  if (typeof document === 'undefined') return 'light'
  return (document.documentElement.getAttribute('data-theme') as Theme) || 'light'
}
