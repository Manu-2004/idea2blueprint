"use client";

import { useEffect, useRef, useState } from "react";
import {
  clearToken,
  createSpecJob,
  deleteSpecJob,
  generateFromDraft,
  getSpecJob,
  getSpecUsage,
  getToken,
  listSpecJobs,
  saveDraft,
  submitClarification,
  updateDraft,
} from "../lib/api";
import { login, logout as logoutRequest, me, signup } from "../lib/auth";
import { QUESTIONS, SAMPLE_SPEC, TEMPLATES } from "../lib/data";
import type { AuthMode, ClarificationAnswer, ClarifyingQuestion, FormFields, HandoffResponse, JobError, JobStatus, Screen, Spec, SpecJobSummary, User } from "../lib/types";
import { Landing } from "../components/Landing";
import { AuthScreen } from "../components/AuthScreen";
import { AppShell } from "../components/AppShell";
import { Dashboard } from "../components/Dashboard";
import { Templates } from "../components/Templates";
import { NewSpecForm } from "../components/NewSpecForm";
import { Generating } from "../components/Generating";
import { ClarifyQuestions } from "../components/ClarifyQuestions";
import { SpecView } from "../components/SpecView";
import { ExportDialog } from "../components/ExportDialog";
import { AgentKitDialog } from "../components/AgentKitDialog";
import { ToastStack, type ToastItem, type ToastTone } from "../components/Toast";

const POLL_INTERVAL_MS = 2000;
const BACKGROUND_POLL_MS = 4000;

export default function Home() {
  const [screen, setScreen] = useState<Screen>("landing");
  const [authMode, setAuthMode] = useState<AuthMode>("signup");
  const [authChecked, setAuthChecked] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [form, setForm] = useState<FormFields>({ ...TEMPLATES.saas.form });
  const [formSource, setFormSource] = useState("Blank spec");
  const [step, setStep] = useState(0);
  const [draftId, setDraftId] = useState<string | null>(null);
  const [draftStatus, setDraftStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [genStep, setGenStep] = useState(0);
  const [genError, setGenError] = useState<JobError | null>(null);
  const [revisionRound, setRevisionRound] = useState(0);
  const [maxRevisionRounds, setMaxRevisionRounds] = useState(0);
  const [spec, setSpec] = useState<Spec | null>(null);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [clarifyJobId, setClarifyJobId] = useState<string | null>(null);
  const [clarifyQuestions, setClarifyQuestions] = useState<ClarifyingQuestion[]>([]);
  const [clarifySubmitting, setClarifySubmitting] = useState(false);
  const [handoff, setHandoff] = useState<HandoffResponse | null>(null);
  const [specs, setSpecs] = useState<SpecJobSummary[]>([]);
  const [specsLoading, setSpecsLoading] = useState(false);
  const [specsUsedThisMonth, setSpecsUsedThisMonth] = useState(0);
  const [showExport, setShowExport] = useState(false);
  const [showAgentKit, setShowAgentKit] = useState(false);
  const [format, setFormat] = useState("PDF");
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const activeJobIdRef = useRef<string | null>(null);
  const specsRef = useRef<SpecJobSummary[]>([]);
  const knownStatusesRef = useRef<Map<string, JobStatus>>(new Map());
  const toastIdRef = useRef(0);

  const pushToast = (message: string, tone: ToastTone = "success") => {
    const id = ++toastIdRef.current;
    setToasts((t) => [...t, { id, message, tone }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 5000);
  };
  const dismissToast = (id: number) => setToasts((t) => t.filter((x) => x.id !== id));

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setAuthChecked(true);
      return;
    }
    me()
      .then((u) => {
        setUser(u);
        setScreen("dashboard");
      })
      .catch(() => clearToken())
      .finally(() => setAuthChecked(true));
  }, []);

  const refreshSpecs = () => {
    if (!user) return;
    setSpecsLoading(true);
    listSpecJobs()
      .then(setSpecs)
      .catch(() => setSpecs([]))
      .finally(() => setSpecsLoading(false));
    getSpecUsage()
      .then((usage) => setSpecsUsedThisMonth(usage.specs_used_this_month))
      .catch(() => {});
  };

  useEffect(() => {
    refreshSpecs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  useEffect(() => { specsRef.current = specs; }, [specs]);

  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);

  // Keeps dashboard badges live and fires a "spec ready" notification even after the user
  // has navigated away from the generating screen (which stops the fine-grained poll below).
  useEffect(() => {
    if (!user) return;
    const id = setInterval(() => {
      const hasActive = specsRef.current.some((s) => s.status === "pending" || s.status === "running");
      if (!hasActive) return;
      listSpecJobs()
        .then((next) => {
          for (const job of next) {
            const prevStatus = knownStatusesRef.current.get(job.id);
            if (prevStatus === "pending" || prevStatus === "running") {
              if (job.status === "done") pushToast(`"${job.title}" is ready.`, "success");
              else if (job.status === "failed") pushToast(`"${job.title}" failed to generate.`, "error");
            }
          }
          for (const job of next) knownStatusesRef.current.set(job.id, job.status);
          setSpecs(next);
        })
        .catch(() => {});
    }, BACKGROUND_POLL_MS);
    return () => clearInterval(id);
  }, [user]);

  const go = (next: Screen) => {
    if (timerRef.current) clearInterval(timerRef.current);
    activeJobIdRef.current = null;
    setScreen(next);
    setGenStep(0);
    setStep(0);
  };

  const useTemplate = (key: string) => {
    const t = TEMPLATES[key];
    setStep(0);
    setForm({ ...t.form });
    setFormSource("From template · " + t.title);
    setDraftId(null);
    setDraftStatus("idle");
    setScreen("new");
  };

  const startNewSpec = () => {
    setDraftId(null);
    setDraftStatus("idle");
    go("new");
  };

  const pollJob = (jobId: string) => {
    if (timerRef.current) clearInterval(timerRef.current);
    activeJobIdRef.current = jobId;

    const tick = async () => {
      try {
        const job = await getSpecJob(jobId);
        // The user may have navigated away (or started tracking a different job) while this
        // request was in flight — clearInterval doesn't cancel an already-dispatched fetch, so
        // without this check a late response could yank the user back to a screen they left.
        if (activeJobIdRef.current !== jobId) return;

        setGenStep((prev) => Math.max(prev, job.progress.step));
        setRevisionRound(job.progress.revision_round);
        setMaxRevisionRounds(job.progress.max_revision_rounds);

        if (job.status === "done" && job.spec) {
          if (timerRef.current) clearInterval(timerRef.current);
          activeJobIdRef.current = null;
          setSpec(job.spec);
          setCurrentJobId(jobId);
          setHandoff(null);
          go("spec");
          refreshSpecs();
          pushToast(`"${job.spec.title}" is ready.`, "success");
        } else if (job.status === "failed") {
          if (timerRef.current) clearInterval(timerRef.current);
          activeJobIdRef.current = null;
          setGenError(job.error ?? { type: "internal_error", message: "Something went wrong generating the spec." });
          refreshSpecs();
        } else if (job.status === "needs_input") {
          if (timerRef.current) clearInterval(timerRef.current);
          activeJobIdRef.current = null;
          setClarifyJobId(jobId);
          setClarifyQuestions(job.clarifying_questions ?? []);
          go("clarify");
          refreshSpecs();
        }
      } catch {
        if (activeJobIdRef.current !== jobId) return;
        if (timerRef.current) clearInterval(timerRef.current);
        setGenError({ type: "internal_error", message: "Lost connection while generating your spec." });
      }
    };

    tick();
    timerRef.current = setInterval(tick, POLL_INTERVAL_MS);
  };

  const generate = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    activeJobIdRef.current = null;
    setGenStep(0);
    setGenError(null);
    setRevisionRound(0);
    setMaxRevisionRounds(0);
    setScreen("generating");

    const start = draftId
      ? updateDraft(draftId, form).then(() => generateFromDraft(draftId))
      : createSpecJob(form);

    start
      .then(({ job_id }) => {
        setDraftId(null);
        setDraftStatus("idle");
        refreshSpecs();
        pollJob(job_id);
      })
      .catch(() => {
        setGenError({
          type: "internal_error",
          message: "Couldn't start spec generation. Is the backend running?",
        });
      });
  };

  const handleSubmitClarification = (answers: ClarificationAnswer[]) => {
    if (!clarifyJobId) return;
    setClarifySubmitting(true);
    submitClarification(clarifyJobId, answers)
      .then(({ job_id }) => {
        setClarifySubmitting(false);
        setClarifyJobId(null);
        setClarifyQuestions([]);
        setGenStep(0);
        setGenError(null);
        setRevisionRound(0);
        setMaxRevisionRounds(0);
        setScreen("generating");
        refreshSpecs();
        pollJob(job_id);
      })
      .catch(() => {
        setClarifySubmitting(false);
        pushToast("Couldn't submit your answers — try again.", "error");
      });
  };

  const handleSaveDraft = () => {
    setDraftStatus("saving");
    const save = draftId ? updateDraft(draftId, form) : saveDraft(form);
    save
      .then(({ job_id }) => {
        setDraftId(job_id);
        setDraftStatus("saved");
        refreshSpecs();
      })
      .catch(() => setDraftStatus("error"));
  };

  const handleDeleteSpec = (id: string) => {
    deleteSpecJob(id)
      .then(refreshSpecs)
      .catch(() => window.alert("Couldn't delete that spec — try again."));
  };

  const openSpec = (id: string) => {
    if (timerRef.current) clearInterval(timerRef.current);
    activeJobIdRef.current = null;
    getSpecJob(id)
      .then((job) => {
        if (job.status === "draft") {
          setForm(job.brief);
          setFormSource("Draft");
          setDraftId(id);
          setDraftStatus("idle");
          setStep(0);
          setScreen("new");
          return;
        }
        if (job.status === "done" && job.spec) {
          setSpec(job.spec);
          setCurrentJobId(id);
          setHandoff(job.agent_prompt && job.agents_md ? { agent_prompt: job.agent_prompt, agents_md: job.agents_md } : null);
          go("spec");
          return;
        }
        if (job.status === "needs_input") {
          setClarifyJobId(id);
          setClarifyQuestions(job.clarifying_questions ?? []);
          go("clarify");
          return;
        }
        setGenStep(job.progress.step);
        setRevisionRound(job.progress.revision_round);
        setMaxRevisionRounds(job.progress.max_revision_rounds);
        setGenError(job.status === "failed" ? job.error ?? { type: "internal_error", message: "Something went wrong generating the spec." } : null);
        setScreen("generating");
        if (job.status !== "failed") pollJob(id);
      })
      .catch(() => {
        setGenError({ type: "internal_error", message: "Couldn't load that spec." });
        setScreen("generating");
      });
  };

  const handleAuthSubmit = async (fields: { name: string; email: string; password: string }) => {
    const authedUser = authMode === "signup"
      ? await signup(fields.name, fields.email, fields.password)
      : await login(fields.email, fields.password);
    setUser(authedUser);
    go("dashboard");
  };

  const handleLogout = () => {
    logoutRequest().finally(() => {
      setUser(null);
      setSpecs([]);
      setSpec(null);
      setCurrentJobId(null);
      setHandoff(null);
      go("landing");
    });
  };

  const setField = (key: keyof FormFields, value: string) => {
    setForm((f) => ({ ...f, [key]: value }));
    setDraftStatus((s) => (s === "idle" || s === "saving") ? s : "idle");
  };

  const handleNext = () => {
    if (step === QUESTIONS.length) generate();
    else setStep((s) => s + 1);
  };

  const handleBack = () => {
    if (step === 0) setScreen("dashboard");
    else setStep((s) => s - 1);
  };

  if (!authChecked) return null;

  return (
    <>
      {screen === "landing" && (
        <Landing onSignup={() => { setAuthMode("signup"); setScreen("auth"); }} onSampleSpec={() => { setSpec(SAMPLE_SPEC); setCurrentJobId(null); setHandoff(null); go("spec"); }} />
      )}

      {screen === "auth" && (
        <AuthScreen
          authMode={authMode}
          onSetLogin={() => setAuthMode("login")}
          onSetSignup={() => setAuthMode("signup")}
          onSubmit={handleAuthSubmit}
        />
      )}

      {(screen === "dashboard" || screen === "templates" || screen === "new" || screen === "generating" || screen === "clarify" || screen === "spec") && (
        <AppShell screen={screen} user={user} specsUsed={specsUsedThisMonth} onGo={go} onNew={startNewSpec} onLogout={handleLogout}>
          {screen === "dashboard" && (
            <Dashboard
              specs={specs}
              loading={specsLoading}
              onOpenSpec={openSpec}
              onDeleteSpec={handleDeleteSpec}
              onGoTemplates={() => go("templates")}
              onUseTemplate={useTemplate}
            />
          )}
          {screen === "templates" && <Templates onUseTemplate={useTemplate} />}
          {screen === "new" && (
            <NewSpecForm
              form={form}
              formSource={formSource}
              step={step}
              draftStatus={draftStatus}
              onIdeaChange={(value) => setField("idea", value)}
              onChoiceSelect={(key, value) => setField(key, value)}
              onCustomChange={(key, value) => setField(key, value)}
              onNext={handleNext}
              onBack={handleBack}
              onSaveDraft={handleSaveDraft}
            />
          )}
          {screen === "generating" && (
            <Generating
              genStep={genStep}
              error={genError}
              onRetry={generate}
              onEdit={() => go("new")}
              revisionRound={revisionRound}
              maxRevisionRounds={maxRevisionRounds}
            />
          )}
          {screen === "clarify" && (
            <ClarifyQuestions
              questions={clarifyQuestions}
              submitting={clarifySubmitting}
              onSubmit={handleSubmitClarification}
            />
          )}
          {screen === "spec" && spec && (
            <SpecView
              title={spec.title}
              summary={spec.summary}
              sections={spec.sections}
              onRegenerate={() => go("new")}
              onOpenExport={() => setShowExport(true)}
              onOpenAgentKit={currentJobId ? () => setShowAgentKit(true) : undefined}
            />
          )}
        </AppShell>
      )}

      {showExport && spec && (
        <ExportDialog spec={spec} format={format} onSelectFormat={setFormat} onClose={() => setShowExport(false)} />
      )}

      {showAgentKit && currentJobId && (
        <AgentKitDialog
          jobId={currentJobId}
          initial={handoff}
          onGenerated={setHandoff}
          onClose={() => setShowAgentKit(false)}
        />
      )}

      <ToastStack toasts={toasts} onDismiss={dismissToast} />
    </>
  );
}
