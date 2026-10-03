"use client";

import { useState } from "react";

interface BayesianBarProps {
  label?: string;
  probability: number; // 0 to 1
  misconceptionName?: string;
  showFormula?: boolean;
}

export default function BayesianBar({
  label = "P(Misconception | Evidence)",
  probability,
  misconceptionName,
  showFormula = true,
}: BayesianBarProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const percentage = Math.round(probability * 100);

  // Gradient selection based on threshold
  const isHighRisk = probability > 0.7;
  const isModerate = probability >= 0.3 && probability <= 0.7;

  let barGradient = "from-[#10b981] to-[#34d399]"; // low risk / master
  if (isHighRisk) {
    barGradient = "from-[#f59e0b] to-[#ef4444]"; // high risk
  } else if (isModerate) {
    barGradient = "from-[#6366f1] to-[#818cf8]"; // learning / probe
  }

  return (
    <div className="w-full space-y-1.5 font-mono">
      <div className="flex items-center justify-between text-[11px]">
        <div className="flex items-center gap-1.5 text-[#d8c3ad]">
          <span className="font-sans font-medium">{label}</span>
          {showFormula && (
            <div className="relative inline-block">
              <button
                type="button"
                onMouseEnter={() => setShowTooltip(true)}
                onMouseLeave={() => setShowTooltip(false)}
                onClick={() => setShowTooltip(!showTooltip)}
                className="text-[#a08e7a] hover:text-[#c2fb4d] transition-colors"
                aria-label="Formula details"
              >
                <span className="material-symbols-outlined text-[13px]">help_outline</span>
              </button>

              {showTooltip && (
                <div className="absolute bottom-full left-0 mb-2 w-64 p-3 rounded-lg bg-[#1d1f26] border border-[#534434] shadow-xl text-[11px] text-[#e2e2ea] z-30 font-sans">
                  <div className="font-mono text-[#c2fb4d] font-semibold mb-1">
                    Bayes Theorem Update:
                  </div>
                  <div className="font-mono bg-[#0c0e14] p-1.5 rounded text-[10px] text-center mb-1 border border-[#534434]/40">
                    P(M|E) = [P(E|M) · P(M)] / P(E)
                  </div>
                  <p className="text-[10px] text-[#d8c3ad] leading-normal">
                    Estimates the likelihood you harbor {misconceptionName || "this cognitive model"} given your pattern of answers across discriminatory test cases.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {misconceptionName && (
            <span className="text-[10px] text-[#a08e7a] hidden sm:inline">{misconceptionName}</span>
          )}
          <span
            className={`font-semibold ${
              isHighRisk ? "text-[#ef4444]" : isModerate ? "text-[#818cf8]" : "text-[#10b981]"
            }`}
          >
            {percentage}%
          </span>
        </div>
      </div>

      {/* Progress track */}
      <div className="h-1.5 w-full rounded-full bg-[#1c2235] overflow-hidden border border-[#534434]/30">
        <div
          className={`h-full rounded-full bg-gradient-to-r ${barGradient} transition-all duration-700 ease-out`}
          style={{ width: `${Math.min(100, Math.max(4, percentage))}%` }}
        />
      </div>
    </div>
  );
}
