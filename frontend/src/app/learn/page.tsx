"use client";

import { FormEvent, useEffect, useState } from "react";
import { answer, getIntervention, startSession } from "../../lib/api";
import { AnswerResponse, Item, SessionStart } from "../../lib/types";
import { ConfidenceSlider } from "../../components/ConfidenceSlider";
import { InterventionCard } from "../../components/InterventionCard";

export default function Learn() {
  const [session, setSession] = useState<SessionStart | null>(null);
  const [item, setItem] = useState<Item | null>(null);
  const [studentAnswer, setStudentAnswer] = useState("");
  const [confidence, setConfidence] = useState(3);
  const [result, setResult] = useState<AnswerResponse | null>(null);
  const [intervention, setIntervention] = useState<{ title: string; takeaway: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    startSession().then(data => { setSession(data); setItem(data.item); }).catch(() => setError("Unable to start a session."));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!session || !item || !studentAnswer.trim()) return;
    setError(null);
    try {
      const diagnosis = await answer({ session_id: session.session_id, item_id: item.item_id, answer: studentAnswer, confidence });
      setResult(diagnosis);
      setStudentAnswer("");
      const nextItem = diagnosis.next_item ?? diagnosis.next.item;
      if (nextItem) setItem(nextItem);
      if ((diagnosis.next_action ?? diagnosis.next.action) === "intervene" && (diagnosis.next_misconception ?? diagnosis.next.misconception)) {
        const id = diagnosis.next_misconception ?? diagnosis.next.misconception;
        if (id) setIntervention(await getIntervention(id));
      }
    } catch {
      setError("The answer could not be submitted.");
    }
  }

  if (!item) return <main className="p-10"><h1 className="text-2xl">Learn</h1><p className="mt-4">Loading session…</p></main>;

  const action = result?.next_action ?? result?.next.action;
  return <main className="max-w-2xl space-y-6 p-10">
    <h1 className="text-2xl">Learn</h1>
    <p>{item.prompt}</p>
    <pre className="rounded bg-slate-800 p-4 text-white">{item.code}</pre>
    <form className="space-y-4" onSubmit={submit}>
      <label className="block">Your answer
        <textarea className="mt-2 w-full rounded border p-2" value={studentAnswer} onChange={event => setStudentAnswer(event.target.value)} />
      </label>
      <label className="block">Confidence: {confidence}
        <ConfidenceSlider value={confidence} onChange={setConfidence} />
      </label>
      <button className="rounded bg-blue-600 px-4 py-2 text-white" type="submit">Check answer</button>
    </form>
    {error && <p role="alert">{error}</p>}
    {result && <section className="space-y-2 rounded border p-4"><p>Top hypothesis: {result.top}</p><p>What Python does: {result.real_output}</p><p>What you thought: {result.believed_output}</p><p>Next action: {action}</p></section>}
    {intervention && <InterventionCard title={intervention.title} takeaway={intervention.takeaway} />}
  </main>;
}
