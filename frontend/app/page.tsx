"use client";

import { useEffect, useRef, useState } from "react";
import { clearToken, createSpecJob, getSpecJob, getToken, listSpecJobs } from "../lib/api";
import { login, logout as logoutRequest, me, signup } from "../lib/auth";
import { QUESTIONS, SAMPLE_SPEC, TEMPLATES } from "../lib/data";
import type { AuthMode, FormFields, JobError, Screen, Spec, SpecJobSummary, User } from "../lib/types";
import { Landing } from "../components/Landing";
import { AuthScreen } from "../components/AuthScreen";
import { AppShell } from "../components/AppShell";
import { Dashboard } from "../components/Dashboard";
import { Templates } from "../components/Templates";
import { NewSpecForm } from "../components/NewSpecForm";
import { Generating } from "../components/Generating";
import { SpecView } from "../components/SpecView";
import { ExportDialog } from "../components/ExportDialog";

const POLL_INTERVAL_MS = 2000;

export default function Home() {
  const [screen, setScreen] = useState<Screen>("landing");
  const [authMode, setAuthMode] = useState<AuthMode>("signup");
  const [authChecked, setAuthChecked] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [form, setForm] = useState<FormFields>({ ...TEMPLATES.saas.form });
  const [formSource, setFormSource] = useState("Blank spec");
  const [step, setStep] = useState(0);
  const [genStep, setGenStep] = useState(0);
  const [genError, setGenError] = useState<JobError | null>(null);
  const [revisionRound, setRevisionRound] = useState(0);
  const [maxRevisionRounds, setMaxRevisionRounds] = useState(0);
  const [spec, setSpec] = useState<Spec | null>(null);
  const [specs, setSpecs] = useState<SpecJobSummary[]>([]);
  const [specsLoading, setSpecsLoading] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [format, setFormat] = useState("PDF");
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

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

  useEffect(() => {
    if (screen !== "dashboard" || !user) return;
    setSpecsLoading(true);
    listSpecJobs()
      .then(setSpecs)
      .catch(() => setSpecs([]))
      .finally(() => setSpecsLoading(false));
  }, [screen, user]);

  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);

  const go = (next: Screen) => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (next === "spec") setSpec((current) => current ?? SAMPLE_SPEC);
    setScreen(next);
    setGenStep(0);
    setStep(0);
  };

  const useTemplate = (key: string) => {
    const t = TEMPLATES[key];
    setStep(0);
    setForm({ ...t.form });
    setFormSource("From template · " + t.title);
    setScreen("new");
  };

  const pollJob = (jobId: string) => {
    if (timerRef.current) clearInterval(timerRef.current);

    const tick = async () => {
      try {
        const job = await getSpecJob(jobId);
        setGenStep((prev) => Math.max(prev, job.progress.step));
        setRevisionRound(job.progress.revision_round);
        setMaxRevisionRounds(job.progress.max_revision_rounds);

        if (job.status === "done" && job.spec) {
          if (timerRef.current) clearInterval(timerRef.current);
          setSpec(job.spec);
          go("spec");
        } else if (job.status === "failed") {
          if (timerRef.current) clearInterval(timerRef.current);
          setGenError(job.error ?? { type: "internal_error", message: "Something went wrong generating the spec." });
        }
      } catch {
        if (timerRef.current) clearInterval(timerRef.current);
        setGenError({ type: "internal_error", message: "Lost connection while generating your spec." });
      }
    };

    tick();
    timerRef.current = setInterval(tick, POLL_INTERVAL_MS);
  };

  const generate = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setGenStep(0);
    setGenError(null);
    setRevisionRound(0);
    setMaxRevisionRounds(0);
    setScreen("generating");

    createSpecJob(form)
      .then(({ job_id }) => pollJob(job_id))
      .catch(() => {
        setGenError({
          type: "internal_error",
          message: "Couldn't start spec generation. Is the backend running?",
        });
      });
  };

  const openSpec = (id: string) => {
    if (timerRef.current) clearInterval(timerRef.current);
    getSpecJob(id)
      .then((job) => {
        if (job.status === "done" && job.spec) {
          setSpec(job.spec);
          go("spec");
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
      go("landing");
    });
  };

  const setField = (key: keyof FormFields, value: string) => {
    setForm((f) => ({ ...f, [key]: value }));
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
        <Landing onSignup={() => { setAuthMode("signup"); setScreen("auth"); }} onSampleSpec={() => go("spec")} />
      )}

      {screen === "auth" && (
        <AuthScreen
          authMode={authMode}
          onSetLogin={() => setAuthMode("login")}
          onSetSignup={() => setAuthMode("signup")}
          onSubmit={handleAuthSubmit}
        />
      )}

      {(screen === "dashboard" || screen === "templates" || screen === "new" || screen === "generating" || screen === "spec") && (
        <AppShell screen={screen} user={user} onGo={go} onNew={() => go("new")} onLogout={handleLogout}>
          {screen === "dashboard" && (
            <Dashboard
              specs={specs}
              loading={specsLoading}
              onOpenSpec={openSpec}
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
              onIdeaChange={(value) => setField("idea", value)}
              onChoiceSelect={(key, value) => setField(key, value)}
              onCustomChange={(key, value) => setField(key, value)}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}
          {screen === "generating" && (
            <Generating
              genStep={genStep}
              error={genError}
              onRetry={generate}
              revisionRound={revisionRound}
              maxRevisionRounds={maxRevisionRounds}
            />
          )}
          {screen === "spec" && spec && (
            <SpecView
              title={spec.title}
              summary={spec.summary}
              sections={spec.sections}
              onRegenerate={() => go("new")}
              onOpenExport={() => setShowExport(true)}
            />
          )}
        </AppShell>
      )}

      {showExport && spec && (
        <ExportDialog spec={spec} format={format} onSelectFormat={setFormat} onClose={() => setShowExport(false)} />
      )}
    </>
  );
}
