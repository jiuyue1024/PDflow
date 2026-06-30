import React from "react";
import { Search, ChevronRight, Bell } from "lucide-react";

const Header: React.FC = () => {
  return (
    <header
      className="flex h-14 items-center border-b px-6"
      style={{
        backgroundColor: "var(--bg-app)",
        borderColor: "var(--border)",
      }}
    >
      {/* Left: Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm">
        <span style={{ color: "var(--primary-text)" }}>Home</span>
        <ChevronRight className="h-3.5 w-3.5" style={{ color: "var(--text-muted)" }} />
        <span style={{ color: "var(--text-primary)" }}>Document Processing</span>
      </nav>

      {/* Center: Search bar */}
      <div className="mx-auto flex max-w-[400px] flex-1 justify-center">
        <div className="relative w-full">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2"
            style={{ color: "var(--text-muted)" }}
          />
          <input
            type="text"
            placeholder="Search..."
            className="h-10 w-full rounded-lg pl-9 pr-3 text-sm outline-none"
            style={{
              backgroundColor: "var(--bg-input-placeholder)",
              color: "var(--text-primary)",
            }}
          />
        </div>
      </div>

      {/* Right: Notification bell */}
      <div className="relative ml-auto flex items-center">
        <Bell className="h-5 w-5" style={{ color: "var(--text-secondary)" }} />
        <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-red-500" />
      </div>
    </header>
  );
};

export default Header;
