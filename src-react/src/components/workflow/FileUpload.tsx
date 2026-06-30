import React from "react";
import { CloudUpload } from "lucide-react";

interface FileUploadProps {
  locked: boolean;
}

export default function FileUpload({ locked }: FileUploadProps) {
  return (
    <div
      className={`rounded-xl border p-6 shadow-sm transition-opacity ${
        locked ? "pointer-events-none opacity-60" : ""
      }`}
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border)',
      }}
    >
      {/* Panel Header */}
      <div className="mb-5 flex items-center justify-between">
        <h3
          className="text-base font-semibold"
          style={{ color: 'var(--text-primary)' }}
        >
          Upload Files
        </h3>
        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
          Locked
        </span>
      </div>

      {/* Drop Zone */}
      <div
        className="flex min-h-[200px] flex-col items-center justify-center rounded-xl border-2 border-dashed"
        style={{
          borderColor: 'var(--border)',
          backgroundColor: 'var(--bg-input-placeholder)',
        }}
      >
        <CloudUpload
          className="mb-3 h-12 w-12"
          style={{ color: 'var(--text-muted)' }}
        />
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Drag &amp; drop your files here
        </p>
      </div>

      {/* Browse Button (disabled) */}
      <button
        disabled
        className="mt-4 w-full cursor-not-allowed rounded-lg border px-5 py-2.5 text-sm"
        style={{
          backgroundColor: 'var(--bg-hover)',
          borderColor: 'var(--border)',
          color: 'var(--text-muted)',
        }}
      >
        Browse Files
      </button>

      {/* Helper Text */}
      <p
        className="mt-3 text-center text-xs"
        style={{ color: 'var(--text-muted)' }}
      >
        PDF and images supported. Max 50MB per file
      </p>
    </div>
  );
}
