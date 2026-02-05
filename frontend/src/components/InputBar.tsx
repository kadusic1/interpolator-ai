import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  ChevronDown,
  Waves,
  ArrowUpRight,
  ArrowDownRight,
  Target,
  Image as ImageIcon,
  Sparkles,
  X,
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
  { id: "lagrange", label: "Lagrange", icon: Waves },
  { id: "newton_forward", label: "Newton Nap.", icon: ArrowUpRight },
  { id: "newton_backward", label: "Newton Naz.", icon: ArrowDownRight },
  { id: "direct", label: "Direktna", icon: Target },
  { id: "hermite", label: "Hermitova", icon: Sparkles }
];

const InputBar: React.FC<InputBarProps> = ({ onSend, isLoading }) => {
  const [input, setInput] = useState("");
  const [method, setMethod] = useState<AgentQuery["method"]>("lagrange");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragging, setIsDragging] = useState(false);

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

  const handleFile = (file: File) => {
    if (file.size > 5 * 1024 * 1024) {
      alert("Veličina datoteke mora biti manja od 5MB");
      return;
    }
    
    if (!file.type.startsWith("image/")) {
      alert("Molimo učitajte sliku");
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setSelectedImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFile(file);
    }
    // Reset input so same file can be selected again if needed
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const removeImage = () => {
    setSelectedImage(null);
  };

  const handleSubmit = () => {
    if (!input.trim() || isLoading) return;

    onSend({ 
      user_input: input, 
      method,
      image_base64: selectedImage 
    });
    setInput("");
    setSelectedImage(null);
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
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={clsx(
          "bg-white/80 backdrop-blur-md rounded-[28px] p-2 flex flex-col relative border transition-all duration-300 ring-0",
          isDragging 
            ? "border-blue-400 shadow-[0_8px_30px_rgb(59,130,246,0.15)] bg-blue-50/50" 
            : "border-gray-200/50 shadow-[0_8px_30px_rgb(0,0,0,0.04)] focus-within:shadow-[0_8px_30px_rgb(59,130,246,0.08)] focus-within:border-blue-200/60"
        )}
      >
        {/* Image Preview */}
        {selectedImage && (
          <div className="px-4 pt-3 pb-1">
            <div className="relative inline-block">
              <img 
                src={selectedImage} 
                alt="Selected" 
                className="h-20 w-auto rounded-xl border border-gray-200 shadow-sm object-cover"
              />
              <button
                onClick={removeImage}
                className="absolute -top-2 -right-2 bg-gray-800 text-white rounded-full p-1 shadow-md hover:bg-gray-900 transition-colors"
              >
                <X size={12} />
              </button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Unesite tačke (npr. (1,2), (3,4)) ili funkciju..."
          className="w-full bg-transparent border-0 focus:ring-0 resize-none px-4 py-3 min-h-[52px] max-h-[200px] text-gray-800 placeholder-gray-500 outline-none"
          rows={1}
          disabled={isLoading}
        />

        {/* Hidden File Input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="image/*"
          className="hidden"
        />

        {/* Toolbar */}
        <div className="flex justify-between items-center px-2 pb-1">
          <div className="flex items-center gap-2">
            {/* Add Image Button */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 rounded-full text-gray-500 hover:bg-gray-100 hover:text-primary transition-colors"
              title="Dodaj sliku"
            >
              <ImageIcon size={20} />
            </button>

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
    </div>
  );
};

export default InputBar;
