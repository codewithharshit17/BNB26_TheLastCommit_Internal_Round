"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function LearnPage() {
  const router = useRouter();

  useEffect(() => {
    // Navigate to the interactive Practice & Diagnostic studio.
    router.replace("/practice");
  }, [router]);

  return (
    <div className="flex-1 flex items-center justify-center p-12">
      <div className="flex items-center gap-3 font-mono text-sm text-[#c2fb4d]">
        <span className="w-4 h-4 border-2 border-[#c2fb4d] border-t-transparent rounded-full animate-spin"></span>
        <span>Loading Re:Learn Diagnostic Engine...</span>
      </div>
    </div>
  );
}