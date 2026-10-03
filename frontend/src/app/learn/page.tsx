import { startSession } from "../../lib/api";
export default async function Learn() { const data = await startSession(); return <main className="p-10"><h1 className="text-2xl">Learn</h1><p className="mt-4">{data.item.prompt}</p><pre className="mt-4 rounded bg-slate-800 p-4">{data.item.code}</pre></main>; }
