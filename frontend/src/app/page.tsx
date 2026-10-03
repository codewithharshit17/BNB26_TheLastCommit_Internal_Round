"use client";

import Link from "next/link";
import { useState } from "react";
import SyntaxCode from "@/components/SyntaxCode";
import BayesianBar from "@/components/BayesianBar";
import MisconceptionBadge from "@/components/MisconceptionBadge";
import { COMPANY_TRACKS, PROBLEMS } from "@/lib/data";

export default function Home() {
  // Hero interactive demo state
  const [heroInput, setHeroInput] = useState<string>("10");
  const [activeTab, setActiveTab] = useState<"indexing" | "defaults" | "closures">("indexing");

  const tabDemos = {
    indexing: {
      code: "a = [10, 20, 30]\nprint(a[1])",
      userBelief: "Slot 1 (1st item) -> 10",
      pythonActual: "Offset [1] (skip 1 item) -> 20",
      misconception: "1-Based Ordinal Indexing",
      probability: 0.78,
      takeaway: "Indices represent memory offsets from the pointer start, not cardinal count.",
    },
    defaults: {
      code: "def add(x, bucket=[]):\n    bucket.append(x)\n    return bucket\n\nprint(add(1))\nprint(add(2))",
      userBelief: "Fresh [] created on call 2 -> [2]",
      pythonActual: "Reuses shared list in __defaults__ -> [1, 2]",
      misconception: "Recreated Default Arguments",
      probability: 0.84,
      takeaway: "Default arguments are evaluated once at function definition time, not invocation.",
    },
    closures: {
      code: "funcs = [lambda x: x * i for i in range(3)]\nprint([f(2) for f in funcs])",
      userBelief: "i bound at loop time -> [0, 2, 4]",
      pythonActual: "i evaluated late when called (i=2) -> [4, 4, 4]",
      misconception: "Early-Binding Closures",
      probability: 0.81,
      takeaway: "Closures capture variables by reference from enclosing scopes, evaluated at call-time.",
    },
  };

  const currentDemo = tabDemos[activeTab];

  return (
    <div className="w-full flex-1 flex flex-col max-w-7xl mx-auto px-4 md:px-8 py-8 md:py-16">
      {/* Ambient background glow */}
      <div className="relative w-full overflow-hidden">
        <div
          className="absolute -top-32 left-1/4 w-96 h-96 rounded-full blur-3xl pointer-events-none -z-10"
          style={{ backgroundColor: "rgba(194, 251, 77, 0.08)" }}
        />
        <div
          className="absolute top-20 right-10 w-[480px] h-[480px] rounded-full blur-[100px] pointer-events-none -z-10"
          style={{ backgroundColor: "rgba(99, 102, 241, 0.06)" }}
        />

        {/* HERO SECTION */}
        <section className="relative w-full pt-4 pb-16 md:pt-12 md:pb-24">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
            {/* Left Content */}
            <div className="lg:col-span-6 flex flex-col items-start gap-6">
              {/* AI Badge */}
              <div
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#282a30]/80 border border-[#534434]/40"
                style={{ boxShadow: "rgba(194, 251, 77, 0.15) 0px 0px 20px" }}
              >
                <span className="w-2 h-2 rounded-full bg-[#c2fb4d] animate-pulse" />
                <span className="text-[11px] font-mono uppercase tracking-wider font-semibold text-[#c2fb4d]">
                  AI-POWERED PYTHON COGNITIVE ENGINE
                </span>
              </div>

              {/* Headline */}
              <h1 className="font-extrabold text-3xl sm:text-4xl lg:text-5xl tracking-tight text-[#e2e2ea] leading-[1.15]">
                Understand <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#e2e2ea] via-[#c2fb4d] to-[#ffb95f]">
                  how you think
                </span>{" "}
                <br />
                about Python.
              </h1>

              {/* Subtitle */}
              <p className="text-base md:text-lg text-[#d8c3ad] max-w-xl leading-relaxed">
                Re:Learn detects the precise mental misconception behind your mistakes and mathematically validates your conceptual mastery using Bayesian inference.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <Link
                  href="/practice"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#c2fb4d] text-[#0c0e14] font-semibold text-sm hover:bg-[#d4fc79] transition-all shadow-[0_0_20px_rgba(194,251,77,0.3)] hover:shadow-[0_0_30px_rgba(194,251,77,0.5)] cursor-pointer"
                >
                  <span>Start Learning Now</span>
                  <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                </Link>

                <Link
                  href="/trace"
                  className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-[#1d1f26] border border-[#534434]/50 text-[#e2e2ea] text-sm font-medium hover:bg-[#282a30] transition-colors"
                >
                  <span className="material-symbols-outlined text-[18px] text-[#c2fb4d]">insights</span>
                  <span>Interactive Dual Trace</span>
                </Link>
              </div>

              {/* Micro-Trust Indicators */}
              <div className="flex items-center gap-6 pt-4 text-xs text-[#a08e7a] font-mono">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[#c2fb4d] text-[16px]">verified</span>
                  <span>Trained on 42,000+ developer traces</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-[#818cf8] text-[16px]">psychology</span>
                  <span>67 Cognitive Traps</span>
                </div>
              </div>
            </div>

            {/* Right Interactive Hero Widget */}
            <div className="lg:col-span-6">
              <div className="relative rounded-2xl bg-[#1d1f26]/90 border border-[#534434]/50 p-5 md:p-6 shadow-2xl backdrop-blur-md">
                <div className="flex items-center justify-between pb-4 border-b border-[#534434]/30">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#10b981]"></span>
                    <span className="text-xs font-mono text-[#e2e2ea] font-medium">
                      live_diagnostic.py
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-[#c2fb4d] bg-[#c2fb4d]/10 border border-[#c2fb4d]/30 px-2 py-0.5 rounded-full">
                    Active Diagnostic
                  </span>
                </div>

                <div className="py-4">
                  <SyntaxCode
                    filename="inspect_index.py"
                    code="a = [10, 20, 30]&#10;print(a[1])"
                    activeLine={2}
                  />
                </div>

                {/* Interactive response simulation */}
                <div className="bg-[#111319] rounded-xl p-4 border border-[#534434]/30 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[#d8c3ad] font-mono">Predict STDOUT:</span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setHeroInput("10")}
                        className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
                          heroInput === "10"
                            ? "bg-[#ef4444]/20 border border-[#ef4444] text-[#ef4444] font-bold"
                            : "bg-[#1d1f26] text-[#a08e7a] hover:text-[#e2e2ea]"
                        }`}
                      >
                        10 (Common Trap)
                      </button>
                      <button
                        onClick={() => setHeroInput("20")}
                        className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
                          heroInput === "20"
                            ? "bg-[#10b981]/20 border border-[#10b981] text-[#10b981] font-bold"
                            : "bg-[#1d1f26] text-[#a08e7a] hover:text-[#e2e2ea]"
                        }`}
                      >
                        20 (Runtime Truth)
                      </button>
                    </div>
                  </div>

                  {/* Diagnostic feedback result */}
                  {heroInput === "10" ? (
                    <div className="bg-[#282a30] p-3 rounded-lg border border-[#ef4444]/30 space-y-2 animate-fadeIn">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs text-[#ef4444] font-medium font-mono">
                          <span className="material-symbols-outlined text-[16px]">close</span>
                          <span>Predicted 10 != Runtime 20</span>
                        </div>
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#ef4444]/20 text-[#ef4444] font-bold">
                          Divergence
                        </span>
                      </div>
                      <div className="text-xs text-[#d8c3ad] leading-relaxed">
                        Detected Misconception: <strong className="text-[#e2e2ea]">Indexing as 1-Based Ordinal</strong>.
                        You mapped index 1 to the 1st slot. In Python, index represents memory offset (elements to skip).
                      </div>
                      <BayesianBar
                        label="P(index_1_based | answer=10)"
                        probability={0.78}
                        misconceptionName="1-Based Indexing"
                      />
                    </div>
                  ) : (
                    <div className="bg-[#282a30] p-3 rounded-lg border border-[#10b981]/30 space-y-2 animate-fadeIn">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5 text-xs text-[#10b981] font-medium font-mono">
                          <span className="material-symbols-outlined text-[16px]">check</span>
                          <span>Output Matches Python Runtime (20)</span>
                        </div>
                        <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-[#10b981]/20 text-[#10b981] font-bold">
                          Zero-Based Offset
                        </span>
                      </div>
                      <BayesianBar
                        label="P(Mental Model Invariant Retained)"
                        probability={0.96}
                        misconceptionName="0-Based Memory Alignment"
                      />
                    </div>
                  )}

                  <div className="flex justify-end pt-1">
                    <Link
                      href="/trace"
                      className="text-xs text-[#c2fb4d] hover:underline flex items-center gap-1 font-mono"
                    >
                      <span>Explore Full Dual Trace Analysis</span>
                      <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* METRICS STRIP */}
        <section className="w-full py-8 border-y border-[#534434]/30 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="space-y-1">
            <div className="text-2xl md:text-3xl font-bold font-mono text-[#c2fb4d]">42,000+</div>
            <div className="text-xs text-[#a08e7a]">Mental Models Analyzed</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl md:text-3xl font-bold font-mono text-[#38bdf8]">91.4%</div>
            <div className="text-xs text-[#a08e7a]">Transfer Invariant Retention</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl md:text-3xl font-bold font-mono text-[#f59e0b]">67</div>
            <div className="text-xs text-[#a08e7a]">Cognitive Misconception Traps</div>
          </div>
          <div className="space-y-1">
            <div className="text-2xl md:text-3xl font-bold font-mono text-[#10b981]">FAANG</div>
            <div className="text-xs text-[#a08e7a]">Interview System Alignment</div>
          </div>
        </section>

        {/* FEATURES GRID: "Fix the thinking, not just the test cases" */}
        <section className="w-full py-16 md:py-24 space-y-12">
          <div className="text-center space-y-3 max-w-2xl mx-auto">
            <span className="text-xs font-mono uppercase tracking-widest text-[#c2fb4d] font-semibold">
              COGNITIVE DIAGNOSTIC ARCHITECTURE
            </span>
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-bold text-[#e2e2ea] tracking-tight">
              Fix the thinking, not just the test cases.
            </h2>
            <p className="text-sm md:text-base text-[#d8c3ad]">
              Traditional LeetCode test cases tell you whether code passed or failed. Re:Learn uncovers the exact wrong rule running in your head.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Card 1 */}
            <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 flex flex-col justify-between space-y-6 hover:border-[#c2fb4d]/50 transition-colors">
              <div className="space-y-4">
                <div className="w-10 h-10 rounded-xl bg-[#c2fb4d]/10 border border-[#c2fb4d]/30 flex items-center justify-center text-[#c2fb4d]">
                  <span className="material-symbols-outlined text-[22px]">compare_arrows</span>
                </div>
                <h3 className="text-lg font-semibold text-[#e2e2ea]">Dual Trace Execution</h3>
                <p className="text-xs md:text-sm text-[#d8c3ad] leading-relaxed">
                  Side-by-side comparative inspection between how you mentally visualized execution vs how the CPython bytecode actually executed in memory.
                </p>
              </div>
              <div className="pt-4 border-t border-[#534434]/20 flex items-center justify-between text-xs text-[#c2fb4d]">
                <span>View Divergence Ticks</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </div>
            </div>

            {/* Card 2 */}
            <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 flex flex-col justify-between space-y-6 hover:border-[#818cf8]/50 transition-colors">
              <div className="space-y-4">
                <div className="w-10 h-10 rounded-xl bg-[#818cf8]/10 border border-[#818cf8]/30 flex items-center justify-center text-[#818cf8]">
                  <span className="material-symbols-outlined text-[22px]">ssid_chart</span>
                </div>
                <h3 className="text-lg font-semibold text-[#e2e2ea]">Bayesian Belief Updating</h3>
                <p className="text-xs md:text-sm text-[#d8c3ad] leading-relaxed">
                  Every answer feeds an online Bayesian model that updates posterior probabilities over 67 distinct hypothesis classes, dynamically prescribing diagnostic probes.
                </p>
              </div>
              <div className="pt-4 border-t border-[#534434]/20 flex items-center justify-between text-xs text-[#818cf8]">
                <span>P(M|E) Telemetry</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </div>
            </div>

            {/* Card 3 */}
            <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 flex flex-col justify-between space-y-6 hover:border-[#10b981]/50 transition-colors">
              <div className="space-y-4">
                <div className="w-10 h-10 rounded-xl bg-[#10b981]/10 border border-[#10b981]/30 flex items-center justify-center text-[#10b981]">
                  <span className="material-symbols-outlined text-[22px]">verified</span>
                </div>
                <h3 className="text-lg font-semibold text-[#e2e2ea]">Transfer Milestones</h3>
                <p className="text-xs md:text-sm text-[#d8c3ad] leading-relaxed">
                  Proves you didn&apos;t just memorize the answer to one question. Injects disguised transfer problems across different syntactic surfaces and delayed re-tests.
                </p>
              </div>
              <div className="pt-4 border-t border-[#534434]/20 flex items-center justify-between text-xs text-[#10b981]">
                <span>Invariant Verification</span>
                <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
              </div>
            </div>
          </div>
        </section>

        {/* INTERACTIVE COMPARISON PLAYGROUND */}
        <section className="w-full py-12 md:py-20 space-y-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-[#c2fb4d] font-semibold">
                INTERACTIVE DEMO
              </span>
              <h2 className="text-2xl md:text-3xl font-bold text-[#e2e2ea] tracking-tight">
                Inspect Common Python Cognitive Pitfalls
              </h2>
            </div>

            {/* Tabs */}
            <div className="flex items-center gap-2 p-1 rounded-xl bg-[#191b22] border border-[#534434]/30 self-start md:self-auto">
              <button
                onClick={() => setActiveTab("indexing")}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                  activeTab === "indexing"
                    ? "bg-[#282a30] text-[#c2fb4d] shadow"
                    : "text-[#d8c3ad] hover:text-[#e2e2ea]"
                }`}
              >
                1-Based Indexing
              </button>
              <button
                onClick={() => setActiveTab("defaults")}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                  activeTab === "defaults"
                    ? "bg-[#282a30] text-[#c2fb4d] shadow"
                    : "text-[#d8c3ad] hover:text-[#e2e2ea]"
                }`}
              >
                Mutable Defaults
              </button>
              <button
                onClick={() => setActiveTab("closures")}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                  activeTab === "closures"
                    ? "bg-[#282a30] text-[#c2fb4d] shadow"
                    : "text-[#d8c3ad] hover:text-[#e2e2ea]"
                }`}
              >
                Late Closures
              </button>
            </div>
          </div>

          {/* Interactive display box */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            <div className="lg:col-span-6">
              <SyntaxCode code={currentDemo.code} filename={`${activeTab}_trap.py`} />
            </div>

            <div className="lg:col-span-6 rounded-xl bg-[#1d1f26] border border-[#534434]/40 p-6 flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs uppercase font-mono text-[#a08e7a]">Active Cognitive Trap</span>
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-[#ef4444]/20 border border-[#ef4444]/30 text-[#ef4444] font-semibold">
                    {currentDemo.misconception}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                  <div className="p-3 rounded-lg bg-[#111319] border border-[#ef4444]/30">
                    <span className="text-[11px] font-mono text-[#ef4444] font-semibold block mb-1">
                      Learner Intuition
                    </span>
                    <p className="text-xs text-[#e2e2ea] font-mono">{currentDemo.userBelief}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#111319] border border-[#10b981]/30">
                    <span className="text-[11px] font-mono text-[#10b981] font-semibold block mb-1">
                      CPython Runtime Truth
                    </span>
                    <p className="text-xs text-[#e2e2ea] font-mono">{currentDemo.pythonActual}</p>
                  </div>
                </div>

                <div className="pt-2">
                  <p className="text-xs text-[#d8c3ad] italic leading-relaxed">
                    💡 Takeaway: {currentDemo.takeaway}
                  </p>
                </div>
              </div>

              <div className="pt-4 border-t border-[#534434]/30 space-y-3">
                <BayesianBar
                  probability={currentDemo.probability}
                  misconceptionName={currentDemo.misconception}
                />
                <div className="flex items-center justify-between">
                  <Link
                    href={`/practice`}
                    className="text-xs text-[#c2fb4d] hover:underline font-mono flex items-center gap-1"
                  >
                    <span>Test yourself on this problem</span>
                    <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                  </Link>
                  <Link
                    href={`/trace`}
                    className="text-xs text-[#818cf8] hover:underline font-mono"
                  >
                    View step-by-step trace
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* COMPANY PATHWAYS PREVIEW */}
        <section className="w-full py-12 md:py-20 space-y-8">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-[#c2fb4d] font-semibold">
                CURATED EMPLOYER PATHWAYS
              </span>
              <h2 className="text-2xl md:text-3xl font-bold text-[#e2e2ea] tracking-tight">
                Practice Problems That Feel Real
              </h2>
            </div>
            <Link
              href="/tracks"
              className="text-xs font-mono text-[#c2fb4d] hover:underline hidden sm:flex items-center gap-1"
            >
              <span>Explore all tracks ({COMPANY_TRACKS.length})</span>
              <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {COMPANY_TRACKS.slice(0, 3).map((track) => (
              <div
                key={track.id}
                className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 flex flex-col justify-between space-y-4 hover:border-[#c2fb4d]/40 transition-all group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-lg text-[#e2e2ea]">{track.company}</span>
                    <span className="text-[11px] font-mono text-[#a08e7a] bg-[#111319] px-2 py-0.5 rounded border border-[#534434]/30">
                      {track.problem_count} Problems
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-[#e2e2ea] group-hover:text-[#c2fb4d] transition-colors">
                    {track.title}
                  </h4>
                  <p className="text-xs text-[#d8c3ad] leading-relaxed line-clamp-2">
                    {track.description}
                  </p>
                </div>

                <Link
                  href={`/tracks?company=${track.id}`}
                  className="pt-3 border-t border-[#534434]/20 flex items-center justify-between text-xs text-[#c2fb4d] font-mono"
                >
                  <span>Launch Pathway</span>
                  <span className="material-symbols-outlined text-[16px] group-hover:translate-x-1 transition-transform">
                    arrow_forward
                  </span>
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* BOTTOM CALL TO ACTION */}
        <section className="w-full py-12">
          <div className="rounded-3xl bg-gradient-to-r from-[#1d1f26] via-[#282a30] to-[#1d1f26] border border-[#534434]/50 p-8 md:p-12 text-center space-y-6 shadow-2xl relative overflow-hidden">
            <div
              className="absolute -top-24 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full blur-3xl pointer-events-none"
              style={{ backgroundColor: "rgba(194, 251, 77, 0.15)" }}
            />
            <span className="text-xs font-mono uppercase tracking-widest text-[#c2fb4d] font-semibold">
              ELEVATE YOUR CODE INTUITION
            </span>
            <h2 className="text-2xl sm:text-3xl md:text-4xl font-extrabold text-[#e2e2ea] tracking-tight max-w-2xl mx-auto">
              Ready to discover what your intuition gets wrong about Python?
            </h2>
            <p className="text-sm md:text-base text-[#d8c3ad] max-w-xl mx-auto">
              Takes less than 3 minutes to diagnose your first mental model and inspect your personalized Bayesian telemetry.
            </p>
            <div className="pt-2">
              <Link
                href="/practice"
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-xl bg-[#c2fb4d] text-[#0c0e14] font-bold text-sm hover:bg-[#d4fc79] transition-all shadow-[0_0_24px_rgba(194,251,77,0.35)] cursor-pointer"
              >
                <span>Start Practice Diagnostic</span>
                <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
              </Link>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
