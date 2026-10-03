"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

export default function Navbar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: "Home", href: "/" },
    { name: "Learn", href: "/trace" },
    { name: "Practice", href: "/practice" },
    { name: "Company Tracks", href: "/tracks" },
    { name: "Progress", href: "/progress" },
    { name: "Profile", href: "/profile" },
  ];

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="fixed top-0 inset-x-0 z-50 bg-[#0c0e14]/85 backdrop-blur-xl border-b border-[#534434]/30 shadow-[0_1px_12px_rgba(0,0,0,0.5)]">
      <div className="h-16 max-w-7xl mx-auto px-4 md:px-8 flex items-center justify-between gap-4">
        {/* Left Logo + Nav */}
        <div className="flex items-center gap-6 lg:gap-8">
          <Link href="/" className="flex items-center gap-2 group transition-transform hover:scale-[1.02]">
            <span className="font-headline-sm text-lg md:text-xl text-[#e2e2ea] font-extrabold tracking-tight">
              RE<span className="text-[#c2fb4d]">:</span>LEARN
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-[#c2fb4d]/10 border border-[#c2fb4d]/30 text-[#c2fb4d] text-[11px] font-semibold tracking-wide">
              <span className="material-symbols-outlined text-[12px] text-[#c2fb4d]">auto_awesome</span>
              AI
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const active = isActive(link.href);
              return (
                <Link
                  key={link.name}
                  href={link.href}
                  className={`px-3 py-1.5 rounded-lg text-[13px] font-medium transition-all ${
                    active
                      ? "bg-[#282a30] text-[#c2fb4d] font-semibold shadow-sm border border-[#534434]/40"
                      : "text-[#d8c3ad] hover:text-[#e2e2ea] hover:bg-[#1d1f26]"
                  }`}
                >
                  {link.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 px-2.5 py-1 rounded-full bg-[#191b22] border border-[#534434]/30 text-[11px] text-[#d8c3ad]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse"></span>
            <span>CPython 3.12 Sandboxed</span>
          </div>

          <Link
            href="/practice"
            className="inline-flex items-center justify-center px-3.5 py-1.5 rounded-xl bg-[#c2fb4d] text-[#0c0e14] text-[13px] font-semibold hover:bg-[#d4fc79] transition-all shadow-[0_0_16px_rgba(194,251,77,0.3)] hover:shadow-[0_0_22px_rgba(194,251,77,0.5)] cursor-pointer"
          >
            Start Practice →
          </Link>

          {/* User profile pill */}
          <Link
            href="/profile"
            className="flex items-center gap-2 p-1 pl-2 rounded-full bg-[#1d1f26] border border-[#534434]/40 hover:border-[#c2fb4d]/50 transition-colors"
          >
            <span className="hidden sm:inline-block text-[12px] text-[#e2e2ea] font-medium pr-1">
              Alex R.
            </span>
            <div className="w-7 h-7 rounded-full bg-[#c2fb4d]/20 border border-[#c2fb4d]/60 flex items-center justify-center text-[#c2fb4d] text-[12px] font-bold">
              AR
            </div>
          </Link>

          {/* Mobile menu trigger */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-lg bg-[#1d1f26] text-[#e2e2ea] hover:bg-[#282a30] transition-colors"
            aria-label="Toggle menu"
          >
            <span className="material-symbols-outlined text-[20px]">
              {mobileMenuOpen ? "close" : "menu"}
            </span>
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#0c0e14]/95 border-b border-[#534434]/40 px-4 py-3 space-y-1">
          {navLinks.map((link) => {
            const active = isActive(link.href);
            return (
              <Link
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`block px-3 py-2 rounded-lg text-sm font-medium ${
                  active
                    ? "bg-[#282a30] text-[#c2fb4d] font-semibold"
                    : "text-[#d8c3ad] hover:bg-[#1d1f26]"
                }`}
              >
                {link.name}
              </Link>
            );
          })}
        </div>
      )}
    </header>
  );
}
