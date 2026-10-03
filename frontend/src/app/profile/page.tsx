"use client";

import Link from "next/link";
import { ACTIVE_MISCONCEPTIONS, PROBLEMS } from "@/lib/data";
import MisconceptionBadge from "@/components/MisconceptionBadge";

export default function LearnerProfilePage() {
  const sessionHistory = [
    {
      id: "sess_01",
      item_id: "i1",
      date: "Today, 10:45 AM",
      problem: "List Element Extraction (GGL-PY-101)",
      answer: "10",
      real_output: "20",
      status: "Divergence Identified",
      misconception: "1-Based Ordinal Indexing",
      resolved: false,
    },
    {
      id: "sess_02",
      item_id: "i1",
      date: "Today, 10:48 AM",
      problem: "Array Offset Discriminator (GGL-PY-102)",
      answer: "'alpha'",
      real_output: "'alpha'",
      status: "Invariant Verified",
      misconception: "None (Resolved)",
      resolved: true,
    },
    {
      id: "sess_03",
      item_id: "i3",
      date: "Yesterday, 4:20 PM",
      problem: "Late-Binding Loop Closures (AMZ-PY-315)",
      answer: "[4, 4, 4]",
      real_output: "[4, 4, 4]",
      status: "Invariant Verified",
      misconception: "None (Resolved)",
      resolved: true,
    },
    {
      id: "sess_04",
      item_id: "i4",
      date: "Oct 2, 2026",
      problem: "String In-Place Modification (MSFT-PY-108)",
      answer: "hello",
      real_output: "hello",
      status: "Invariant Verified",
      misconception: "None (Resolved)",
      resolved: true,
    },
  ];

  return (
    <div className="w-full flex-1 max-w-7xl mx-auto px-4 md:px-8 py-8 md:py-16 space-y-12">
      {/* Profile Header */}
      <div className="rounded-3xl bg-[#1d1f26] border border-[#534434]/40 p-6 md:p-8 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
        <div
          className="absolute -top-24 right-10 w-80 h-80 rounded-full blur-3xl pointer-events-none -z-10"
          style={{ backgroundColor: "rgba(194, 251, 77, 0.08)" }}
        />

        <div className="flex items-center gap-5">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#c2fb4d]/30 to-[#818cf8]/30 border-2 border-[#c2fb4d] flex items-center justify-center text-[#c2fb4d] text-2xl font-extrabold shadow-lg">
            AR
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl md:text-3xl font-extrabold text-[#e2e2ea]">Alex Rivera</h1>
              <span className="text-[11px] font-mono text-[#c2fb4d] bg-[#c2fb4d]/10 border border-[#c2fb4d]/30 px-2 py-0.5 rounded-full font-semibold">
                Cognitive Level: L4
              </span>
            </div>
            <p className="text-xs md:text-sm text-[#d8c3ad]">
              Python Core Systems Software Engineer • Preparing for FAANG Senior Roles
            </p>
            <div className="flex items-center gap-4 text-xs font-mono text-[#a08e7a] pt-1">
              <span className="flex items-center gap-1 text-[#f59e0b]">
                <span className="material-symbols-outlined text-[16px]">local_fire_department</span>
                14 Days Streak
              </span>
              <span>•</span>
              <span className="text-[#10b981] flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px]">verified</span>
                38 Concepts Mastered
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-3 self-stretch md:self-auto">
          <button className="flex-1 md:flex-none px-4 py-2 rounded-xl bg-[#111319] border border-[#534434]/40 text-xs font-mono text-[#d8c3ad] hover:text-[#e2e2ea] hover:bg-[#282a30] transition-colors flex items-center justify-center gap-1.5">
            <span className="material-symbols-outlined text-[16px]">edit</span>
            <span>Edit Profile</span>
          </button>
          <Link
            href="/practice"
            className="flex-1 md:flex-none px-4 py-2 rounded-xl bg-[#c2fb4d] text-[#0c0e14] text-xs font-mono font-bold hover:bg-[#d4fc79] transition-all shadow flex items-center justify-center gap-1.5"
          >
            <span>Resume Studio</span>
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </Link>
        </div>
      </div>

      {/* Key Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-5 space-y-2">
          <span className="text-xs font-mono text-[#a08e7a] uppercase tracking-wider block">
            Mastered Invariants
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold font-mono text-[#e2e2ea]">38 / 42</span>
            <span className="text-xs font-mono text-[#10b981]">(90%)</span>
          </div>
          <p className="text-[11px] text-[#a08e7a]">Verified across 112 discriminator variants</p>
        </div>

        <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-5 space-y-2">
          <span className="text-xs font-mono text-[#a08e7a] uppercase tracking-wider block">
            Practice Streak
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold font-mono text-[#f59e0b]">14 Days</span>
            <span className="text-xs font-mono text-[#a08e7a]">Active</span>
          </div>
          <p className="text-[11px] text-[#a08e7a]">Top 4% cognitive momentum (Best: 32)</p>
        </div>

        <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-5 space-y-2">
          <span className="text-xs font-mono text-[#a08e7a] uppercase tracking-wider block">
            Primary Target Track
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-extrabold font-mono text-[#38bdf8]">Google L5</span>
          </div>
          <p className="text-[11px] text-[#a08e7a]">Python Core & Memory Offsets Pathway</p>
        </div>
      </div>

      {/* Current Concepts in Focus */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-[#e2e2ea]">Active Cognitive Concepts</h2>
          <Link href="/progress" className="text-xs font-mono text-[#c2fb4d] hover:underline">
            View full progress dashboard →
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {ACTIVE_MISCONCEPTIONS.slice(0, 3).map((concept) => (
            <div
              key={concept.id}
              className="p-5 rounded-2xl bg-[#1d1f26] border border-[#534434]/40 space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-[#a08e7a]">{concept.id}</span>
                <MisconceptionBadge state={concept.state} size="sm" />
              </div>
              <h3 className="font-bold text-sm text-[#e2e2ea]">{concept.name}</h3>
              <p className="text-xs text-[#d8c3ad] line-clamp-2">{concept.description}</p>
              <div className="pt-2">
                <div className="flex justify-between text-[11px] font-mono text-[#a08e7a] mb-1">
                  <span>Posterior:</span>
                  <span className="text-[#c2fb4d] font-bold">
                    {Math.round(concept.posterior * 100)}%
                  </span>
                </div>
                <div className="h-1.5 w-full bg-[#111319] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#10b981] to-[#c2fb4d] rounded-full"
                    style={{ width: `${Math.round(concept.posterior * 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Session History Log */}
      <div className="rounded-2xl bg-[#1d1f26] border border-[#534434]/40 p-6 space-y-6 shadow-xl">
        <div className="flex items-center justify-between border-b border-[#534434]/30 pb-4">
          <div className="space-y-1">
            <h2 className="text-lg font-bold text-[#e2e2ea]">Recent Diagnostic History</h2>
            <p className="text-xs text-[#a08e7a]">
              Historical trace evaluations and cognitive divergence recordings.
            </p>
          </div>
          <span className="text-xs font-mono text-[#a08e7a]">4 Recent Attempts</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b border-[#534434]/30 text-[#a08e7a] pb-2">
                <th className="py-2.5 font-semibold">TIMESTAMP</th>
                <th className="py-2.5 font-semibold">PROBLEM</th>
                <th className="py-2.5 font-semibold">YOUR PREDICTION</th>
                <th className="py-2.5 font-semibold">RUNTIME TRUTH</th>
                <th className="py-2.5 font-semibold">STATUS</th>
                <th className="py-2.5 font-semibold text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#534434]/20">
              {sessionHistory.map((sess) => (
                <tr key={sess.id} className="hover:bg-[#111319]/50 transition-colors">
                  <td className="py-3 text-[#a08e7a]">{sess.date}</td>
                  <td className="py-3 font-semibold text-[#e2e2ea]">{sess.problem}</td>
                  <td className="py-3 text-[#d8c3ad] font-bold">
                    <code className="bg-[#111319] px-2 py-0.5 rounded border border-[#534434]/30">
                      {sess.answer}
                    </code>
                  </td>
                  <td className="py-3 text-[#c2fb4d] font-bold">
                    <code className="bg-[#111319] px-2 py-0.5 rounded border border-[#534434]/30">
                      {sess.real_output}
                    </code>
                  </td>
                  <td className="py-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${
                        sess.resolved
                          ? "bg-[#10b981]/20 text-[#10b981] border border-[#10b981]/40"
                          : "bg-[#ef4444]/20 text-[#ef4444] border border-[#ef4444]/40"
                      }`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-current"></span>
                      {sess.status}
                    </span>
                  </td>
                  <td className="py-3 text-right">
                    <Link
                      href={`/trace?problem=${sess.item_id}&prediction=${encodeURIComponent(
                        sess.answer
                      )}`}
                      className="text-[#c2fb4d] hover:underline flex items-center justify-end gap-1 font-bold"
                    >
                      <span>Review Trace</span>
                      <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
