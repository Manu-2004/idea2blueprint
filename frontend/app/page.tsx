"use client";

import { useEffect, useRef, useState } from "react";
import { GEN_LABELS, QUESTIONS, TEMPLATES } from "../lib/data";
import type { AuthMode, FormFields, Screen } from "../lib/types";
import { Landing } from "../components/Landing";
import { AuthScreen } from "../components/AuthScreen";
import { AppShell } from "../components/AppShell";
import { Dashboard } from "../components/Dashboard";
import { Templates } from "../components/Templates";
import { NewSpecForm } from "../components/NewSpecForm";
import { Generating } from "../components/Generating";
import { SpecView } from "../components/SpecView";
import { ExportDialog } from "../components/ExportDialog";

const SPEC_TITLE = "Invoice chaser for freelancers";

export default function Home() {
  const [screen, setScreen] = useState<Screen>("landing");
  const [authMode, setAuthMode] = useState<AuthMode>("signup");
  const [form, setForm] = useState<FormFields>({ ...TEMPLATES.saas.form });
  const [formSource, setFormSource] = useState("Blank spec");
  const [step, setStep] = useState(0);
  const [genStep, setGenStep] = useState(0);
  const [showExport, setShowExport] = useState(false);
  const [format, setFormat] = useState("PDF");
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const go = (next: Screen) => {
    if (timerRef.current) clearInterval(timerRef.current);
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

  const generate = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setGenStep(0);
    setScreen("generating");
    timerRef.current = setInterval(() => {
      setGenStep((s) => {
        const next = s + 1;
        if (next > GEN_LABELS.length) {
          if (timerRef.current) clearInterval(timerRef.current);
          setScreen("spec");
          return 0;
        }
        return next;
      });
    }, 850);
  };

  useEffect(() => () => { if (timerRef.current) clearInterval(timerRef.current); }, []);

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
          onSubmit={() => go("dashboard")}
        />
      )}

      {(screen === "dashboard" || screen === "templates" || screen === "new" || screen === "generating" || screen === "spec") && (
        <AppShell screen={screen} onGo={go} onNew={() => go("new")}>
          {screen === "dashboard" && (
            <Dashboard
              onOpenSpec={() => go("spec")}
              onOpenForm={() => go("new")}
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
          {screen === "generating" && <Generating genStep={genStep} />}
          {screen === "spec" && (
            <SpecView specTitle={SPEC_TITLE} onRegenerate={() => go("new")} onOpenExport={() => setShowExport(true)} />
          )}
        </AppShell>
      )}

      {showExport && (
        <ExportDialog format={format} onSelectFormat={setFormat} onClose={() => setShowExport(false)} />
      )}
    </>
  );
}
