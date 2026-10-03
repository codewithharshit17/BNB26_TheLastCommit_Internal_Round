import type { AnswerRequest, AnswerResponse, InterventionResponse, LearnerResponse, SessionStart } from "./types";
import * as mock from "./mock";
const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
const mocked = process.env.NEXT_PUBLIC_MOCK === "1";
async function get<T>(path: string): Promise<T> { const response = await fetch(`${base}${path}`); return response.json(); }
export async function startSession(): Promise<SessionStart> { return mocked ? mock.start as SessionStart : get("/session/start"); }
export async function answer(payload: AnswerRequest): Promise<AnswerResponse> { return mocked ? mock.answerProbe as AnswerResponse : fetch(`${base}/answer`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) }).then(r => r.json()); }
export async function getLearner(sessionId: string): Promise<LearnerResponse> { return mocked ? mock.learner as LearnerResponse : get(`/learner/${sessionId}`); }
export async function getIntervention(id: string): Promise<InterventionResponse> { return mocked ? mock.intervention as InterventionResponse : get(`/intervention/${id}`); }
export async function health(): Promise<{ ok: boolean }> { return get("/health"); }
