import { useState } from 'react'
import ToolSelector from '@/components/workflow/ToolSelector'
import FileUpload from '@/components/workflow/FileUpload'

export default function HomePage() {
  const [selectedTool, setSelectedTool] = useState<string | null>(null)

  const handleToolSelect = (tool: string) => {
    setSelectedTool(tool)
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      {/* Page heading — centered, minimal */}
      <div className="mb-8 text-center">
        <h1
          className="text-[28px] font-semibold"
          style={{ color: 'var(--text-primary)' }}
        >
          What would you like to do?
        </h1>
        <p
          className="mt-1.5 text-[13px]"
          style={{ color: 'var(--text-muted)' }}
        >
          Select a tool to get started
        </p>
      </div>

      {/* Tool selector — the primary action */}
      <div className="mb-8">
        <ToolSelector selectedTool={selectedTool} onToolSelect={handleToolSelect} />
      </div>

      {/* File upload — appears after tool selection */}
      <div>
        <FileUpload locked={selectedTool === null} />
      </div>
    </div>
  )
}
