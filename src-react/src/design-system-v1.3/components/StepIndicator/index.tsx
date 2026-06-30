import type { CSSProperties } from 'react'

interface Step {
  label: string
  /** Optional custom icon displayed inside the circle instead of number */
  icon?: React.ReactNode
}

interface StepIndicatorProps {
  steps: Step[]
  /** Current active step (0-indexed) */
  currentStep: number
  /** Orientation */
  orientation?: 'horizontal' | 'vertical'
}

export default function StepIndicator({ steps, currentStep, orientation = 'horizontal' }: StepIndicatorProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: orientation === 'horizontal' ? 'row' : 'column',
      alignItems: orientation === 'horizontal' ? 'flex-start' : 'flex-start',
      justifyContent: 'center',
      gap: '0',
    }}>
      {steps.map((step, index) => {
        const isActive = index === currentStep
        const isCompleted = index < currentStep

        const circleStyle: CSSProperties = {
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '32px',
          height: '32px',
          borderRadius: '9999px',
          fontSize: '14px',
          fontWeight: 600,
          flexShrink: 0,
          transition: 'background-color 0.22s ease, color 0.22s ease',
          ...(isCompleted || isActive
            ? { backgroundColor: 'var(--primary)', color: 'var(--btn-primary-text)' }
            : { backgroundColor: 'var(--stepper-inactive-bg)', color: 'var(--stepper-inactive-text)' }),
        }

        const labelStyle: CSSProperties = {
          fontSize: '13px',
          marginTop: '8px',
          whiteSpace: 'nowrap',
          transition: 'color 0.22s ease',
          ...(isActive
            ? { fontWeight: 600, color: 'var(--primary)' }
            : { fontWeight: 400, color: 'var(--stepper-inactive-text)' }),
        }

        const lineContainerStyle: CSSProperties = {
          display: 'flex',
          alignItems: orientation === 'horizontal' ? 'center' : 'stretch',
          ...(orientation === 'horizontal'
            ? { width: '80px', marginLeft: '0' }
            : { height: '24px', marginTop: '8px', alignSelf: 'center', flexDirection: 'column', justifyContent: 'center' }),
        }

        const lineStyle: CSSProperties = {
          ...(orientation === 'horizontal'
            ? { height: '1px', width: '100%' }
            : { width: '1px', height: '100%' }),
          backgroundColor: isCompleted ? 'var(--primary)' : 'var(--stepper-line)',
          transition: 'background-color 0.22s ease',
        }

        return (
          <div key={index} style={{
            display: 'flex',
            flexDirection: orientation === 'horizontal' ? 'row' : 'column',
            alignItems: orientation === 'horizontal' ? 'flex-start' : 'center',
          }}>
            {/* Step circle + label */}
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}>
              <div style={circleStyle}>
                {step.icon || (index + 1)}
              </div>
              <span style={labelStyle}>{step.label}</span>
            </div>

            {/* Connector line (not after last step) */}
            {index < steps.length - 1 && (
              <div style={lineContainerStyle}>
                <div style={lineStyle} />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
