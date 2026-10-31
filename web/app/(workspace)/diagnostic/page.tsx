'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Compass,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  ArrowLeft,
  Send,
  Sparkles,
  BookOpen,
  Award,
  RotateCcw,
} from 'lucide-react';

interface DiagnosticQuestion {
  question_id: string;
  concept_id: string;
  chapter: string;
  prompt: string;
  expected_answer?: string;
}

const DEFAULT_QUESTIONS: DiagnosticQuestion[] = [
  {
    question_id: 'diag_q1_reflection',
    concept_id: 'c_reflection_refraction',
    chapter: 'Light - Reflection and Refraction',
    prompt: 'According to the laws of reflection, what is the angle of reflection if the angle of incidence is 45 degrees?',
    expected_answer: '45 degrees',
  },
  {
    question_id: 'diag_q2_electric_current',
    concept_id: 'c_electric_current',
    chapter: 'Electricity',
    prompt: 'What is the electric current flowing when 1 Coulomb of charge passes through a cross-section per second?',
    expected_answer: '1 A',
  },
  {
    question_id: 'diag_q3_ohms_law',
    concept_id: 'c_ohms_law',
    chapter: 'Electricity',
    prompt: "According to Ohm's Law at constant temperature, what is the mathematical formula relating potential difference V, current I, and resistance R?",
    expected_answer: 'V = IR',
  },
  {
    question_id: 'diag_q4_lens_power',
    concept_id: 'c_lens_formula',
    chapter: 'Light - Reflection and Refraction',
    prompt: 'What is the SI unit of power of a lens having focal length expressed in meters?',
    expected_answer: 'Dioptre',
  },
  {
    question_id: 'diag_q5_magnetic_field',
    concept_id: 'c_magnetic_fields',
    chapter: 'Magnetic Effects of Electric Current',
    prompt: 'What is the conventional direction of magnetic field lines outside a bar magnet?',
    expected_answer: 'North to South',
  },
  {
    question_id: 'diag_q6_flemings_rules',
    concept_id: 'c_flemings_rules',
    chapter: 'Magnetic Effects of Electric Current',
    prompt: "In Fleming's Left-Hand Rule, which finger represents the direction of the magnetic field?",
    expected_answer: 'Forefinger',
  },
];

interface AnswerState {
  answer: string;
  reasoning: string;
}

interface SubmitResult {
  status: string;
  session_id: string;
  score: number;
  concept_mastery: Record<string, number>;
  recommendations?: Array<{ concept_id: string; name: string; chapter?: string }>;
}

export default function DiagnosticPage() {
  const [sessionId, setSessionId] = useState<string>('diag_session_init');
  const [questions, setQuestions] = useState<DiagnosticQuestion[]>(DEFAULT_QUESTIONS);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, AnswerState>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<SubmitResult | null>(null);

  // Initialize diagnostic session
  useEffect(() => {
    let isMounted = true;
    async function startSession() {
      try {
        const res = await fetch('/api/diagnostic/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ syllabus: 'class10_physics' }),
        });
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            if (data.session_id) setSessionId(data.session_id);
            if (Array.isArray(data.questions) && data.questions.length > 0) {
              setQuestions(data.questions);
            }
          }
        }
      } catch {
        // Safe offline / fallback behavior
      }
    }
    startSession();
    return () => {
      isMounted = false;
    };
  }, []);

  const currentQ = questions[currentIndex] || DEFAULT_QUESTIONS[0];
  const currentAnswer = answers[currentQ.question_id] || { answer: '', reasoning: '' };

  const handleInputChange = (field: 'answer' | 'reasoning', value: string) => {
    setAnswers((prev) => ({
      ...prev,
      [currentQ.question_id]: {
        ...prev[currentQ.question_id],
        [field]: value,
      },
    }));
  };

  const answeredCount = Object.values(answers).filter(
    (a) => a?.answer?.trim().length > 0
  ).length;

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const payloadAnswers: Record<string, { answer: string; reasoning: string }> = {};
      questions.forEach((q) => {
        payloadAnswers[q.question_id] = {
          answer: answers[q.question_id]?.answer || '',
          reasoning: answers[q.question_id]?.reasoning || '',
        };
      });

      const res = await fetch(`/api/diagnostic/${sessionId}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: payloadAnswers }),
      });

      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else {
        // Local calculation fallback
        let correctCount = 0;
        const mastery: Record<string, number> = {};
        questions.forEach((q) => {
          const userAns = (answers[q.question_id]?.answer || '').trim().toLowerCase();
          const expected = (q.expected_answer || '').trim().toLowerCase();
          const isCorrect = userAns === expected;
          if (isCorrect) correctCount++;
          mastery[q.concept_id] = isCorrect ? 0.601 : 0.176;
        });

        const score = correctCount / questions.length;
        setResult({
          status: 'completed',
          session_id: sessionId,
          score,
          concept_mastery: mastery,
        });
      }
    } catch {
      // Local fallback on network failure
      let correctCount = 0;
      const mastery: Record<string, number> = {};
      questions.forEach((q) => {
        const userAns = (answers[q.question_id]?.answer || '').trim().toLowerCase();
        const expected = (q.expected_answer || '').trim().toLowerCase();
        const isCorrect = userAns === expected;
        if (isCorrect) correctCount++;
        mastery[q.concept_id] = isCorrect ? 0.601 : 0.176;
      });

      setResult({
        status: 'completed',
        session_id: sessionId,
        score: correctCount / questions.length,
        concept_mastery: mastery,
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (result) {
    const scorePct = Math.round(result.score * 100);
    const masteryEntries = Object.entries(result.concept_mastery || {});

    return (
      <div className="min-h-screen bg-background text-foreground px-4 py-8">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 sm:p-8 shadow-sm text-center">
            <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
              <Award className="h-7 w-7" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-foreground">
              Diagnostic Calibration Complete
            </h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Initial Bayesian Knowledge Tracing (BKT) priors calibrated from your milestone answers
            </p>

            <div className="mt-6 flex flex-wrap items-center justify-center gap-6 border-y border-border py-4">
              <div>
                <p className="text-xs text-muted-foreground">Diagnostic Score</p>
                <p className="text-3xl font-extrabold text-foreground">{scorePct}%</p>
              </div>
              <div className="h-8 w-px bg-border hidden sm:block" />
              <div>
                <p className="text-xs text-muted-foreground">Calibrated Concepts</p>
                <p className="text-3xl font-extrabold text-primary">{masteryEntries.length}</p>
              </div>
              <div className="h-8 w-px bg-border hidden sm:block" />
              <div>
                <p className="text-xs text-muted-foreground">Session Status</p>
                <span className="inline-block px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
                  Calibrated
                </span>
              </div>
            </div>

            {/* Concept Mastery Radar / Bar breakdown */}
            <div className="mt-6 text-left space-y-4">
              <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Initial Concept Mastery Radar ($P(L)$)
              </h3>

              <div className="space-y-3">
                {masteryEntries.map(([cid, val]) => {
                  const pct = Math.round(val * 100);
                  const isHigh = val >= 0.5;
                  const label = cid.replace('c_', '').replace(/_/g, ' ');

                  return (
                    <div key={cid} className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="font-medium capitalize text-foreground">{label}</span>
                        <span className={`font-semibold ${isHigh ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                          {pct}%
                        </span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${isHigh ? 'bg-emerald-500' : 'bg-amber-500'}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                href="/learning"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow transition-colors hover:bg-primary/90"
              >
                <span>Continue to Learning Path</span>
                <ArrowRight className="h-4 w-4" />
              </Link>
              <button
                type="button"
                onClick={() => {
                  setResult(null);
                  setCurrentIndex(0);
                  setAnswers({});
                }}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-background px-4 py-2.5 text-sm font-medium text-foreground hover:bg-muted transition-colors"
              >
                <RotateCcw className="h-4 w-4" />
                <span>Retake Diagnostic</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground px-4 py-8">
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center border border-primary/20">
              <Compass className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-foreground">
                Class 10 Physics Diagnostic Assessment
              </h1>
              <p className="text-xs text-muted-foreground">
                Answer each milestone question and articulate your reasoning step-by-step
              </p>
            </div>
          </div>
          <span className="text-xs font-semibold text-muted-foreground">
            {answeredCount} of {questions.length} answered
          </span>
        </div>

        {/* Progress Bar & Question Step Indicators */}
        <div className="space-y-2">
          <div className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-primary h-full transition-all duration-300"
              style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
          <div className="flex items-center justify-between gap-1">
            {questions.map((q, idx) => {
              const isAnswered = (answers[q.question_id]?.answer || '').trim().length > 0;
              const isCurrent = idx === currentIndex;
              return (
                <button
                  key={q.question_id}
                  type="button"
                  onClick={() => setCurrentIndex(idx)}
                  className={`flex-1 py-1 text-center text-[11px] font-semibold rounded transition-colors ${
                    isCurrent
                      ? 'bg-primary text-primary-foreground'
                      : isAnswered
                      ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300'
                      : 'bg-muted text-muted-foreground hover:bg-muted/80'
                  }`}
                >
                  Q{idx + 1}
                </button>
              );
            })}
          </div>
        </div>

        {/* Question Card */}
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between gap-2 border-b border-border pb-3">
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1 rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-foreground">
                <BookOpen className="h-3 w-3" />
                {currentQ.chapter}
              </span>
            </div>
            <span className="text-xs font-bold text-muted-foreground">
              Question {currentIndex + 1} of {questions.length}
            </span>
          </div>

          <div>
            <h2 className="text-base sm:text-lg font-medium text-foreground leading-relaxed">
              {currentQ.prompt}
            </h2>
          </div>

          {/* Student Answer Input */}
          <div className="space-y-2">
            <label
              htmlFor="student-answer"
              className="block text-xs font-semibold text-foreground uppercase tracking-wider"
            >
              Your Answer
            </label>
            <input
              id="student-answer"
              type="text"
              value={currentAnswer.answer}
              onChange={(e) => handleInputChange('answer', e.target.value)}
              placeholder="e.g. 45 degrees, 1 A, V = IR, Dioptre..."
              className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground shadow-sm outline-none focus:border-ring focus:ring-1 focus:ring-ring"
            />
          </div>

          {/* Step-by-Step Reasoning Input */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label
                htmlFor="student-reasoning"
                className="block text-xs font-semibold text-foreground uppercase tracking-wider"
              >
                Step-by-Step Reasoning
              </label>
              <span className="text-[11px] text-muted-foreground">
                Used to diagnose reasoning misconceptions
              </span>
            </div>
            <textarea
              id="student-reasoning"
              rows={4}
              value={currentAnswer.reasoning}
              onChange={(e) => handleInputChange('reasoning', e.target.value)}
              placeholder="Explain how you arrived at this conclusion (e.g. formula applied, sign conventions, physical principles)..."
              className="w-full rounded-xl border border-border bg-background p-3 text-sm text-foreground placeholder:text-muted-foreground shadow-sm outline-none focus:border-ring focus:ring-1 focus:ring-ring resize-y"
            />
          </div>

          {/* Navigation & Submit Buttons */}
          <div className="flex items-center justify-between pt-3 border-t border-border">
            <button
              type="button"
              disabled={currentIndex === 0}
              onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3.5 py-2 text-xs font-medium text-foreground hover:bg-muted disabled:opacity-40 disabled:pointer-events-none transition-colors"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              <span>Previous</span>
            </button>

            <div className="flex items-center gap-2">
              {currentIndex < questions.length - 1 ? (
                <button
                  type="button"
                  onClick={() => setCurrentIndex((prev) => Math.min(questions.length - 1, prev + 1))}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground shadow hover:bg-primary/90 transition-colors"
                >
                  <span>Next</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              ) : null}

              <button
                type="button"
                disabled={submitting}
                onClick={handleSubmit}
                className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 text-xs font-semibold shadow transition-colors disabled:opacity-50"
              >
                <Send className="h-3.5 w-3.5" />
                <span>{submitting ? 'Submitting...' : 'Submit Assessment'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
