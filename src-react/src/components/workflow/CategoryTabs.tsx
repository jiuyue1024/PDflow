import React, { useState } from "react";

interface CategoryTabsProps {
  categories: string[];
  activeCategory: string;
  onCategoryChange: (category: string) => void;
}

const CategoryTabs: React.FC<CategoryTabsProps> = ({
  categories,
  activeCategory,
  onCategoryChange,
}) => {
  return (
    <nav className="w-full overflow-x-auto scrollbar-none">
      <ul className="flex gap-0 min-w-max">
        {categories.map((category) => {
          const isActive = category === activeCategory;

          return (
            <TabButton
              key={category}
              isActive={isActive}
              label={category}
              onClick={() => onCategoryChange(category)}
            />
          );
        })}
      </ul>
    </nav>
  );
};

function TabButton({
  isActive,
  label,
  onClick,
}: {
  isActive: boolean;
  label: string;
  onClick: () => void;
}) {
  const [hovered, setHovered] = useState(false);

  const buttonStyle: React.CSSProperties = isActive
    ? { color: 'var(--primary)' }
    : hovered
      ? { color: 'var(--text-primary)', backgroundColor: 'var(--bg-hover)', borderRadius: '0.5rem' }
      : { color: 'var(--text-secondary)' };

  return (
    <li className="relative">
      <button
        type="button"
        onClick={onClick}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        className="py-2.5 px-4 text-sm cursor-pointer transition-colors duration-150 whitespace-nowrap"
        style={buttonStyle}
      >
        {label}
        {/* Active indicator line */}
        {isActive && (
          <span
            className="absolute bottom-0 left-4 right-4 h-[2px]"
            style={{ backgroundColor: 'var(--primary)' }}
            aria-hidden="true"
          />
        )}
      </button>
    </li>
  );
}

export default CategoryTabs;
