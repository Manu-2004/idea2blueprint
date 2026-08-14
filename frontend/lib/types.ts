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

export type SpecItem = {
  title: string;
  meta: string;
  stage: string;
  pct: string;
  status: "Ready" | "Draft";
  open?: boolean;
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
