import type { AnswerRequest, AnswerResponse, InterventionResponse, LearnerResponse, SessionStart } from "./types";
import * as mock from "./mock";
import { PROBLEMS, ACTIVE_MISCONCEPTIONS } from "./data";

const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
const forceMock = process.env.NEXT_PUBLIC_MOCK === "1";

async function safeFetch<T>(path: string, options: RequestInit = {}, fallback: T): Promise<T> {
  if (forceMock || typeof window === "undefined") {
    // In build-time prerendering or forced mock, always use fallback
    return fallback;
  }
  try {
    const res = await fetch(`${base}${path}`, {
      ...options,
      headers: {
        "content-type": "application/json",
        ...(options.headers || {}),
      },
    });
    if (!res.ok) {
      return fallback;
    }
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export async function startSession(): Promise<SessionStart> {
  const fallback: SessionStart = (mock.start as SessionStart) || {
    session_id: "demo-session",
    item: PROBLEMS[0],
  };
  return safeFetch<SessionStart>("/session/start", { method: "POST" }, fallback);
}

export async function answer(payload: AnswerRequest): Promise<AnswerResponse> {
  const currentProblem = PROBLEMS.find((p) => p.item_id === payload.item_id) || PROBLEMS[0];
  const isCorrect = payload.answer.trim() === currentProblem.expected_output?.trim();
  const detectedMisconception = currentProblem.misconceptions_map?.[payload.answer.trim()] || null;

  const fallback: AnswerResponse = {
    posterior: {
      correct: isCorrect ? 0.95 : 0.05,
      index_1_based: detectedMisconception === "index_1_based" ? 0.78 : 0.05,
      mutable_default: detectedMisconception === "recreated_default_arg" ? 0.84 : 0.04,
      closure_early_binding: detectedMisconception === "closure_early_binding" ? 0.81 : 0.03,
      noop_method: detectedMisconception === "noop_method" ? 0.76 : 0.02,
      assign_copies: detectedMisconception === "assign_copies" ? 0.72 : 0.03,
      add_before_div: detectedMisconception === "add_before_div" ? 0.69 : 0.02,
      unknown: isCorrect ? 0.02 : detectedMisconception ? 0.05 : 0.6,
    },
    top: isCorrect ? "correct" : detectedMisconception || "unknown",
    bank_ids: [15, 66],
    real_output: currentProblem.expected_output || "20",
    believed_output: payload.answer,
    believed_source: `${currentProblem.code}\n# Believed model divergence`,
    next: {
      action: isCorrect ? "probe" : "intervene",
      item: PROBLEMS[(PROBLEMS.findIndex((p) => p.item_id === currentProblem.item_id) + 1) % PROBLEMS.length],
      misconception: detectedMisconception,
    },
  };

  return safeFetch<AnswerResponse>(
    "/answer",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    fallback
  );
}

export async function getLearner(sessionId: string): Promise<LearnerResponse> {
  const fallback: LearnerResponse = {
    misconceptions: ACTIVE_MISCONCEPTIONS.map((m) => ({
      id: m.id,
      state: m.state,
      posterior_history: m.posterior_history,
      evidence: m.evidence,
    })),
  };
  return safeFetch<LearnerResponse>(`/learner/${sessionId}`, { method: "GET" }, fallback);
}

export async function getIntervention(id: string): Promise<InterventionResponse> {
  const fallback: InterventionResponse = (mock.intervention as InterventionResponse) || {
    title: "Python indexes start at zero",
    bank_description: "The first list element is at index 0, not index 1.",
    contrast_code: "a[0] # first element (offset 0)\na[1] # second element (offset 1)",
    real_output: "10\n20",
    believed_output: "20\n30",
    steps: ["Count memory offsets from zero.", "Index n is base_ptr + n * sizeof(pointer)."],
    takeaway: "In Python, index represents the offset from the beginning of the memory buffer.",
  };
  return safeFetch<InterventionResponse>(`/intervention/${id}`, { method: "GET" }, fallback);
}

export async function health(): Promise<{ ok: boolean }> {
  return safeFetch<{ ok: boolean }>("/health", { method: "GET" }, { ok: true });
}
