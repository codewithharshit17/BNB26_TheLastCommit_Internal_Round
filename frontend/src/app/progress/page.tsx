"use client";

import { useState } from "react";
import Link from "next/link";
import BayesianBar from "@/components/BayesianBar";
import MisconceptionBadge from "@/components/MisconceptionBadge";
import { ACTIVE_MISCONCEPTIONS } from "@/lib/data";

export default function ProgressMasteryPage() {
  const [selectedFilter, setSelectedFilter] = useState<string>("all");

  const filteredMisconceptions = ACTIVE_MISCONCEPTIONS.filter((m) => {
    if (selectedFilter === "all") return true;
    return m.state === selectedFilter;
  });

  // Simulated 52-week activity heatmap data (7 rows x 24 columns for layout)
  const heatmapWeeks = Array.from({ length: 24 }, (_, weekIdx) =>
    Array.from({ length: 7 }, (_, dayIdx) => {
      // Deterministic streak simulation
      const isRecent = weekIdx >= 20;
      const intensity = isRecent
        ? (weekIdx + dayIdx) % 3 === 0
          ? 3
          : 2
        : (weekIdx * 7 + dayIdx) % 5 === 0
        ? 2
        : (weekIdx * 7 + dayIdx) % 3 === 0
        ? 1
        : 0;
      return intensity;
    })
  );

  return (
    <div className="w-full flex-1 max-w-7xl mx-auto px-4 md:px-8 py-8 md:py-16 space-y-12">
      {/* Header section */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#1d1f26] border border-[#c2fb4d]/30 text-[#c2fb4d] text-xs font-mono font-semibold">
          <span className="material-symbols-outlined text-[16px]">psychology_alt</span>
          <span>MENTAL MODEL MASTERY</span>
        </div>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#e2e2ea] tracking-tight">
              Mastery Progress
            </h1>
            <p className="text-sm md:text-base text-[#d8c3ad] mt-2 max-w-2xl">
              Track how your mental models evolve and prove lasting retention across Python invariants using empirical Bayesian evidence.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/practice"
              className="px-4 py-2 rounded-xl bg-[#c2fb4d] text-[#0c0e14] font-bold text-xs hover:bg-[#d4fc79] transition-all shadow-[0_0_16px_rgba(194,251,77,0.3)]"
            >
              Start Practice Session →
            </Link>
          </div>
        </div>
      </div>

      {/* Top 3 Impact Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1 */}
        <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-[#a08e7a]">
            <span className="text-xs uppercase font-mono tracking-wider">Models Mastered</span>
            <span className="material-symbols-outlined text-[#10b981] text-[20px]">verified</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl md:text-4xl font-extrabold font-mono text-[#e2e2ea]">38</span>
            <span className="text-sm font-mono text-[#a08e7a]">/ 42 Mastered (90%)</span>
          </div>
          <div className="h-1.5 w-full bg-[#111319] rounded-full overflow-hidden">
            <div className="h-full bg-[#10b981] rounded-full" style={{ width: "90%" }} />
          </div>
          <div className="text-[11px] text-[#10b981] font-mono">
            4 active or suspected remaining
          </div>
        </div>

        {/* Card 2 */}
        <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-[#a08e7a]">
            <span className="text-xs uppercase font-mono tracking-wider">Practice Streak</span>
            <span className="material-symbols-outlined text-[#f59e0b] text-[20px]">
              local_fire_department
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl md:text-4xl font-extrabold font-mono text-[#e2e2ea]">14</span>
            <span className="text-sm font-mono text-[#a08e7a]">Days Consistent</span>
          </div>
          <div className="h-1.5 w-full bg-[#111319] rounded-full overflow-hidden">
            <div className="h-full bg-[#f59e0b] rounded-full" style={{ width: "70%" }} />
          </div>
          <div className="text-[11px] text-[#f59e0b] font-mono">
            Top 4% cognitive momentum • Best: 32 days
          </div>
        </div>

        {/* Card 3 */}
        <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 space-y-3 shadow-lg">
          <div className="flex items-center justify-between text-[#a08e7a]">
            <span className="text-xs uppercase font-mono tracking-wider">Transfer Accuracy</span>
            <span className="material-symbols-outlined text-[#38bdf8] text-[20px]">
              check_circle
            </span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl md:text-4xl font-extrabold font-mono text-[#e2e2ea]">
              91.4%
            </span>
            <span className="text-sm font-mono text-[#a08e7a]">Invariant Passed</span>
          </div>
          <div className="h-1.5 w-full bg-[#111319] rounded-full overflow-hidden">
            <div className="h-full bg-[#38bdf8] rounded-full" style={{ width: "91.4%" }} />
          </div>
          <div className="text-[11px] text-[#38bdf8] font-mono">
            112 / 122 Probes Verified
          </div>
        </div>
      </div>

      {/* Consistency & Activity Heatmap */}
      <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 md:p-8 space-y-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#534434]/30 pb-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#c2fb4d] text-[20px]">grid_view</span>
              <h2 className="text-lg font-bold text-[#e2e2ea]">Consistency & Activity</h2>
            </div>
            <p className="text-xs text-[#a08e7a]">
              Daily diagnostic probes and invariant transfer checks over recent cycles.
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="flex items-center gap-1.5 text-[#10b981]">
              <span className="w-2 h-2 rounded-full bg-[#10b981]"></span>
              <span>14 days active streak</span>
            </div>
            <div className="text-[#d8c3ad] bg-[#111319] px-2.5 py-1 rounded border border-[#534434]/40">
              Daily Target: <strong className="text-[#c2fb4d]">4 / 4 Met</strong>
            </div>
          </div>
        </div>

        {/* Heatmap grid */}
        <div className="overflow-x-auto pb-2">
          <div className="inline-flex gap-1.5">
            {heatmapWeeks.map((week, wIdx) => (
              <div key={wIdx} className="flex flex-col gap-1.5">
                {week.map((intensity, dIdx) => {
                  let bgClass = "bg-[#111319] border border-[#534434]/30";
                  if (intensity === 1) bgClass = "bg-[#c2fb4d]/25 border border-[#c2fb4d]/30";
                  if (intensity === 2) bgClass = "bg-[#c2fb4d]/60 border border-[#c2fb4d]/60";
                  if (intensity === 3) bgClass = "bg-[#c2fb4d] shadow-[0_0_8px_rgba(194,251,77,0.5)]";

                  return (
                    <div
                      key={dIdx}
                      className={`w-3.5 h-3.5 rounded-sm transition-all hover:scale-125 cursor-pointer ${bgClass}`}
                      title={`Week ${wIdx + 1}, Day ${dIdx + 1} (${intensity} probes passed)`}
                    />
                  );
                })}
              </div>
            ))}
          </div>

          <div className="flex items-center justify-between pt-3 text-[10px] font-mono text-[#a08e7a]">
            <span>Nov</span>
            <span>Dec</span>
            <span>Jan</span>
            <span>Feb</span>
            <span>Mar</span>
            <span>Apr</span>
            <div className="flex items-center gap-1">
              <span>Less</span>
              <span className="w-2.5 h-2.5 rounded-sm bg-[#111319] border border-[#534434]/40"></span>
              <span className="w-2.5 h-2.5 rounded-sm bg-[#c2fb4d]/30"></span>
              <span className="w-2.5 h-2.5 rounded-sm bg-[#c2fb4d]/70"></span>
              <span className="w-2.5 h-2.5 rounded-sm bg-[#c2fb4d]"></span>
              <span>More</span>
            </div>
          </div>
        </div>
      </div>

      {/* Active Misconceptions in Focus */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-[#e2e2ea]">Active Misconceptions in Focus</h2>
            <p className="text-xs text-[#d8c3ad] mt-1">
              Bayesian beliefs evaluated across invariant discriminator challenges.
            </p>
          </div>

          {/* Filter tabs */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-[#1d1f26] border border-[#534434]/40 text-xs font-mono">
            {["all", "active", "intervened", "suspected_resolved", "confirmed_resolved"].map(
              (f) => (
                <button
                  key={f}
                  onClick={() => setSelectedFilter(f)}
                  className={`px-3 py-1 rounded-lg transition-all capitalize ${
                    selectedFilter === f
                      ? "bg-[#c2fb4d] text-[#0c0e14] font-bold shadow-sm"
                      : "text-[#a08e7a] hover:text-[#e2e2ea]"
                  }`}
                >
                  {f.replace(/_/g, " ")}
                </button>
              )
            )}
          </div>
        </div>

        {/* Misconception cards list */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredMisconceptions.map((item) => (
            <div
              key={item.id}
              className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 space-y-4 hover:border-[#c2fb4d]/40 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <span className="text-xs font-mono font-bold text-[#a08e7a]">
                    ID: {item.id}
                  </span>
                  <MisconceptionBadge state={item.state} />
                </div>

                <h3 className="text-lg font-bold text-[#e2e2ea]">{item.name}</h3>
                <p className="text-xs text-[#d8c3ad] leading-relaxed">{item.description}</p>

                {/* Evidence Checklist */}
                <div className="pt-2 border-t border-[#534434]/20 space-y-1.5 text-xs font-mono">
                  <div className="flex items-center justify-between text-[#a08e7a]">
                    <span>Discriminator Passes:</span>
                    <span className="text-[#c2fb4d] font-bold">
                      {item.evidence.discriminator_passes} / 3 verified
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[#a08e7a]">
                    <span>Surface Variants:</span>
                    <span className="text-[#e2e2ea]">
                      {item.evidence.surface_forms.join(", ")}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[#a08e7a]">
                    <span>Delayed Retest:</span>
                    <span
                      className={
                        item.evidence.delayed_retest ? "text-[#10b981]" : "text-[#f59e0b]"
                      }
                    >
                      {item.evidence.delayed_retest ? "Passed" : "Pending Scheduled"}
                    </span>
                  </div>
                </div>

                {/* Bayesian probability meter */}
                <div className="pt-2">
                  <BayesianBar
                    label="P(Misconception | Evidence)"
                    probability={item.posterior}
                    misconceptionName={item.name}
                  />
                </div>
              </div>

              {/* Action buttons */}
              <div className="pt-4 border-t border-[#534434]/30 flex items-center justify-between">
                <Link
                  href="/trace"
                  className="text-xs font-mono text-[#818cf8] hover:underline flex items-center gap-1"
                >
                  <span className="material-symbols-outlined text-[14px]">insights</span>
                  <span>View Trace Model</span>
                </Link>

                <Link
                  href="/practice"
                  className="px-3 py-1.5 rounded-lg bg-[#c2fb4d] text-[#0c0e14] text-xs font-mono font-bold hover:bg-[#d4fc79] transition-all"
                >
                  Practice Transfer →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Target Track Company Readiness */}
      <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 md:p-8 space-y-6 shadow-xl">
        <div className="space-y-1">
          <h2 className="text-lg font-bold text-[#e2e2ea]">Company Target Readiness</h2>
          <p className="text-xs text-[#a08e7a]">
            Cognitive depth index benchmarked against FAANG & Tier-1 systems interviews.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { company: "Google L5", score: 92, note: "Pointers & Indexing" },
            { company: "Meta E5", score: 84, note: "Runtime References & Closures" },
            { company: "Amazon SDE II", score: 96, note: "Core Model & Scoping" },
            { company: "Stripe L2", score: 78, note: "Financial Invariants & Mutability" },
          ].map((item) => (
            <div
              key={item.company}
              className="p-4 rounded-xl bg-[#111319] border border-[#534434]/40 space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-[#e2e2ea]">{item.company}</span>
                <span className="text-xs font-mono text-[#c2fb4d] font-bold">{item.score}%</span>
              </div>
              <div className="h-1.5 w-full bg-[#1c2235] rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-[#10b981] to-[#c2fb4d] rounded-full"
                  style={{ width: `${item.score}%` }}
                />
              </div>
              <div className="text-[10px] font-mono text-[#a08e7a]">{item.note}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
