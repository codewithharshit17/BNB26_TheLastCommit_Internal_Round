"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import confetti from "canvas-confetti";
import SyntaxCode from "@/components/SyntaxCode";
import BayesianBar from "@/components/BayesianBar";
import { PROBLEMS } from "@/lib/data";
import { answer } from "@/lib/api";
import type { AnswerResponse } from "@/lib/types";

function PracticeContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const problemRef = searchParams.get("problem");

  const initialIndex = problemRef
    ? Math.max(
        0,
        PROBLEMS.findIndex((p) => p.problem_ref === problemRef || p.item_id === problemRef)
      )
    : 0;

  const [currentIndex, setCurrentIndex] = useState(initialIndex >= 0 ? initialIndex : 0);
  const currentProblem = PROBLEMS[currentIndex] || PROBLEMS[0];

  const [predictedOutput, setPredictedOutput] = useState("");
  const [confidence, setConfidence] = useState<number>(4);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [evaluationResult, setEvaluationResult] = useState<AnswerResponse | null>(null);

  useEffect(() => {
    if (problemRef) {
      const idx = PROBLEMS.findIndex(
        (p) => p.problem_ref === problemRef || p.item_id === problemRef
      );
      if (idx !== -1) {
        setCurrentIndex(idx);
        setPredictedOutput("");
        setEvaluationResult(null);
      }
    }
  }, [problemRef]);

  const handleSelectOption = (opt: string) => {
    setPredictedOutput(opt);
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!predictedOutput.trim() || isSubmitting) return;

    setIsSubmitting(true);

    try {
      const res = await answer({
        session_id: "demo-session-1",
        item_id: currentProblem.item_id,
        answer: predictedOutput.trim(),
        confidence,
      });

      setEvaluationResult(res);

      const isCorrect = predictedOutput.trim() === currentProblem.expected_output?.trim();
      if (isCorrect) {
        confetti({
          particleCount: 80,
          spread: 70,
          origin: { y: 0.6 },
          colors: ["#c2fb4d", "#10b981", "#38bdf8", "#ffc174"],
        });
      }
    } catch (err) {
      console.error("Evaluation error:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      handleSubmit();
    }
  };

  const nextProblem = () => {
    const nextIdx = (currentIndex + 1) % PROBLEMS.length;
    setCurrentIndex(nextIdx);
    setPredictedOutput("");
    setEvaluationResult(null);
  };

  const prevProblem = () => {
    const prevIdx = (currentIndex - 1 + PROBLEMS.length) % PROBLEMS.length;
    setCurrentIndex(prevIdx);
    setPredictedOutput("");
    setEvaluationResult(null);
  };

  const isCorrect =
    evaluationResult &&
    predictedOutput.trim() === currentProblem.expected_output?.trim();

  return (
    <div className="w-full flex-1 max-w-7xl mx-auto px-4 md:px-8 py-8 md:py-12">
      {/* Top Breadcrumb & Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-[#534434]/30">
        <div className="flex items-center gap-2 text-xs font-mono text-[#a08e7a]">
          <Link href="/tracks" className="hover:text-[#c2fb4d] transition-colors">
            Tracks
          </Link>
          <span>/</span>
          <span className="text-[#d8c3ad]">{currentProblem.category || "Core Python"}</span>
          <span>/</span>
          <span className="text-[#c2fb4d] font-bold">
            {currentProblem.problem_ref || `Q0${currentIndex + 1}`}
          </span>
        </div>

        {/* Problem Navigator pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 md:pb-0">
          <button
            onClick={prevProblem}
            className="p-1 rounded bg-[#1d1f26] text-[#d8c3ad] hover:text-[#e2e2ea] hover:bg-[#282a30] transition-colors"
            title="Previous Problem"
          >
            <span className="material-symbols-outlined text-[16px]">chevron_left</span>
          </button>

          {PROBLEMS.map((p, idx) => (
            <button
              key={p.item_id}
              onClick={() => {
                setCurrentIndex(idx);
                setPredictedOutput("");
                setEvaluationResult(null);
              }}
              className={`px-2.5 py-1 rounded text-xs font-mono transition-all ${
                currentIndex === idx
                  ? "bg-[#c2fb4d] text-[#0c0e14] font-bold shadow-md"
                  : "bg-[#1d1f26] text-[#a08e7a] hover:text-[#e2e2ea]"
              }`}
            >
              Q0{idx + 1}
            </button>
          ))}

          <button
            onClick={nextProblem}
            className="p-1 rounded bg-[#1d1f26] text-[#d8c3ad] hover:text-[#e2e2ea] hover:bg-[#282a30] transition-colors"
            title="Next Problem"
          >
            <span className="material-symbols-outlined text-[16px]">chevron_right</span>
          </button>
        </div>
      </div>

      {/* Main Studio Grid */}
      <div className="pt-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Problem Code View */}
        <div className="lg:col-span-7 space-y-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium bg-[#1d1f26] text-[#38bdf8] border border-[#38bdf8]/30">
                {currentProblem.company || "Google"} Target
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-mono font-medium bg-[#1d1f26] text-[#f59e0b] border border-[#f59e0b]/30">
                {currentProblem.difficulty || "Diagnostic"}
              </span>
              <span className="text-xs text-[#a08e7a] font-mono">
                Model Family: {currentProblem.family}
              </span>
            </div>

            <h1 className="text-2xl md:text-3xl font-extrabold text-[#e2e2ea] tracking-tight">
              {currentProblem.prompt}
            </h1>
            <p className="text-xs md:text-sm text-[#d8c3ad]">
              Predict what Python outputs before running the code. Do not use a compiler.
            </p>
          </div>

          {/* Code block viewer */}
          <div className="shadow-2xl">
            <SyntaxCode code={currentProblem.code} filename="main.py" />
          </div>

          {/* Quick Explanation / Hint when evaluated */}
          {evaluationResult && (
            <div
              className={`p-4 rounded-xl border space-y-2 animate-fadeIn ${
                isCorrect
                  ? "bg-[#10b981]/10 border-[#10b981]/40"
                  : "bg-[#ef4444]/10 border-[#ef4444]/40"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className={`material-symbols-outlined text-[20px] ${
                      isCorrect ? "text-[#10b981]" : "text-[#ef4444]"
                    }`}
                  >
                    {isCorrect ? "check_circle" : "error"}
                  </span>
                  <span className="font-bold text-sm text-[#e2e2ea]">
                    {isCorrect
                      ? "Correct! Invariant Mastered"
                      : "Divergence Detected! Python Evaluates Differently"}
                  </span>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-[#111319] text-[#d8c3ad]">
                  Runtime Output:{" "}
                  <strong className="text-[#c2fb4d]">{currentProblem.expected_output}</strong>
                </span>
              </div>

              <p className="text-xs text-[#d8c3ad] leading-relaxed pt-1">
                {currentProblem.explanation}
              </p>

              <div className="pt-2 flex flex-wrap items-center justify-between gap-3">
                <BayesianBar
                  probability={
                    isCorrect
                      ? 0.05
                      : evaluationResult.posterior[evaluationResult.top] || 0.78
                  }
                  misconceptionName={
                    isCorrect
                      ? "Zero Divergence"
                      : evaluationResult.top.replace(/_/g, " ")
                  }
                />

                <div className="flex items-center gap-3">
                  {!isCorrect && (
                    <Link
                      href={`/trace?problem=${currentProblem.item_id}&prediction=${encodeURIComponent(
                        predictedOutput
                      )}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#ef4444] text-white text-xs font-bold hover:bg-[#dc2626] transition-colors shadow"
                    >
                      <span>Deep Dive in Dual Trace</span>
                      <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                    </Link>
                  )}
                  <button
                    onClick={nextProblem}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#c2fb4d] text-[#0c0e14] text-xs font-bold hover:bg-[#d4fc79] transition-colors"
                  >
                    <span>Next Challenge</span>
                    <span className="material-symbols-outlined text-[16px]">navigate_next</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Interactive Prediction Console */}
        <div className="lg:col-span-5 rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 space-y-6 shadow-xl">
          <div className="flex items-center justify-between border-b border-[#534434]/30 pb-3">
            <span className="text-xs uppercase font-mono tracking-wider font-semibold text-[#c2fb4d] flex items-center gap-1.5">
              <span className="material-symbols-outlined text-[16px]">terminal</span>
              Prediction Console
            </span>
            <span className="text-[10px] font-mono text-[#a08e7a]">Exact STDOUT Match</span>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Input field */}
            <div className="space-y-2">
              <label
                htmlFor="terminal-answer"
                className="text-xs font-mono text-[#d8c3ad] flex items-center justify-between"
              >
                <span>Your Predicted Output</span>
                <span className="text-[10px] text-[#a08e7a]">Case & whitespace sensitive</span>
              </label>

              <div className="relative flex items-center">
                <span className="absolute left-3.5 text-[#c2fb4d] font-mono text-sm font-bold select-none">
                  &gt;
                </span>
                <input
                  id="terminal-answer"
                  type="text"
                  value={predictedOutput}
                  onChange={(e) => setPredictedOutput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="e.g. 10 or 20"
                  className="w-full pl-8 pr-4 py-3 rounded-xl bg-[#0c0e14] border border-[#534434]/60 text-sm font-mono text-[#e2e2ea] placeholder-[#534434] focus:outline-none focus:border-[#c2fb4d] focus:ring-1 focus:ring-[#c2fb4d] transition-all"
                  autoComplete="off"
                />
              </div>
            </div>

            {/* Quick Suggestions Chips */}
            {currentProblem.options && currentProblem.options.length > 0 && (
              <div className="space-y-2">
                <span className="text-[11px] font-mono text-[#a08e7a] block">
                  Click a candidate value:
                </span>
                <div className="flex flex-wrap gap-2">
                  {currentProblem.options.map((opt) => (
                    <button
                      type="button"
                      key={opt}
                      onClick={() => handleSelectOption(opt)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-mono border transition-all ${
                        predictedOutput === opt
                          ? "bg-[#c2fb4d]/20 border-[#c2fb4d] text-[#c2fb4d] font-bold"
                          : "bg-[#111319] border-[#534434]/40 text-[#d8c3ad] hover:text-[#e2e2ea] hover:border-[#a08e7a]"
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Confidence Rating (1-5 scale) */}
            <div className="space-y-3 pt-2 border-t border-[#534434]/20">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono text-[#d8c3ad] flex items-center gap-1">
                  <span className="material-symbols-outlined text-[15px] text-[#f59e0b]">psychology</span>
                  Confidence Rating
                </span>
                <span className="font-mono text-[#c2fb4d] font-bold text-xs">
                  {confidence === 1 && "1 — Guessing"}
                  {confidence === 2 && "2 — Unsure"}
                  {confidence === 3 && "3 — Neutral"}
                  {confidence === 4 && "4 — Fairly Sure"}
                  {confidence === 5 && "5 — 100% Confident"}
                </span>
              </div>

              {/* 5-part button group */}
              <div className="grid grid-cols-5 gap-1.5 p-1 rounded-xl bg-[#111319] border border-[#534434]/30">
                {[1, 2, 3, 4, 5].map((level) => (
                  <button
                    type="button"
                    key={level}
                    onClick={() => setConfidence(level)}
                    className={`py-2 rounded-lg text-xs font-mono font-bold transition-all text-center ${
                      confidence === level
                        ? "bg-[#c2fb4d] text-[#0c0e14] shadow-md"
                        : "text-[#a08e7a] hover:text-[#e2e2ea] hover:bg-[#1d1f26]"
                    }`}
                  >
                    {level}
                  </button>
                ))}
              </div>
              <div className="flex justify-between text-[10px] text-[#534434] font-mono px-1">
                <span>1 (Pure guess)</span>
                <span>5 (Absolute certainty)</span>
              </div>
            </div>

            {/* Submit Action */}
            <div className="pt-2 space-y-2">
              <button
                type="submit"
                disabled={!predictedOutput.trim() || isSubmitting}
                className={`w-full py-3.5 rounded-xl font-bold text-sm font-mono flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  !predictedOutput.trim() || isSubmitting
                    ? "bg-[#282a30] text-[#a08e7a] cursor-not-allowed"
                    : "bg-[#c2fb4d] text-[#0c0e14] hover:bg-[#d4fc79] shadow-[0_0_20px_rgba(194,251,77,0.3)] hover:shadow-[0_0_30px_rgba(194,251,77,0.5)]"
                }`}
              >
                {isSubmitting ? (
                  <>
                    <span className="w-4 h-4 border-2 border-[#0c0e14] border-t-transparent rounded-full animate-spin"></span>
                    <span>Running Sandbox...</span>
                  </>
                ) : (
                  <>
                    <span>Analyze Answer</span>
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </>
                )}
              </button>

              <div className="text-center text-[10px] font-mono text-[#a08e7a]">
                Press <kbd className="px-1.5 py-0.5 rounded bg-[#111319] border border-[#534434]/40 text-[#e2e2ea]">Enter ↵</kbd> to submit response
              </div>
            </div>
          </form>

          {/* Quick Links */}
          <div className="pt-4 border-t border-[#534434]/30 flex items-center justify-between text-xs text-[#a08e7a] font-mono">
            <Link href="/trace" className="hover:text-[#c2fb4d] transition-colors flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">insights</span>
              <span>Dual Trace Inspector</span>
            </Link>
            <Link href="/progress" className="hover:text-[#c2fb4d] transition-colors flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">grid_view</span>
              <span>Mastery Progress</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PracticePage() {
  return (
    <Suspense
      fallback={
        <div className="flex-1 flex items-center justify-center p-12">
          <div className="flex items-center gap-3 font-mono text-sm text-[#c2fb4d]">
            <span className="w-4 h-4 border-2 border-[#c2fb4d] border-t-transparent rounded-full animate-spin"></span>
            <span>Loading Practice Studio...</span>
          </div>
        </div>
      }
    >
      <PracticeContent />
    </Suspense>
  );
}
