import React, { useState } from "react";
import {
  Combine,
  Scissors,
  Minimize2,
  Table2,
  Droplets,
  LayoutGrid,
  ChevronDown,
} from "lucide-react";

interface ToolSelectorProps {
  selectedTool: string | null;
  onToolSelect: (tool: string) => void;
}

const tools = [
  { id: "merge", label: "Merge PDF", icon: Combine },
  { id: "split", label: "Split PDF", icon: Scissors },
  { id: "compress", label: "Compress PDF", icon: Minimize2 },
  { id: "pdf-excel", label: "PDF \u2192 Excel", icon: Table2 },
  { id: "watermark", label: "Watermark", icon: Droplets },
  { id: "templates", label: "Templates", icon: LayoutGrid },
] as const;

export default function ToolSelector({
  selectedTool,
  onToolSelect,
}: ToolSelectorProps) {
  return (
    <div
      className="rounded-xl border p-6"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border)',
      }}
    >
      {/* Panel Header */}
      <div className="mb-6 flex items-center justify-between">
        <h3
          className="text-[14px] font-semibold"
          style={{ color: 'var(--text-primary)' }}
        >
          Choose a Tool
        </h3>
        <span className="text-xs font-medium" style={{ color: 'var(--primary)' }}>
          *Active
        </span>
      </div>

      {/* Dropdown */}
      <div className="relative mb-8">
        <select
          value={selectedTool ?? ""}
          onChange={(e) => onToolSelect(e.target.value)}
          className="h-11 w-full appearance-none rounded-lg border px-4 pr-10 text-sm outline-none transition-colors"
          style={{
            backgroundColor: 'var(--bg-input)',
            borderColor: 'var(--border)',
            color: 'var(--text-primary)',
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--border-active)';
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'var(--border)';
          }}
        >
          <option value="">Select a tool...</option>
          {tools.map((tool) => (
            <option key={tool.id} value={tool.id}>
              {tool.label}
            </option>
          ))}
        </select>
        <ChevronDown
          className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2"
          style={{ color: 'var(--text-secondary)' }}
        />
      </div>

      {/* Quick Action Chips */}
      <div className="flex flex-wrap gap-4">
        {tools.map((tool) => {
          const Icon = tool.icon;
          const isSelected = selectedTool === tool.id;

          return (
            <ToolChip
              key={tool.id}
              tool={tool}
              isSelected={isSelected}
              onSelect={() => onToolSelect(tool.id)}
            />
          );
        })}
      </div>
    </div>
  );
}

function ToolChip({
  tool,
  isSelected,
  onSelect,
}: {
  tool: (typeof tools)[number];
  isSelected: boolean;
  onSelect: () => void;
}) {
  const [hovered, setHovered] = useState(false);
  const Icon = tool.icon;

  const chipStyle: React.CSSProperties = isSelected
    ? {
        borderColor: 'var(--primary)',
        backgroundColor: 'var(--primary-subtle)',
        color: 'var(--primary)',
      }
    : hovered
      ? {
          borderColor: 'var(--primary)',
          backgroundColor: 'var(--primary-subtle)',
          color: 'var(--primary)',
        }
      : {
          borderColor: 'var(--border)',
          backgroundColor: 'var(--bg-card)',
          color: 'var(--text-primary)',
        };

  return (
    <button
      onClick={onSelect}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      className="flex items-center gap-2 rounded-lg border px-4 py-2.5 text-[13px] transition-all cursor-pointer shadow-none"
      style={chipStyle}
    >
      <Icon className="h-4 w-4" />
      <span>{tool.label}</span>
    </button>
  );
}
