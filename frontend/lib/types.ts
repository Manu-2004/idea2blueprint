export type Screen =
  | "landing"
  | "auth"
  | "dashboard"
  | "templates"
  | "new"
  | "generating"
  | "spec";

export type AuthMode = "login" | "signup";

export type FormFields = {
  idea: string;
  who: string;
  problem: string;
  platform: string;
  features: string;
  budget: string;
  comfort: string;
};

export type QuestionKey = Exclude<keyof FormFields, "idea">;

export type Template = {
  kicker: string;
  title: string;
  body: string;
  meta: string;
  form: FormFields;
};

export type Question = {
  key: QuestionKey;
  label: string;
  help: string;
  choices: string[];
};

export type SectionItem = { text: string };
export type SectionGroup = { label: string; items: SectionItem[] };
export type Section = {
  id: string;
  num: string;
  title: string;
  lead: string;
  groups: SectionGroup[];
};

export type Spec = {
  title: string;
  summary: string;
  sections: Section[];
};

export type JobStatus = "pending" | "running" | "done" | "failed";

export type JobErrorType =
  | "openai_rate_limit"
  | "openai_timeout"
  | "openai_content_policy"
  | "openai_error"
  | "internal_error";

export type JobError = {
  type: JobErrorType;
  message: string;
};

export type ProgressInfo = {
  step: number;
  revision_round: number;
  max_revision_rounds: number;
};

export type JobCreateResponse = {
  job_id: string;
  status: JobStatus;
};

export type JobStatusResponse = {
  status: JobStatus;
  progress: ProgressInfo;
  spec: Spec | null;
  error: JobError | null;
  created_at: string;
  updated_at: string;
};

export type SpecJobSummary = {
  id: string;
  title: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
};

export type User = {
  id: string;
  name: string;
  email: string;
};

export type AuthResponse = {
  token: string;
  user: User;
};
