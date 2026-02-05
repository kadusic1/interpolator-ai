import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  ChevronDown,
  Sparkles,
  Waves,
  ArrowUpRight,
  ArrowDownRight,
  Target,
} from "lucide-react";
import clsx from "clsx";
import type { AgentQuery } from "../types";

interface InputBarProps {
  onSend: (query: AgentQuery) => void;
  isLoading: boolean;
}

interface ModeOption {
  id: AgentQuery["method"];
  label: string;
  icon?: React.ElementType;
}

const MODES: ModeOption[] = [
  { id: "auto", label: "Auto", icon: Sparkles },
  { id: "lagrange", label: "Lagrange", icon: Waves },
  { id: "newton_forward", label: "Newton Fwd.", icon: ArrowUpRight },
  { id: "newton_backward", label: "Newton Bwd.", icon: ArrowDownRight },
  { id: "direct", label: "Direct", icon: Target },
];

const InputBar: React.FC<InputBarProps> = ({ onSend, isLoading }) => {
  const [input, setInput] = useState("");
  const [method, setMethod] = useState<AgentQuery["method"]>("auto");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  // Close menu on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;
    onSend({ user_input: input, method });
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const selectedMode = MODES.find((m) => m.id === method);
  const SelectedIcon = selectedMode?.icon;

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-6">
      <div
        className="bg-white/80 backdrop-blur-md rounded-[28px] p-2 flex flex-col relative 
                border border-gray-200/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] 
                transition-all duration-300 focus-within:shadow-[0_8px_30px_rgb(59,130,246,0.08)] 
                focus-within:border-blue-200/60 ring-0"
      >
        {/* Input Area */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter points (e.g., (1,2), (3,4)) or ask a question..."
          className="w-full bg-transparent border-0 focus:ring-0 resize-none px-4 py-3 min-h-[52px] max-h-[200px] text-gray-800 placeholder-gray-500 outline-none"
          rows={1}
          disabled={isLoading}
        />

        {/* Toolbar */}
        <div className="flex justify-between items-center px-2 pb-1">
          {/* Mode Selector */}
          <div className="relative" ref={menuRef}>
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-white text-gray-700 hover:bg-gray-50 border border-gray-200 shadow-sm transition-all"
            >
              {SelectedIcon && (
                <SelectedIcon size={14} className="text-primary" />
              )}
              {selectedMode?.label}
              <ChevronDown
                size={14}
                className={clsx(
                  "text-gray-400 transition-transform",
                  isMenuOpen && "rotate-180",
                )}
              />
            </button>

            {isMenuOpen && (
              <div className="absolute bottom-full mb-2 left-0 w-40 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden py-1 z-10 animate-in fade-in zoom-in-95 duration-100">
                {MODES.map((m) => {
                  const ModeIcon = m.icon;
                  return (
                    <button
                      key={m.id}
                      onClick={() => {
                        setMethod(m.id);
                        setIsMenuOpen(false);
                      }}
                      className={clsx(
                        "w-full text-left px-4 py-2.5 text-sm hover:bg-gray-50 flex items-center gap-2",
                        method === m.id
                          ? "text-primary font-medium bg-blue-50/50"
                          : "text-gray-700",
                      )}
                    >
                      {ModeIcon && <ModeIcon size={14} />}
                      {m.label}
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          {/* Send Button */}
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
            className={clsx(
              "p-2 rounded-full transition-all duration-200",
              input.trim() && !isLoading
                ? "bg-primary text-white shadow-md hover:bg-blue-700 hover:shadow-lg"
                : "bg-gray-200 text-gray-400 cursor-not-allowed",
            )}
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      <div className="text-center mt-2">
        <p className="text-[10px] text-gray-400">
          AI can make mistakes. Please double check the interpolation results.
        </p>
      </div>
    </div>
  );
};

export default InputBar;
