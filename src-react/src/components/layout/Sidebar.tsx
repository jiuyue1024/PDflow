import { useState } from "react";
import {
  LayoutDashboard,
  CreditCard,
  FileText,
  Receipt,
  BarChart3,
  Table2,
  FileDown,
  MonitorPlay,
  Combine,
  Scissors,
  Minimize2,
  Droplets,
  Sparkles,
  Settings,
  FlaskConical,
  Grid3X3,
  FileStack,
  Repeat,
  Wrench,
  Layers,
  ChevronDown,
  type LucideIcon,
} from "lucide-react";

interface NavItem {
  id: string;
  label: string;
  icon: LucideIcon;
}

interface NavSection {
  title: string;
  icon: LucideIcon;
  items: NavItem[];
}

const topItems: NavItem[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
];

const sections: NavSection[] = [
  {
    title: "TEMPLATES",
    icon: FileStack,
    items: [
      { id: "business-cards", label: "Business Cards", icon: CreditCard },
      { id: "contracts", label: "Contracts", icon: FileText },
      { id: "invoices", label: "Invoices & Receipts", icon: Receipt },
      { id: "reports", label: "Analysis Reports", icon: BarChart3 },
    ],
  },
  {
    title: "CONVERT",
    icon: Repeat,
    items: [
      { id: "pdf-excel", label: "PDF \u2192 Excel", icon: Table2 },
      { id: "pdf-word", label: "PDF \u2192 Word", icon: FileDown },
      { id: "pdf-ppt", label: "PDF \u2192 PPT", icon: MonitorPlay },
      { id: "batch-convert", label: "Batch Convert", icon: Layers },
    ],
  },
  {
    title: "TOOLS",
    icon: Wrench,
    items: [
      { id: "merge", label: "Merge", icon: Combine },
      { id: "split", label: "Split", icon: Scissors },
      { id: "optimize", label: "Optimize", icon: Minimize2 },
      { id: "watermark", label: "Watermark", icon: Droplets },
    ],
  },
];

const aiLabsSection: NavSection = {
  title: "AI LABS",
  icon: FlaskConical,
  items: [
    { id: "ai-writing", label: "AI Writing Studio", icon: Sparkles },
  ],
};

interface SidebarProps {
  activeItem: string;
  onItemClick: (item: string) => void;
  developerMode: boolean;
  onDeveloperModeChange: (enabled: boolean) => void;
}

function SectionDivider() {
  return <div className="mx-4 border-t" style={{ borderColor: 'var(--border)' }} />;
}

export default function Sidebar({ activeItem, onItemClick, developerMode, onDeveloperModeChange }: SidebarProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set()
  );
  const [showSettingsPanel, setShowSettingsPanel] = useState(false);
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  const toggleSection = (title: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(title)) {
        next.delete(title);
      } else {
        next.add(title);
      }
      return next;
    });
  };

  const handleSettingsClick = () => {
    onItemClick("settings");
    setShowSettingsPanel((prev) => !prev);
  };

  const handleDevToggle = () => {
    const next = !developerMode;
    onDeveloperModeChange(next);
    if (next) {
      // Opening dev mode — auto expand AI LABS
      setExpandedSections((prev) => {
        const nextSet = new Set(prev);
        nextSet.add("AI LABS");
        return nextSet;
      });
    }
  };

  return (
    <aside
      className="flex h-full w-[260px] flex-shrink-0 flex-col border-r"
      style={{ backgroundColor: 'var(--bg-sidebar)', borderColor: 'var(--border)' }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg text-white" style={{ backgroundColor: 'var(--primary)' }}>
          <Grid3X3 size={18} strokeWidth={1.8} />
        </div>
        <span
          className="text-[17px] font-semibold tracking-tight"
          style={{ color: 'var(--sidebar-text)' }}
        >
          PDFlow
        </span>
      </div>

      {/* Top-level item: Dashboard */}
      <nav className="flex flex-col px-4">
        {topItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeItem === item.id;
          const isHovered = hoveredId === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onItemClick(item.id)}
              onMouseEnter={() => setHoveredId(item.id)}
              onMouseLeave={() => setHoveredId(null)}
              className="flex w-full cursor-pointer items-center gap-3 rounded-lg py-2.5 text-[14px] font-medium transition-colors"
              style={{
                backgroundColor: isActive
                  ? 'var(--sidebar-active-bg)'
                  : isHovered
                    ? 'var(--sidebar-hover)'
                    : 'transparent',
                color: isActive
                  ? 'var(--sidebar-active-text)'
                  : 'var(--sidebar-text)',
              }}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Collapsible sections */}
      <div className="mt-2 flex flex-1 flex-col overflow-y-auto">
        {sections.map((section) => {
          const SectionIcon = section.icon;
          const isExpanded = expandedSections.has(section.title);
          const sectionHeaderId = `header-${section.title}`;
          const isSectionHovered = hoveredId === sectionHeaderId;

          return (
            <div key={section.title}>
              <SectionDivider />
              <button
                onClick={() => toggleSection(section.title)}
                onMouseEnter={() => setHoveredId(sectionHeaderId)}
                onMouseLeave={() => setHoveredId(null)}
                className="flex w-full cursor-pointer items-center gap-2.5 px-4 pt-3 pb-1 text-[12px] font-bold uppercase tracking-widest transition-colors"
                style={{
                  color: isExpanded
                    ? 'var(--sidebar-active-text)'
                    : isSectionHovered
                      ? 'var(--sidebar-text)'
                      : 'var(--sidebar-section-title)',
                }}
              >
                <SectionIcon size={13} strokeWidth={2.2} />
                <span className="flex-1 text-left">{section.title}</span>
                <ChevronDown
                  size={14}
                  strokeWidth={2}
                  className={`transition-transform duration-200 ${
                    isExpanded ? "rotate-180" : ""
                  }`}
                />
              </button>

              <div
                className={`overflow-hidden transition-all duration-200 ${
                  isExpanded
                    ? "max-h-[500px] opacity-100"
                    : "max-h-0 opacity-0"
                }`}
              >
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeItem === item.id;
                  const isItemHovered = hoveredId === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => onItemClick(item.id)}
                      onMouseEnter={() => setHoveredId(item.id)}
                      onMouseLeave={() => setHoveredId(null)}
                      className={`flex w-full cursor-pointer items-center gap-3 rounded-lg pl-11 pr-4 py-2 text-[13px] transition-colors ${
                        isActive ? "font-medium" : ""
                      }`}
                      style={{
                        backgroundColor: isActive
                          ? 'var(--sidebar-active-bg)'
                          : isItemHovered
                            ? 'var(--sidebar-hover)'
                            : 'transparent',
                        color: isActive
                          ? 'var(--sidebar-active-text)'
                          : 'var(--sidebar-text)',
                      }}
                    >
                      <Icon
                        size={16}
                        strokeWidth={1.8}
                        className="opacity-70"
                      />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bottom area: Settings */}
      <div className="flex flex-col px-4 pb-5 pt-2">
        <SectionDivider />

        {/* Settings button */}
        <button
          onClick={handleSettingsClick}
          onMouseEnter={() => setHoveredId("settings-btn")}
          onMouseLeave={() => setHoveredId(null)}
          className="flex w-full cursor-pointer items-center gap-2.5 rounded-lg py-2.5 text-[12px] font-bold uppercase tracking-widest transition-colors"
          style={{
            backgroundColor: activeItem === "settings"
              ? 'var(--sidebar-active-bg)'
              : hoveredId === "settings-btn"
                ? 'var(--sidebar-hover)'
                : 'transparent',
            color: activeItem === "settings"
              ? 'var(--sidebar-active-text)'
              : hoveredId === "settings-btn"
                ? 'var(--sidebar-text)'
                : 'var(--sidebar-section-title)',
          }}
        >
          <Settings size={14} strokeWidth={2.2} />
          <span>Settings</span>
          <ChevronDown
            size={12}
            strokeWidth={2}
            className={`ml-auto transition-transform duration-200 ${
              showSettingsPanel ? "rotate-180" : ""
            }`}
          />
        </button>

        {/* Settings dropdown panel */}
        <div
          className={`overflow-hidden transition-all duration-200 ${
            showSettingsPanel
              ? "max-h-[200px] opacity-100 mt-2"
              : "max-h-0 opacity-0"
          }`}
        >
          <div
            className="rounded-lg border p-3"
            style={{ borderColor: 'var(--border)', backgroundColor: 'var(--bg-card)' }}
          >
            {/* Developer Mode toggle */}
            <div className="flex items-center justify-between">
              <div>
                <p
                  className="text-[12px] font-medium"
                  style={{ color: 'var(--sidebar-text)' }}
                >
                  Developer Mode
                </p>
                <p
                  className="text-[11px]"
                  style={{ color: 'var(--sidebar-section-title)' }}
                >
                  Enable experimental AI features
                </p>
              </div>
              <button
                type="button"
                onClick={handleDevToggle}
                className="relative h-5 w-9 cursor-pointer rounded-full transition-colors duration-200"
                style={{ backgroundColor: developerMode ? 'var(--primary)' : 'var(--border)' }}
              >
                <span
                  className={`
                    absolute left-0.5 top-0.5 h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-200
                    ${developerMode ? "translate-x-4" : "translate-x-0"}
                  `}
                />
              </button>
            </div>
          </div>
        </div>

        {/* AI LABS — only visible when Developer Mode is ON */}
        {developerMode && (
          <div className="mt-2">
            <SectionDivider />
            <button
              onClick={() => toggleSection(aiLabsSection.title)}
              onMouseEnter={() => setHoveredId(`header-${aiLabsSection.title}`)}
              onMouseLeave={() => setHoveredId(null)}
              className="flex w-full cursor-pointer items-center gap-2.5 px-0 pt-3 pb-1 text-[12px] font-bold uppercase tracking-widest transition-colors"
              style={{
                color: expandedSections.has(aiLabsSection.title)
                  ? 'var(--sidebar-active-text)'
                  : hoveredId === `header-${aiLabsSection.title}`
                    ? 'var(--sidebar-text)'
                    : 'var(--sidebar-section-title)',
              }}
            >
              <FlaskConical size={13} strokeWidth={2.2} />
              <span className="flex-1 text-left">{aiLabsSection.title}</span>
              <ChevronDown
                size={14}
                strokeWidth={2}
                className={`transition-transform duration-200 ${
                  expandedSections.has(aiLabsSection.title) ? "rotate-180" : ""
                }`}
              />
            </button>
            <div
              className={`overflow-hidden transition-all duration-200 ${
                expandedSections.has(aiLabsSection.title)
                  ? "max-h-[500px] opacity-100"
                  : "max-h-0 opacity-0"
              }`}
            >
              {aiLabsSection.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeItem === item.id;
                const isItemHovered = hoveredId === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => onItemClick(item.id)}
                    onMouseEnter={() => setHoveredId(item.id)}
                    onMouseLeave={() => setHoveredId(null)}
                    className={`flex w-full cursor-pointer items-center gap-3 rounded-lg pl-11 pr-4 py-2 text-[13px] transition-colors ${
                      isActive ? "font-medium" : ""
                    }`}
                    style={{
                      backgroundColor: isActive
                        ? 'var(--sidebar-active-bg)'
                        : isItemHovered
                          ? 'var(--sidebar-hover)'
                          : 'transparent',
                      color: isActive
                        ? 'var(--sidebar-active-text)'
                        : 'var(--sidebar-text)',
                    }}
                  >
                    <Icon size={16} strokeWidth={1.8} className="opacity-70" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </aside>
  );
}
