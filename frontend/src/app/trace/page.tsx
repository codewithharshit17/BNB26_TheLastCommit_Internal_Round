"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import confetti from "canvas-confetti";
import BayesianBar from "@/components/BayesianBar";
import { PROBLEMS, TRACE_STEPS_BY_ITEM } from "@/lib/data";

function TraceAnalysisContent() {
  const searchParams = useSearchParams();
  const problemParam = searchParams.get("problem") || "i1";
  const userPredictionParam = searchParams.get("prediction");

  const [activeItemKey, setActiveItemKey] = useState<string>(
    TRACE_STEPS_BY_ITEM[problemParam] ? problemParam : "i1"
  );
  const currentProblem = PROBLEMS.find((p) => p.item_id === activeItemKey) || PROBLEMS[0];
  const steps = TRACE_STEPS_BY_ITEM[activeItemKey] || TRACE_STEPS_BY_ITEM["i1"];

  const [currentStepIdx, setCurrentStepIdx] = useState<number>(1);
  const [showDiscriminatorModal, setShowDiscriminatorModal] = useState(false);
  const [discriminatorAnswer, setDiscriminatorAnswer] = useState<string | null>(null);
  const [resolvedStatus, setResolvedStatus] = useState<boolean | null>(null);

  const activeStep = steps[currentStepIdx] || steps[0];

  const handleDiscriminatorSubmit = (choice: string) => {
    setDiscriminatorAnswer(choice);
    const isCorrect = choice === "'alpha'";
    setResolvedStatus(isCorrect);
    if (isCorrect) {
      confetti({
        particleCount: 100,
        spread: 80,
        origin: { y: 0.5 },
        colors: ["#10b981", "#c2fb4d", "#38bdf8"],
      });
    }
  };

  return (
    <div className="w-full flex-1 max-w-6xl mx-auto px-4 md:px-8 py-8 md:py-16">
      {/* Header section with ambient glow */}
      <div className="relative text-center space-y-4 mb-10">
        <div
          className="absolute -top-16 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full blur-3xl pointer-events-none -z-10"
          style={{ backgroundColor: "rgba(245, 158, 11, 0.12)" }}
        />

        {/* Misconception Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#1d1f26] border border-[#f59e0b]/40 text-[#f59e0b] text-xs font-mono font-semibold">
          <span className="material-symbols-outlined text-[16px]">psychology</span>
          <span>Detected Misconception: Indexing as 1-Based Ordinal</span>
          <span className="bg-[#f59e0b]/20 px-2 py-0.5 rounded text-[11px]">78% posterior</span>
        </div>

        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#e2e2ea] tracking-tight">
          See what happened.
        </h1>
        <p className="text-sm md:text-base text-[#d8c3ad] max-w-xl mx-auto leading-relaxed">
          Comparing how you thought about the code vs how Python actually executes it step-by-step.
        </p>

        {/* Problem toggle selector */}
        <div className="flex justify-center items-center gap-2 pt-2">
          <button
            onClick={() => {
              setActiveItemKey("i1");
              setCurrentStepIdx(1);
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
              activeItemKey === "i1"
                ? "bg-[#c2fb4d] text-[#0c0e14] shadow"
                : "bg-[#1d1f26] text-[#a08e7a] hover:text-[#e2e2ea]"
            }`}
          >
            Trace: List Indexing (1-Based)
          </button>
          <button
            onClick={() => {
              setActiveItemKey("i2");
              setCurrentStepIdx(2);
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all ${
              activeItemKey === "i2"
                ? "bg-[#c2fb4d] text-[#0c0e14] shadow"
                : "bg-[#1d1f26] text-[#a08e7a] hover:text-[#e2e2ea]"
            }`}
          >
            Trace: Mutable Default Args
          </button>
        </div>
      </div>

      {/* Step scrubber & timeline */}
      <div className="mb-8 p-4 rounded-xl bg-[#1d1f26] border border-[#534434]/40 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-[#c2fb4d] font-bold">
            Step {currentStepIdx + 1} of {steps.length}:
          </span>
          <span className="text-[#e2e2ea]">{activeStep.description}</span>
        </div>

        {/* Stepper buttons */}
        <div className="flex items-center gap-2 shrink-0">
          {steps.map((st, idx) => (
            <button
              key={st.step}
              onClick={() => setCurrentStepIdx(idx)}
              className={`px-3 py-1 rounded text-xs font-mono transition-all ${
                currentStepIdx === idx
                  ? "bg-[#c2fb4d] text-[#0c0e14] font-bold shadow-md"
                  : "bg-[#111319] text-[#a08e7a] hover:text-[#e2e2ea]"
              }`}
            >
              Tick {idx + 1}
              {st.divergence && (
                <span className="ml-1 text-[10px] text-[#ef4444] font-bold">⚡</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Two-Column Visual Comparison */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8 items-stretch">
        {/* Left Panel: Your Thinking */}
        <div className="relative flex flex-col justify-between bg-[#1d1f26] rounded-2xl p-6 border border-[#ef4444]/40 shadow-xl space-y-6">
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[#534434]/30 pb-3">
              <span className="text-xs uppercase font-mono tracking-wider font-semibold text-[#d8c3ad]">
                Your Mental Model
              </span>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#f59e0b]/15 text-[#f59e0b] text-[11px] font-mono border border-[#f59e0b]/30">
                <span className="w-1.5 h-1.5 rounded-full bg-[#f59e0b]" />
                1-Based Ordinal
              </span>
            </div>

            {/* Code Snippet with annotation */}
            <div className="bg-[#0c0e14] rounded-xl p-4 font-mono text-xs text-[#e2e2ea] space-y-1.5 border border-[#534434]/40">
              <div className="text-[#a08e7a]">a = [10, 20, 30]</div>
              <div className="text-[#f59e0b] italic text-[11px]">
                # You mapped index 1 to the 1st element
              </div>
              <div>
                print(a[<span className="text-[#ef4444] font-bold underline">1</span>])
              </div>
            </div>

            {/* Believed Mapping visualization */}
            <div className="space-y-2 pt-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#a08e7a] block">
                {activeStep.learner_view.title}
              </span>

              <div className="grid grid-cols-3 gap-2">
                {activeStep.learner_view.mapping.map((slot, i) => (
                  <div
                    key={i}
                    className={`rounded-xl p-3 text-center transition-all ${
                      slot.selected
                        ? "bg-[#ef4444]/15 border-2 border-[#ef4444] shadow-md"
                        : "bg-[#111319] border border-[#534434]/30 opacity-60"
                    }`}
                  >
                    <div
                      className={`text-[10px] font-mono uppercase ${
                        slot.selected ? "text-[#ef4444] font-bold" : "text-[#a08e7a]"
                      }`}
                    >
                      {slot.label}
                    </div>
                    <div
                      className={`text-lg font-bold font-mono my-0.5 ${
                        slot.selected ? "text-[#e2e2ea]" : "text-[#d8c3ad]"
                      }`}
                    >
                      {slot.value}
                    </div>
                    <div
                      className={`text-[10px] font-mono ${
                        slot.selected ? "text-[#ef4444]" : "text-[#a08e7a]"
                      }`}
                    >
                      {slot.note}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Predicted Result Box */}
          <div className="mt-4 p-4 rounded-xl bg-[#111319] border border-[#ef4444]/40 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-[#ef4444] text-[22px]">close</span>
              <div>
                <div className="text-[11px] font-mono text-[#a08e7a]">Predicted Output</div>
                <div className="text-base font-bold font-mono text-[#e2e2ea]">
                  [ {userPredictionParam || activeStep.learner_view.output || "10"} ]
                </div>
              </div>
            </div>
            <span className="text-[10px] font-mono uppercase px-2.5 py-1 rounded-full bg-[#ef4444]/20 border border-[#ef4444]/40 text-[#ef4444] font-bold">
              Cognitive Divergence
            </span>
          </div>
        </div>

        {/* Right Panel: Python Actually Does */}
        <div className="relative flex flex-col justify-between bg-[#1d1f26] rounded-2xl p-6 border border-[#c2fb4d]/40 shadow-xl space-y-6">
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-[#534434]/30 pb-3">
              <span className="text-xs uppercase font-mono tracking-wider font-semibold text-[#c2fb4d]">
                Python Actually Does
              </span>
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#c2fb4d]/15 text-[#c2fb4d] text-[11px] font-mono border border-[#c2fb4d]/30">
                <span className="w-1.5 h-1.5 rounded-full bg-[#c2fb4d]" />
                0-Based Memory Offset
              </span>
            </div>

            {/* Code Snippet with annotation */}
            <div className="bg-[#0c0e14] rounded-xl p-4 font-mono text-xs text-[#e2e2ea] space-y-1.5 border border-[#534434]/40">
              <div className="text-[#a08e7a]">a = [10, 20, 30]</div>
              <div className="text-[#c2fb4d] italic text-[11px]">
                # Offset 1 skips 10, yields element at index 1
              </div>
              <div>
                print(a[<span className="text-[#c2fb4d] font-bold underline">1</span>])
              </div>
            </div>

            {/* Actual Memory Offset visualization */}
            <div className="space-y-2 pt-2">
              <span className="text-[11px] font-mono uppercase tracking-wider text-[#a08e7a] block">
                {activeStep.python_view.title}
              </span>

              <div className="grid grid-cols-3 gap-2">
                {activeStep.python_view.offsets.map((slot, i) => (
                  <div
                    key={i}
                    className={`rounded-xl p-3 text-center transition-all ${
                      slot.selected
                        ? "bg-[#c2fb4d]/15 border-2 border-[#c2fb4d] shadow-md"
                        : "bg-[#111319] border border-[#534434]/30 opacity-60"
                    }`}
                  >
                    <div
                      className={`text-[10px] font-mono uppercase ${
                        slot.selected ? "text-[#c2fb4d] font-bold" : "text-[#a08e7a]"
                      }`}
                    >
                      {slot.label}
                    </div>
                    <div
                      className={`text-lg font-bold font-mono my-0.5 ${
                        slot.selected ? "text-[#e2e2ea]" : "text-[#d8c3ad]"
                      }`}
                    >
                      {slot.value}
                    </div>
                    <div
                      className={`text-[10px] font-mono ${
                        slot.selected ? "text-[#c2fb4d]" : "text-[#a08e7a]"
                      }`}
                    >
                      {slot.note}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Ground Truth Result Box */}
          <div className="mt-4 p-4 rounded-xl bg-[#111319] border border-[#c2fb4d]/40 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-[#c2fb4d] text-[22px]">check</span>
              <div>
                <div className="text-[11px] font-mono text-[#a08e7a]">Runtime Truth STDOUT</div>
                <div className="text-base font-bold font-mono text-[#c2fb4d]">
                  [ {activeStep.python_view.output || currentProblem.expected_output || "20"} ]
                </div>
              </div>
            </div>
            <span className="text-[10px] font-mono uppercase px-2.5 py-1 rounded-full bg-[#c2fb4d]/20 border border-[#c2fb4d]/40 text-[#c2fb4d] font-bold">
              CPython Invariant
            </span>
          </div>
        </div>
      </div>

      {/* Explanation & Pedagogical Intervention Bar */}
      <div className="bg-[#1d1f26] rounded-2xl p-6 md:p-8 mb-8 border border-[#534434]/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2 max-w-2xl">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-[#e2e2ea]">Why?</span>
            <span className="text-[#a08e7a]">•</span>
            <span className="text-xs uppercase font-mono text-[#c2fb4d] font-semibold">
              Core Mental Model
            </span>
          </div>
          <p className="text-xs md:text-sm text-[#d8c3ad] leading-relaxed">
            Python list indexes start at <strong className="text-[#e2e2ea]">0, not 1</strong>. The
            index represents the memory offset: how many items to skip from the base memory address.
            When you write <code className="text-[#c2fb4d] bg-[#0c0e14] px-1.5 py-0.5 rounded font-mono">a[1]</code>,
            Python skips the first item (<code className="text-[#e2e2ea]">10</code>) and accesses the second item (<code className="text-[#e2e2ea]">20</code>).
          </p>
        </div>

        {/* Bayesian Probability meter */}
        <div className="w-full md:w-64 shrink-0 bg-[#111319] p-3 rounded-xl border border-[#534434]/30">
          <BayesianBar probability={0.78} misconceptionName="1-Based Indexing" />
        </div>
      </div>

      {/* Primary Action Button */}
      <div className="flex flex-col items-center justify-center space-y-3 pt-2">
        <button
          onClick={() => setShowDiscriminatorModal(true)}
          className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-[#c2fb4d] text-[#0c0e14] font-bold text-sm hover:bg-[#d4fc79] transition-all shadow-[0_0_24px_rgba(194,251,77,0.35)] hover:shadow-[0_0_32px_rgba(194,251,77,0.5)] cursor-pointer"
        >
          <span>Got it — Let&apos;s Fix This</span>
          <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
        </button>

        <span className="text-xs text-[#a08e7a] font-mono">
          Triggers an invariant transfer challenge to verify resolution
        </span>
      </div>

      {/* Interactive Transfer Challenge Modal */}
      {showDiscriminatorModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-fadeIn">
          <div className="w-full max-w-lg bg-[#1d1f26] border border-[#534434] rounded-2xl p-6 md:p-8 space-y-6 shadow-2xl relative">
            <div className="flex items-center justify-between border-b border-[#534434]/40 pb-3">
              <span className="text-xs font-mono uppercase text-[#c2fb4d] font-semibold flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">verified</span>
                Discriminator Transfer Check
              </span>
              <button
                onClick={() => setShowDiscriminatorModal(false)}
                className="text-[#a08e7a] hover:text-[#e2e2ea]"
              >
                <span className="material-symbols-outlined text-[20px]">close</span>
              </button>
            </div>

            <div className="space-y-3">
              <h3 className="text-lg font-bold text-[#e2e2ea]">
                Now apply the invariant:
              </h3>
              <p className="text-xs text-[#d8c3ad]">
                Given this new string array, what will Python print?
              </p>

              <div className="bg-[#0c0e14] p-3 rounded-lg font-mono text-xs text-[#e2e2ea] border border-[#534434]/40">
                items = [&quot;alpha&quot;, &quot;beta&quot;, &quot;gamma&quot;]
                <br />
                print(items[0])
              </div>
            </div>

            {/* Discriminator options */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: '"alpha"', val: "'alpha'", note: "Offset 0 (first element)" },
                { label: '"beta"', val: "'beta'", note: "Second element" },
                { label: '"gamma"', val: "'gamma'", note: "Third element" },
                { label: "IndexError", val: "IndexError", note: "Exception" },
              ].map((opt) => (
                <button
                  key={opt.val}
                  onClick={() => handleDiscriminatorSubmit(opt.val)}
                  className={`p-3 rounded-xl border text-left font-mono transition-all ${
                    discriminatorAnswer === opt.val
                      ? opt.val === "'alpha'"
                        ? "bg-[#10b981]/20 border-[#10b981] text-[#10b981]"
                        : "bg-[#ef4444]/20 border-[#ef4444] text-[#ef4444]"
                      : "bg-[#111319] border-[#534434]/40 text-[#d8c3ad] hover:text-[#e2e2ea] hover:border-[#a08e7a]"
                  }`}
                >
                  <div className="font-bold text-sm text-[#e2e2ea]">{opt.label}</div>
                  <div className="text-[10px] text-[#a08e7a] mt-0.5">{opt.note}</div>
                </button>
              ))}
            </div>

            {/* Result feedback */}
            {resolvedStatus !== null && (
              <div
                className={`p-4 rounded-xl border text-xs font-mono animate-fadeIn space-y-2 ${
                  resolvedStatus
                    ? "bg-[#10b981]/15 border-[#10b981] text-[#10b981]"
                    : "bg-[#ef4444]/15 border-[#ef4444] text-[#ef4444]"
                }`}
              >
                <div className="font-bold text-sm flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[18px]">
                    {resolvedStatus ? "check_circle" : "cancel"}
                  </span>
                  <span>
                    {resolvedStatus
                      ? "Cognitive Invariant Verified!"
                      : "Still mapping 1 to the first slot. Try again!"}
                  </span>
                </div>
                <p className="text-[#d8c3ad] text-[11px] leading-relaxed">
                  {resolvedStatus
                    ? "Your Bayesian posterior has dropped from 78% -> 18%. Misconception state updated to: Suspected Resolved."
                    : "Remember: offset 0 points to the very first item at the beginning of the memory buffer."}
                </p>

                {resolvedStatus && (
                  <div className="pt-2 flex justify-end">
                    <Link
                      href="/progress"
                      className="px-3.5 py-1.5 rounded-lg bg-[#c2fb4d] text-[#0c0e14] font-bold text-xs hover:bg-[#d4fc79]"
                    >
                      View in Mastery Dashboard →
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function TraceAnalysisPage() {
  return (
    <Suspense
      fallback={
        <div className="flex-1 flex items-center justify-center p-12">
          <div className="flex items-center gap-3 font-mono text-sm text-[#c2fb4d]">
            <span className="w-4 h-4 border-2 border-[#c2fb4d] border-t-transparent rounded-full animate-spin"></span>
            <span>Loading Dual Trace Inspection...</span>
          </div>
        </div>
      }
    >
      <TraceAnalysisContent />
    </Suspense>
  );
}
