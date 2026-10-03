import Link from "next/link";

export default function Footer() {
  return (
    <footer className="w-full bg-[#0c0e14] border-t border-[#534434]/30 mt-auto py-12 px-4 md:px-8">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-[#e2e2ea]">
              RE<span className="text-[#c2fb4d]">:</span>LEARN
            </span>
            <span className="text-[11px] font-mono text-[#a08e7a] bg-[#191b22] px-2 py-0.5 rounded border border-[#534434]/30">
              v4.12-pro
            </span>
          </div>
          <p className="text-xs text-[#d8c3ad]/70 max-w-sm">
            AI-driven cognitive misconception diagnostics and dual-trace compiler telemetry for software engineers.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-6 text-xs text-[#d8c3ad]">
          <Link href="/" className="hover:text-[#c2fb4d] transition-colors">Home</Link>
          <Link href="/practice" className="hover:text-[#c2fb4d] transition-colors">Practice IDE</Link>
          <Link href="/trace" className="hover:text-[#c2fb4d] transition-colors">Trace Analysis</Link>
          <Link href="/tracks" className="hover:text-[#c2fb4d] transition-colors">Company Tracks</Link>
          <Link href="/progress" className="hover:text-[#c2fb4d] transition-colors">Mastery Progress</Link>
          <Link href="/profile" className="hover:text-[#c2fb4d] transition-colors">Learner Profile</Link>
        </div>

        <div className="flex items-center gap-3 text-xs text-[#a08e7a]">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded bg-[#191b22] border border-[#534434]/40 font-mono">
            <span className="w-2 h-2 rounded-full bg-[#10b981]"></span>
            <span>Engine: Online</span>
          </div>
          <span className="font-mono text-[11px]">42,000+ traces evaluated</span>
        </div>
      </div>
    </footer>
  );
}
