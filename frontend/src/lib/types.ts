export type ItemKind =
  | "diagnostic"
  | "probe"
  | "transfer"
  | "discriminator"
  | "retest";

export type Item = {
  item_id: string;
  kind: ItemKind;
  family: string;
  prompt: string;
  code: string;
  problem_ref: string | null;

  // Practice/frontend metadata
  title?: string;
  category?: string;
  difficulty?: "Diagnostic" | "Probe" | "Edge Case" | "Transfer";
  company?: string;
  options?: string[];
  expected_output?: string;
  misconceptions_map?: Record<string, string>;
  explanation?: string;
};

export type SessionStart = {
  session_id: string;
  item: Item;
};

export type AnswerRequest = {
  session_id: string;
  item_id: string;
  answer: string;
  confidence: number;
};

export type AnswerResponse = {
  posterior: Record<string, number>;
  top: string;
  bank_ids: number[];
  real_output: string;
  believed_output: string;
  believed_source: string;

  // Flat diagnosis fields used by the ML integration.
  next_action?: "probe" | "intervene" | "reassess" | "done" | null;
  next_item?: Item | null;
  next_misconception?: string | null;

  // Nested response retained for backend/frontend compatibility.
  next: {
    action: "probe" | "intervene" | "reassess" | "done";
    item?: Item | null;
    misconception?: string | null;
  };
};

export type MisconceptionState =
  | "active"
  | "intervened"
  | "suspected_resolved"
  | "confirmed_resolved"
  | "relapsed";

export type MisconceptionInfo = {
  id: string;
  name: string;
  description: string;
  state: MisconceptionState;
  posterior: number;
  posterior_history: number[];
  bank_ids: number[];
  evidence: {
    discriminator_passes: number;
    surface_forms: string[];
    delayed_retest: boolean;
  };
};

export type LearnerResponse = {
  misconceptions: Array<{
    id: string;
    state: string;
    posterior_history: number[];
    evidence: Record<string, unknown>;
  }>;
};

export type InterventionResponse = {
  title: string;
  bank_description: string;
  contrast_code: string;
  real_output: string;
  believed_output: string;
  steps: string[];
  takeaway: string;
};

export type TraceStep = {
  step: number;
  line: number;
  code: string;
  description: string;
  learner_view: {
    title: string;
    mapping: Array<{
      label: string;
      value: string;
      note: string;
      selected?: boolean;
    }>;
    output?: string;
  };
  python_view: {
    title: string;
    offsets: Array<{
      label: string;
      value: string;
      note: string;
      selected?: boolean;
    }>;
    output?: string;
  };
  divergence?: boolean;
};

export type ProblemTrack = {
  id: string;
  company: string;
  title: string;
  problem_count: number;
  active?: boolean;
  accent: string;
  description: string;
};