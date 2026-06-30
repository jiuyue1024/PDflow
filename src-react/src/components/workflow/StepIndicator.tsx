interface StepIndicatorProps {
  steps: { label: string }[]
  currentStep: number // 0-indexed
}

export default function StepIndicator({ steps, currentStep }: StepIndicatorProps) {
  return (
    <div className="flex items-start justify-center">
      {steps.map((step, index) => {
        const isActive = index === currentStep
        const isCompleted = index < currentStep

        const circleStyle: React.CSSProperties = isCompleted
          ? { backgroundColor: 'var(--primary)', color: 'var(--btn-primary-text)' }
          : isActive
            ? { backgroundColor: 'var(--primary)', color: 'var(--btn-primary-text)' }
            : { backgroundColor: 'var(--stepper-inactive-bg)', color: 'var(--stepper-inactive-text)' }

        const labelStyle: React.CSSProperties = isActive
          ? { color: 'var(--primary)' }
          : { color: 'var(--stepper-inactive-text)' }

        const lineStyle: React.CSSProperties = isCompleted
          ? { backgroundColor: 'var(--primary)' }
          : { backgroundColor: 'var(--stepper-line)' }

        return (
          <div key={index} className="flex items-center">
            {/* 步骤圆圈 + 标签 */}
            <div className="flex flex-col items-center">
              {/* 圆圈 */}
              <div
                className="flex h-8 w-8 items-center justify-center rounded-full text-[14px] font-semibold"
                style={circleStyle}
              >
                {index + 1}
              </div>
              {/* 标签 */}
              <span
                className={`mt-2 text-[13px] ${isActive ? 'font-semibold' : ''}`}
                style={labelStyle}
              >
                {step.label}
              </span>
            </div>

            {/* 连接线（最后一个步骤后不显示） */}
            {index < steps.length - 1 && (
              <div
                className="mx-0 mt-4 h-px w-20"
                style={lineStyle}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
