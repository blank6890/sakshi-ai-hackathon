'use client';

import React, { useEffect, useState, useCallback } from 'react';
import {
  GraduationCap,
  Users,
  TrendingUp,
  AlertTriangle,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { ClassHeatmap, type HeatmapConcept, type HeatmapStudent } from '@/components/teacher/ClassHeatmap';
import { ClassGapsSummary, type ConceptGap } from '@/components/teacher/ClassGapsSummary';
import { MisconceptionBreakdown, type FrequentMisconception } from '@/components/teacher/MisconceptionBreakdown';

const DEFAULT_CONCEPTS: HeatmapConcept[] = [
  { concept_id: 'c_reflection_refraction', concept_name: 'Reflection & Refraction', chapter: 'Light - Reflection and Refraction' },
  { concept_id: 'c_spherical_mirrors', concept_name: 'Spherical Mirrors', chapter: 'Light - Reflection and Refraction' },
  { concept_id: 'c_mirror_formula', concept_name: 'Mirror Formula', chapter: 'Light - Reflection and Refraction' },
  { concept_id: 'c_refraction_lenses', concept_name: 'Refraction & Lenses', chapter: 'Light - Reflection and Refraction' },
  { concept_id: 'c_lens_formula', concept_name: 'Lens Formula', chapter: 'Light - Reflection and Refraction' },
  { concept_id: 'c_electric_charge', concept_name: 'Electric Charge', chapter: 'Electricity' },
  { concept_id: 'c_electric_current', concept_name: 'Electric Current', chapter: 'Electricity' },
  { concept_id: 'c_potential_difference', concept_name: 'Potential Diff (V)', chapter: 'Electricity' },
  { concept_id: 'c_ohms_law', concept_name: "Ohm's Law", chapter: 'Electricity' },
  { concept_id: 'c_resistance_series_parallel', concept_name: 'Series & Parallel R', chapter: 'Electricity' },
  { concept_id: 'c_joules_heating', concept_name: "Joule's Heating", chapter: 'Electricity' },
  { concept_id: 'c_electric_power', concept_name: 'Electric Power', chapter: 'Electricity' },
  { concept_id: 'c_magnetic_fields', concept_name: 'Magnetic Fields', chapter: 'Magnetic Effects of Electric Current' },
  { concept_id: 'c_solenoids', concept_name: 'Solenoids', chapter: 'Magnetic Effects of Electric Current' },
  { concept_id: 'c_flemings_rules', concept_name: "Fleming's Rules", chapter: 'Magnetic Effects of Electric Current' },
];

const DEFAULT_GAPS: ConceptGap[] = [
  {
    concept_id: 'c_resistance_series_parallel',
    concept_name: 'Series & Parallel Resistance',
    chapter: 'Electricity',
    average_mastery: 0.38,
    struggling_student_count: 18,
    struggling_percentage: 72.0,
    common_misconceptions: [
      { misconception_id: 'series_current_consumed', name: 'Current is consumed by series components', count: 14 },
    ],
  },
  {
    concept_id: 'c_ohms_law',
    concept_name: "Ohm's Law (V = IR)",
    chapter: 'Electricity',
    average_mastery: 0.41,
    struggling_student_count: 16,
    struggling_percentage: 64.0,
    common_misconceptions: [
      { misconception_id: 'ohm_r_depends_on_v', name: 'Resistance depends on Voltage or Current', count: 15 },
    ],
  },
  {
    concept_id: 'c_lens_formula',
    concept_name: 'Lens Formula & Magnification',
    chapter: 'Light - Reflection and Refraction',
    average_mastery: 0.44,
    struggling_student_count: 14,
    struggling_percentage: 56.0,
    common_misconceptions: [
      { misconception_id: 'mirror_lens_formula_confusion', name: 'Confusion between lens and mirror sign conventions', count: 12 },
    ],
  },
];

const DEFAULT_MISCONCEPTIONS: FrequentMisconception[] = [
  {
    misconception_id: 'ohm_r_depends_on_v',
    name: 'Resistance depends on Voltage or Current',
    description: "Belief that changing the voltage or current changes the resistor's physical resistance value.",
    remedial_feedback: 'Explain that resistance is an intrinsic geometric/material property (R = ρL/A). Demonstrate that changing V proportionally changes I, keeping R constant.',
    count: 15,
    affected_students: ['Aarav Sharma', 'Ananya Patel', 'Rohan Gupta', 'Aditya Verma', 'Sneha Rao', 'Kavya Iyer', 'Rahul Nair', 'Neha Joshi', 'Devansh Mehta', 'Tanvi Bhat', 'Kabir Sen', 'Isha Chopra', 'Siddharth Jain', 'Meera Pillai', 'Rishi Agarwal'],
  },
  {
    misconception_id: 'series_current_consumed',
    name: 'Current is consumed along series circuits',
    description: 'Students imagine electric current gets used up or diminishes as it flows across successive resistors.',
    remedial_feedback: 'Anchor with the conservation of electric charge: charges cannot disappear. Use the water pipe analogy where volume flow rate is identical at all sequential cross-sections.',
    count: 14,
    affected_students: ['Rohan Gupta', 'Priya Singh', 'Sneha Rao', 'Vikram Malhotra', 'Arjun Reddy', 'Pooja Das', 'Tanvi Bhat', 'Kabir Sen', 'Isha Chopra', 'Meera Pillai', 'Rishi Agarwal', 'Riya Mukherjee', 'Karan Kapoor', 'Anushka Saxena'],
  },
  {
    misconception_id: 'parallel_resistor_additive',
    name: 'Parallel resistance adds up directly (R_eq = R1 + R2)',
    description: 'Applying arithmetic addition to parallel branches instead of reciprocal conductance (1/Req = 1/R1 + 1/R2).',
    remedial_feedback: 'Illustrate that opening additional parallel pathways reduces overall opposition to charge flow, resulting in an equivalent resistance smaller than the smallest branch resistor.',
    count: 13,
    affected_students: ['Aarav Sharma', 'Aditya Verma', 'Rahul Nair', 'Devansh Mehta', 'Siddharth Jain', 'Meera Pillai', 'Rishi Agarwal', 'Manish Pandey', 'Shruti Deshmukh', 'Aryan Ghosh', 'Karan Kapoor', 'Anushka Saxena', 'Tanvi Bhat'],
  },
];

function buildDefaultStudentsAndMatrix(): { students: HeatmapStudent[]; matrix: Record<string, Record<string, number>> } {
  const names = [
    'Aarav Sharma', 'Ananya Patel', 'Rohan Gupta', 'Priya Singh', 'Aditya Verma',
    'Sneha Rao', 'Vikram Malhotra', 'Kavya Iyer', 'Rahul Nair', 'Neha Joshi',
    'Arjun Reddy', 'Pooja Das', 'Devansh Mehta', 'Tanvi Bhat', 'Kabir Sen',
    'Isha Chopra', 'Siddharth Jain', 'Meera Pillai', 'Rishi Agarwal', 'Riya Mukherjee',
    'Karan Kapoor', 'Anushka Saxena', 'Manish Pandey', 'Shruti Deshmukh', 'Aryan Ghosh',
  ];

  const baseProfiles: Record<string, number> = {
    c_reflection_refraction: 0.84,
    c_spherical_mirrors: 0.72,
    c_mirror_formula: 0.58,
    c_refraction_lenses: 0.62,
    c_lens_formula: 0.44,
    c_electric_charge: 0.88,
    c_electric_current: 0.82,
    c_potential_difference: 0.69,
    c_ohms_law: 0.41,
    c_resistance_series_parallel: 0.38,
    c_joules_heating: 0.65,
    c_electric_power: 0.52,
    c_magnetic_fields: 0.76,
    c_solenoids: 0.49,
    c_flemings_rules: 0.55,
  };

  const abilityOffsets = [
    0.18, 0.15, 0.14, 0.12, 0.10,
    0.08, 0.06, 0.04, 0.03, 0.01,
    0.00, -0.02, -0.04, -0.05, -0.07,
    -0.09, -0.11, -0.12, -0.14, -0.16,
    -0.18, -0.19, -0.20, -0.21, -0.22,
  ];

  const students: HeatmapStudent[] = [];
  const matrix: Record<string, Record<string, number>> = {};

  names.forEach((name, idx) => {
    const studentId = `stu_${(idx + 1).toString().padStart(2, '0')}`;
    const offset = abilityOffsets[idx] ?? 0;
    const scores: Record<string, number> = {};

    let sum = 0;
    let count = 0;
    Object.entries(baseProfiles).forEach(([cid, baseVal], cIdx) => {
      const perturbation = (((idx * 7 + cIdx * 11) % 19) - 9) * 0.012;
      const score = Math.max(0.12, Math.min(0.98, Number((baseVal + offset + perturbation).toFixed(2))));
      scores[cid] = score;
      sum += score;
      count += 1;
    });

    const overall = Number((sum / count).toFixed(2));
    students.push({
      student_id: studentId,
      student_name: name,
      overall_mastery: overall,
    });
    matrix[studentId] = scores;
  });

  return { students, matrix };
}

export default function TeacherDashboardPage() {
  const [cohortId, setCohortId] = useState('class-10-a');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cohort summary data
  const [cohortName, setCohortName] = useState('Class 10 - Section A (Physics)');
  const [totalStudents, setTotalStudents] = useState(25);
  const [classAverageMastery, setClassAverageMastery] = useState(0.61);
  const [gaps, setGaps] = useState<ConceptGap[]>(DEFAULT_GAPS);
  const [misconceptions, setMisconceptions] = useState<FrequentMisconception[]>(DEFAULT_MISCONCEPTIONS);

  // Heatmap data
  const defaultHeatmap = buildDefaultStudentsAndMatrix();
  const [concepts, setConcepts] = useState<HeatmapConcept[]>(DEFAULT_CONCEPTS);
  const [students, setStudents] = useState<HeatmapStudent[]>(defaultHeatmap.students);
  const [matrix, setMatrix] = useState<Record<string, Record<string, number>>>(defaultHeatmap.matrix);

  const fetchCohortData = useCallback(async (selectedCohort: string) => {
    setLoading(true);
    setError(null);

    try {
      // Fetch summary
      const summaryRes = await fetch(`/api/teacher/cohorts/${selectedCohort}/summary`).catch(() => null);
      if (summaryRes && summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setCohortName(summaryData.cohort_name || selectedCohort);
        setTotalStudents(summaryData.total_students ?? 25);
        setClassAverageMastery(summaryData.class_average_mastery ?? 0.61);
        if (Array.isArray(summaryData.top_gaps)) {
          setGaps(summaryData.top_gaps);
        }
        if (Array.isArray(summaryData.frequent_misconceptions)) {
          setMisconceptions(summaryData.frequent_misconceptions);
        }
      } else if (selectedCohort === 'empty-cohort') {
        setCohortName('Empty Class (Demo)');
        setTotalStudents(0);
        setClassAverageMastery(0);
        setGaps([]);
        setMisconceptions([]);
      } else {
        // Fallback to default class-10-a seeded metrics
        setGaps(DEFAULT_GAPS);
        setMisconceptions(DEFAULT_MISCONCEPTIONS);
      }

      // Fetch heatmap
      const heatmapRes = await fetch(`/api/teacher/cohorts/${selectedCohort}/heatmap`).catch(() => null);
      if (heatmapRes && heatmapRes.ok) {
        const heatmapData = await heatmapRes.json();
        if (Array.isArray(heatmapData.concepts)) setConcepts(heatmapData.concepts);
        if (Array.isArray(heatmapData.students)) setStudents(heatmapData.students);
        if (heatmapData.matrix) setMatrix(heatmapData.matrix);
      } else if (selectedCohort === 'empty-cohort') {
        setStudents([]);
        setMatrix({});
      } else {
        // Fallback to seeded heatmap
        const seeded = buildDefaultStudentsAndMatrix();
        setConcepts(DEFAULT_CONCEPTS);
        setStudents(seeded.students);
        setMatrix(seeded.matrix);
      }
    } catch (err: unknown) {
      // Graceful fallback on network or parse error
      console.warn('Teacher dashboard fetch failed, keeping fallback data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCohortData(cohortId);
  }, [cohortId, fetchCohortData]);

  const handleCohortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCohortId(e.target.value);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Top Navigation Header */}
      <header className="border-b border-border bg-card/60 backdrop-blur-md sticky top-0 z-30 px-4 sm:px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center border border-primary/20">
              <GraduationCap className="h-5 w-5" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-bold tracking-tight text-foreground">
                Teacher Analytics Dashboard: Class 10 Physics
              </h1>
              <p className="text-xs text-muted-foreground">
                Real-time Bayesian Knowledge Tracing (BKT) & misconception diagnosis
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <label htmlFor="cohort-select" className="text-xs font-medium text-muted-foreground whitespace-nowrap">
              Cohort:
            </label>
            <select
              id="cohort-select"
              value={cohortId}
              onChange={handleCohortChange}
              className="h-9 rounded-lg border border-border bg-background px-3 py-1 text-xs font-medium text-foreground shadow-sm focus:border-ring focus:ring-1 focus:ring-ring outline-none cursor-pointer"
            >
              <option value="class-10-a">Class 10 - Section A (Physics)</option>
              <option value="class-10-b">Class 10 - Section B (Physics)</option>
              <option value="empty-cohort">Empty Cohort (Demo)</option>
            </select>

            <button
              type="button"
              onClick={() => fetchCohortData(cohortId)}
              title="Refresh Analytics"
              className="h-9 w-9 inline-flex items-center justify-center rounded-lg border border-border bg-background hover:bg-muted text-muted-foreground transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-8">
        {/* KPI Stats Overview */}
        <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="rounded-xl border border-border bg-card p-4 shadow-sm flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center">
              <Users className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Total Students</p>
              <p className="text-2xl font-bold text-foreground">{totalStudents}</p>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-4 shadow-sm flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Class Average Mastery</p>
              <p className="text-2xl font-bold text-foreground">{Math.round(classAverageMastery * 100)}%</p>
            </div>
          </div>

          <div className="rounded-xl border border-border bg-card p-4 shadow-sm flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 flex items-center justify-center">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground font-medium">Active High-Priority Gaps</p>
              <p className="text-2xl font-bold text-foreground">
                {gaps.filter((g) => g.struggling_percentage > 50).length} Concepts
              </p>
            </div>
          </div>
        </section>

        {/* Section 1: Class-Wide Knowledge Gaps */}
        <section aria-labelledby="section-gaps" className="space-y-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-rose-500" />
            <h2 id="section-gaps" className="text-lg font-bold text-foreground">
              Class-Wide Knowledge Gaps
            </h2>
          </div>
          <ClassGapsSummary gaps={gaps} loading={loading} />
        </section>

        {/* Section 2: Concept Mastery Heatmap */}
        <section aria-labelledby="section-heatmap" className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            <h2 id="section-heatmap" className="text-lg font-bold text-foreground">
              Concept Mastery Heatmap
            </h2>
          </div>
          <ClassHeatmap
            concepts={concepts}
            students={students}
            matrix={matrix}
            loading={loading}
          />
        </section>

        {/* Section 3: Top Reasoning Misconceptions */}
        <section aria-labelledby="section-misconceptions" className="space-y-3">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5 text-amber-500" />
            <h2 id="section-misconceptions" className="text-lg font-bold text-foreground">
              Top Reasoning Misconceptions
            </h2>
          </div>
          <MisconceptionBreakdown misconceptions={misconceptions} loading={loading} />
        </section>
      </main>
    </div>
  );
}
