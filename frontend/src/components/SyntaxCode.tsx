"use client";

import { useState } from "react";

interface SyntaxCodeProps {
  code: string;
  activeLine?: number;
  filename?: string;
  showLineNumbers?: boolean;
}

export default function SyntaxCode({
  code,
  activeLine,
  filename = "main.py",
  showLineNumbers = true,
}: SyntaxCodeProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = code.split("\n");

  const highlightTokens = (line: string) => {
    // Basic syntax tokenizer for Python display
    const parts = line.split(/(\b(?:def|return|for|in|lambda|print|if|else|import|class|from|as|while|try|except|None|True|False)\b|\b\d+\b|"[^"]*"|'[^']*'|#[^\n]*)/g);
    
    return parts.map((part, i) => {
      if (!part) return null;
      if (part.startsWith("#")) {
        return <span key={i} className="text-[#64748b] italic">{part}</span>;
      }
      if (/^["'].*["']$/.test(part)) {
        return <span key={i} className="text-[#34d399]">{part}</span>;
      }
      if (/^\d+$/.test(part)) {
        return <span key={i} className="text-[#fbbf24] font-medium">{part}</span>;
      }
      if (/^(def|return|for|in|lambda|print|if|else|import|class|from|as|while|try|except)$/.test(part)) {
        return <span key={i} className="text-[#818cf8] font-semibold">{part}</span>;
      }
      if (/^(None|True|False)$/.test(part)) {
        return <span key={i} className="text-[#f472b6] font-semibold">{part}</span>;
      }
      return <span key={i} className="text-[#e2e2ea]">{part}</span>;
    });
  };

  return (
    <div className="rounded-xl overflow-hidden border border-[#534434]/40 bg-[#0c0e14] shadow-2xl font-mono text-[13px]">
      {/* Code header bar */}
      <div className="px-4 py-2.5 bg-[#191b22] border-b border-[#534434]/30 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#ef4444]/70"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#f59e0b]/70"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]/70"></span>
          </div>
          <span className="text-[11px] text-[#a08e7a] ml-2 font-medium">{filename}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[10px] text-[#d8c3ad]/60 uppercase tracking-widest bg-[#111319] px-2 py-0.5 rounded border border-[#534434]/30">
            Python 3.12
          </span>
          <button
            onClick={handleCopy}
            className="text-[11px] text-[#d8c3ad] hover:text-[#c2fb4d] transition-colors flex items-center gap-1 cursor-pointer"
            title="Copy code"
          >
            <span className="material-symbols-outlined text-[14px]">
              {copied ? "check" : "content_copy"}
            </span>
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>
        </div>
      </div>

      {/* Code body */}
      <div className="p-4 overflow-x-auto text-[13px] leading-6">
        <div className="table w-full">
          {lines.map((line, idx) => {
            const lineNum = idx + 1;
            const isHighlighted = activeLine === lineNum;
            return (
              <div
                key={idx}
                className={`table-row transition-colors ${
                  isHighlighted ? "bg-[#c2fb4d]/10 -mx-4 px-4 border-l-2 border-[#c2fb4d]" : ""
                }`}
              >
                {showLineNumbers && (
                  <span className="table-cell select-none pr-4 text-right text-[#534434] opacity-70 w-8">
                    {lineNum}
                  </span>
                )}
                <span className="table-cell whitespace-pre">{highlightTokens(line)}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
