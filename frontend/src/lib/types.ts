export type ItemKind = "diagnostic" | "probe" | "transfer" | "discriminator" | "retest";
export type Item = { item_id: string; kind: ItemKind; family: string; prompt: string; code: string; problem_ref: string | null };
export type SessionStart = { session_id: string; item: Item };
export type AnswerRequest = { session_id: string; item_id: string; answer: string; confidence: number };
export type AnswerResponse = { posterior: Record<string, number>; top: string; bank_ids: number[]; real_output: string; believed_output: string; believed_source: string; next: { action: "probe" | "intervene" | "reassess" | "done"; item?: Item; misconception?: string | null } };
export type LearnerResponse = { misconceptions: Array<{ id: string; state: string; posterior_history: number[]; evidence: Record<string, unknown> }> };
export type InterventionResponse = { title: string; bank_description: string; contrast_code: string; real_output: string; believed_output: string; steps: string[]; takeaway: string };
