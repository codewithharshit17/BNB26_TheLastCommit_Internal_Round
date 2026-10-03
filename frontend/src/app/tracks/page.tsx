"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { COMPANY_TRACKS, PROBLEMS } from "@/lib/data";

function TracksExplorerContent() {
  const searchParams = useSearchParams();
  const selectedCompanyParam = searchParams.get("company");

  const [activeCompany, setActiveCompany] = useState<string>(
    selectedCompanyParam || "all"
  );
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const categories = [
    "all",
    "Lists & Indexing",
    "Functions & Scope",
    "Closures & Scoping",
    "Strings & Immutability",
    "Object References",
    "Compiler Semantics",
  ];

  const filteredProblems = PROBLEMS.filter((problem) => {
    const matchesCompany =
      activeCompany === "all" ||
      (problem.company && problem.company.toLowerCase() === activeCompany.toLowerCase());
    const matchesCategory =
      activeCategory === "all" || problem.category === activeCategory;
    const matchesSearch =
      searchQuery === "" ||
      problem.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      problem.prompt.toLowerCase().includes(searchQuery.toLowerCase()) ||
      problem.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      problem.problem_ref?.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesCompany && matchesCategory && matchesSearch;
  });

  return (
    <div className="w-full flex-1 max-w-7xl mx-auto px-4 md:px-8 py-8 md:py-16 space-y-10">
      {/* Header section */}
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-xs font-mono text-[#a08e7a]">
          <span className="uppercase tracking-widest text-[#c2fb4d] font-semibold">
            INTERVIEW PREPARATION TRACKS
          </span>
          <span>/</span>
          <span>v4.12</span>
        </div>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-[#e2e2ea] tracking-tight">
              Practice problems that feel real.
            </h1>
            <p className="text-sm md:text-base text-[#d8c3ad] mt-2 max-w-2xl">
              Explore Python challenges crafted to probe how you reason through edge-cases, memory pointers, and compiler invariants under pressure.
            </p>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#1d1f26] border border-[#534434]/50 text-xs font-mono shrink-0">
            <span className="text-[#a08e7a]">Target Track:</span>
            <span className="text-[#c2fb4d] font-bold">FAANG + Tier 1</span>
            <span className="text-[#10b981] flex items-center gap-0.5">
              <span className="material-symbols-outlined text-[14px]">verified</span>
              109 in Catalog
            </span>
          </div>
        </div>
      </div>

      {/* Curated Employer Pathways (Cards) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono uppercase tracking-wider text-[#a08e7a] flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[16px]">domain</span>
            Curated Employer Pathways
          </span>
          <span className="text-xs font-mono text-[#d8c3ad]">Click track to filter problems</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <button
            onClick={() => setActiveCompany("all")}
            className={`p-4 rounded-xl border text-left transition-all ${
              activeCompany === "all"
                ? "bg-[#282a30] border-[#c2fb4d] shadow-lg"
                : "bg-[#1d1f26] border-[#534434]/30 hover:border-[#a08e7a]"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="font-bold text-sm text-[#e2e2ea]">All Tracks</span>
              <span className="text-[10px] font-mono text-[#a08e7a]">Catalog</span>
            </div>
            <div className="text-xs text-[#a08e7a] mt-2">All company questions</div>
          </button>

          {COMPANY_TRACKS.map((t) => {
            const isSelected = activeCompany.toLowerCase() === t.company.toLowerCase();
            return (
              <button
                key={t.id}
                onClick={() => setActiveCompany(isSelected ? "all" : t.company)}
                className={`p-4 rounded-xl border text-left transition-all ${
                  isSelected
                    ? "bg-[#282a30] border-[#c2fb4d] shadow-lg"
                    : "bg-[#1d1f26] border-[#534434]/30 hover:border-[#a08e7a]"
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-sm text-[#e2e2ea]">{t.company}</span>
                  <span className="text-[10px] font-mono text-[#c2fb4d]">
                    {t.problem_count} Qs
                  </span>
                </div>
                <div className="text-[11px] text-[#d8c3ad] font-medium line-clamp-1">
                  {t.title}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Search & Category Filter Bar */}
      <div className="bg-[#1d1f26] rounded-2xl p-4 md:p-6 border border-[#534434]/40 space-y-4">
        {/* Search Input */}
        <div className="relative">
          <span className="absolute left-3.5 top-3.5 material-symbols-outlined text-[#a08e7a] text-[18px]">
            search
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search problems by keyword, code token, or problem ID (e.g. GGL-PY-101)..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-[#0c0e14] border border-[#534434]/50 text-sm font-mono text-[#e2e2ea] placeholder-[#534434] focus:outline-none focus:border-[#c2fb4d]"
          />
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs font-mono">
          <span className="text-[#a08e7a] shrink-0 mr-1">Category:</span>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1 rounded-lg transition-all shrink-0 ${
                activeCategory === cat
                  ? "bg-[#c2fb4d] text-[#0c0e14] font-bold shadow-sm"
                  : "bg-[#111319] text-[#d8c3ad] hover:text-[#e2e2ea] hover:bg-[#282a30]"
              }`}
            >
              {cat === "all" ? "All Categories" : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Problem Cards Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-xs font-mono text-[#a08e7a]">
          <span>
            Showing <strong className="text-[#e2e2ea]">{filteredProblems.length}</strong> problems
          </span>
          <span>Click &apos;Solve in Studio&apos; to test your prediction</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredProblems.map((prob) => (
            <div
              key={prob.item_id}
              className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-5 space-y-4 hover:border-[#c2fb4d]/50 transition-all flex flex-col justify-between"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono text-[#c2fb4d] font-bold">
                      {prob.problem_ref}
                    </span>
                    <span className="text-xs font-mono text-[#a08e7a] bg-[#111319] px-2 py-0.5 rounded border border-[#534434]/30">
                      {prob.company || "Google"}
                    </span>
                  </div>
                  <span
                    className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${
                      prob.difficulty === "Diagnostic"
                        ? "bg-[#38bdf8]/10 border-[#38bdf8]/30 text-[#38bdf8]"
                        : prob.difficulty === "Edge Case"
                        ? "bg-[#f59e0b]/10 border-[#f59e0b]/30 text-[#f59e0b]"
                        : "bg-[#a855f7]/10 border-[#a855f7]/30 text-[#a855f7]"
                    }`}
                  >
                    {prob.difficulty}
                  </span>
                </div>

                <h3 className="text-base font-bold text-[#e2e2ea]">{prob.title}</h3>
                <p className="text-xs text-[#d8c3ad] leading-relaxed line-clamp-2">
                  {prob.prompt}
                </p>

                {/* Code preview snippet */}
                <div className="bg-[#0c0e14] p-3 rounded-lg font-mono text-xs text-[#d8c3ad] border border-[#534434]/30 line-clamp-3">
                  <pre className="whitespace-pre overflow-x-hidden">{prob.code}</pre>
                </div>
              </div>

              <div className="pt-4 border-t border-[#534434]/20 flex items-center justify-between">
                <span className="text-xs font-mono text-[#a08e7a]">
                  Category: <span className="text-[#e2e2ea]">{prob.category}</span>
                </span>

                <Link
                  href={`/practice?problem=${prob.problem_ref || prob.item_id}`}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#c2fb4d] text-[#0c0e14] text-xs font-bold hover:bg-[#d4fc79] transition-all shadow-sm"
                >
                  <span>Solve in Studio</span>
                  <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function TracksExplorerPage() {
  return (
    <Suspense
      fallback={
        <div className="flex-1 flex items-center justify-center p-12">
          <div className="flex items-center gap-3 font-mono text-sm text-[#c2fb4d]">
            <span className="w-4 h-4 border-2 border-[#c2fb4d] border-t-transparent rounded-full animate-spin"></span>
            <span>Loading Tracks Explorer...</span>
          </div>
        </div>
      }
    >
      <TracksExplorerContent />
    </Suspense>
  );
}
