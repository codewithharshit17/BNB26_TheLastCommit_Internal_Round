import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "RE:LEARN — Cognitive Mental Model Diagnostics for Python",
  description: "Identify how you reason about Python execution invariants. Dual-trace diagnostics, Bayesian misconception tracking, and transfer probe verification.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#111319] text-[#e2e2ea] min-h-screen flex flex-col antialiased selection:bg-[#c2fb4d]/20 selection:text-[#c2fb4d]">
        <Navbar />
        <main className="w-full flex-1 pt-16 flex flex-col">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
