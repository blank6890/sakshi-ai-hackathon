'use client';

import React from 'react';

export interface HeatmapConcept {
  concept_id: string;
  concept_name: string;
  chapter?: string;
}

export interface HeatmapStudent {
  student_id: string;
  student_name: string;
  overall_mastery: number;
}

export interface ClassHeatmapProps {
  concepts?: HeatmapConcept[];
  students?: HeatmapStudent[];
  matrix?: Record<string, Record<string, number>>;
  loading?: boolean;
}

function getMasteryColor(score: number): string {
  if (score >= 0.70) {
    return 'bg-emerald-100 text-emerald-900 border-emerald-300 dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-800/50';
  }
  if (score >= 0.40) {
    return 'bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-800/50';
  }
  return 'bg-rose-100 text-rose-900 border-rose-300 dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-800/50';
}

function formatPercent(val: number): string {
  return `${Math.round(val * 100)}%`;
}

function normalizeChapter(chapterName?: string): string {
  if (!chapterName) return 'General';
  if (/magnet/i.test(chapterName)) return 'Magnetism';
  if (/electric/i.test(chapterName)) return 'Electricity';
  if (/light/i.test(chapterName)) return 'Light';
  return chapterName;
}

export function ClassHeatmap({
  concepts = [],
  students = [],
  matrix = {},
  loading = false,
}: ClassHeatmapProps) {
  if (loading) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-card-foreground shadow-sm">
        <div className="flex h-48 items-center justify-center text-sm text-muted-foreground animate-pulse">
          Loading concept mastery heatmap...
        </div>
      </div>
    );
  }

  if (students.length === 0 || concepts.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-card-foreground shadow-sm">
        <p className="text-sm text-muted-foreground">No student mastery records found for this cohort.</p>
      </div>
    );
  }

  // Group concepts by chapter while preserving order
  const chapterGroups: { chapter: string; items: HeatmapConcept[] }[] = [];
  concepts.forEach((concept) => {
    const ch = normalizeChapter(concept.chapter);
    const last = chapterGroups[chapterGroups.length - 1];
    if (last && last.chapter === ch) {
      last.items.push(concept);
    } else {
      chapterGroups.push({ chapter: ch, items: [concept] });
    }
  });

  return (
    <div className="rounded-xl border border-border bg-card shadow-sm">
      <div className="border-b border-border p-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold text-foreground">Student Mastery Matrix</h3>
          <p className="text-xs text-muted-foreground">
            BKT mastery probability $P(L)$ across Class 10 Physics milestone concepts
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-3 w-3 rounded bg-emerald-500/80 border border-emerald-600 inline-block" />
            Mastered (&ge;70%)
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-3 w-3 rounded bg-amber-500/80 border border-amber-600 inline-block" />
            Progressing (40-69%)
          </span>
          <span className="flex items-center gap-1.5 font-medium">
            <span className="h-3 w-3 rounded bg-rose-500/80 border border-rose-600 inline-block" />
            Gap (&lt;40%)
          </span>
        </div>
      </div>

      <div className="overflow-x-auto max-h-[540px]">
        <table className="w-full border-collapse text-left text-xs">
          <thead className="sticky top-0 z-10 bg-muted/95 backdrop-blur-sm border-b border-border">
            {/* Top row: Chapter groupings */}
            <tr>
              <th
                rowSpan={2}
                className="sticky left-0 z-20 bg-muted/95 px-3 py-2 font-medium text-foreground min-w-[140px] border-r border-border"
              >
                Student Name
              </th>
              <th
                rowSpan={2}
                className="sticky left-[140px] z-20 bg-muted/95 px-2 py-2 font-medium text-center text-foreground min-w-[70px] border-r border-border"
              >
                Overall
              </th>
              {chapterGroups.map((group, idx) => (
                <th
                  key={`${group.chapter}-${idx}`}
                  colSpan={group.items.length}
                  className="px-2 py-1 text-center font-semibold text-foreground tracking-wider uppercase text-[11px] border-r border-border bg-muted/80"
                >
                  {group.chapter}
                </th>
              ))}
            </tr>
            {/* Bottom row: Concept names */}
            <tr>
              {concepts.map((concept) => (
                <th
                  key={concept.concept_id}
                  title={`${concept.concept_name} (${concept.chapter || 'General'})`}
                  className="px-1.5 py-2 font-medium text-muted-foreground text-[11px] text-center max-w-[85px] truncate border-r border-border hover:bg-muted"
                >
                  {concept.concept_name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60">
            {students.map((student, sIdx) => {
              const studentMatrix = matrix[student.student_id] || {};
              const overallScore = student.overall_mastery;
              return (
                <tr
                  key={student.student_id}
                  className={sIdx % 2 === 0 ? 'bg-card' : 'bg-muted/20'}
                >
                  <td className="sticky left-0 z-10 bg-inherit px-3 py-2 font-medium text-foreground whitespace-nowrap border-r border-border">
                    {student.student_name}
                  </td>
                  <td className="sticky left-[140px] z-10 bg-inherit px-2 py-2 text-center font-semibold border-r border-border">
                    <span
                      className={`inline-block px-1.5 py-0.5 rounded text-[11px] ${
                        overallScore >= 0.70
                          ? 'text-emerald-700 dark:text-emerald-400 font-bold'
                          : overallScore >= 0.40
                          ? 'text-amber-700 dark:text-amber-400 font-bold'
                          : 'text-rose-700 dark:text-rose-400 font-bold'
                      }`}
                    >
                      {formatPercent(overallScore)}
                    </span>
                  </td>
                  {concepts.map((concept) => {
                    const score = studentMatrix[concept.concept_id] ?? 0;
                    return (
                      <td
                        key={concept.concept_id}
                        className="p-1 text-center border-r border-border/40"
                      >
                        <div
                          title={`${student.student_name} • ${concept.concept_name}: ${formatPercent(score)}`}
                          className={`mx-auto rounded px-1.5 py-1 text-[11px] font-medium border transition-transform hover:scale-105 cursor-default ${getMasteryColor(score)}`}
                        >
                          {formatPercent(score)}
                        </div>
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ClassHeatmap;
