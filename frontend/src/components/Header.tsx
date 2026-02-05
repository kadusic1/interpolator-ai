import React from "react";
import { Eraser } from "lucide-react";

interface HeaderProps {
  onClear: () => void;
}

const Header: React.FC<HeaderProps> = ({ onClear }) => {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-[#f0f4f9]/90 backdrop-blur-md z-50 flex justify-between items-center px-6 md:px-10">
      <div className="flex items-center gap-2">
        <span className="text-xl font-semibold text-gray-700 tracking-tight">
          Interpolator
        </span>
        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary tracking-wide uppercase">
          AI
        </span>
      </div>

      <button
        onClick={onClear}
        className="p-2 rounded-full hover:bg-gray-200 text-gray-600 transition-colors tooltip-target"
        title="Clear conversation"
      >
        <Eraser size={20} />
      </button>
    </header>
  );
};

export default Header;
