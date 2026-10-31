'use client';

import React from 'react';
import { AlertTriangle, AlertCircle, ArrowDownRight, BookOpen } from 'lucide-react';

export interface ConceptMisconceptionRef {
  misconception_id: string;
  name: string;
  count: number;
  description?: string;
}

export interface ConceptGap {
  concept_id: string;
  concept_name: string;
  chapter?: string;
  average_mastery: number;
  struggling_student_count: number;
  struggling_percentage: number;
  common_misconceptions?: ConceptMisconceptionRef[];
}

export interface ClassGapsSummaryProps {
  gaps?: ConceptGap[];
  loading?: boolean;
}

export function ClassGapsSummary({ gaps = [], loading = false }: ClassGapsSummaryProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-xl border border-border bg-card p-5 shadow-sm animate-pulse h-44"
          >
            <div className="h-4 w-24 bg-muted rounded mb-3" />
            <div className="h-6 w-3/4 bg-muted rounded mb-2" />
            <div className="h-4 w-1/2 bg-muted rounded" />
          </div>
        ))}
      </div>
    );
  }

  const topGaps = gaps.slice(0, 3);

  if (topGaps.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-card-foreground shadow-sm">
        <p className="text-sm text-muted-foreground">
          No significant concept gaps identified for this cohort.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Top 3 high-leverage concepts requiring targeted whole-class remediation
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {topGaps.map((gap, index) => {
          const rank = index + 1;
          const isHighPriority = gap.struggling_percentage > 50;
          const avgPct = Math.round(gap.average_mastery * 100);

          return (
            <div
              key={gap.concept_id}
              className={`rounded-xl border p-5 shadow-sm transition-all flex flex-col justify-between ${
                isHighPriority
                  ? 'border-rose-300/80 bg-rose-50/40 dark:bg-rose-950/20 dark:border-rose-900/60'
                  : 'border-border bg-card'
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center justify-center h-6 w-6 rounded-full text-xs font-bold ${
                        rank === 1
                          ? 'bg-rose-600 text-white dark:bg-rose-500'
                          : rank === 2
                          ? 'bg-amber-600 text-white dark:bg-amber-500'
                          : 'bg-muted-foreground text-card font-semibold'
                      }`}
                    >
                      #{rank}
                    </span>
                    <span className="text-[11px] font-medium text-muted-foreground flex items-center gap-1">
                      <BookOpen className="h-3 w-3" />
                      {gap.chapter || 'Class 10 Physics'}
                    </span>
                  </div>

                  {isHighPriority && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-800 dark:bg-rose-900/60 dark:text-rose-200 border border-rose-300 dark:border-rose-800">
                      <AlertTriangle className="h-3 w-3 text-rose-600 dark:text-rose-400" />
                      High Priority Gap
                    </span>
                  )}
                </div>

                <h4 className="text-base font-semibold text-foreground leading-snug mb-1">
                  {gap.concept_name}
                </h4>

                <div className="mt-3 flex items-center justify-between text-xs mb-1.5">
                  <span className="text-muted-foreground">Class Average Mastery</span>
                  <span
                    className={`font-bold ${
                      avgPct < 40
                        ? 'text-rose-600 dark:text-rose-400'
                        : avgPct < 70
                        ? 'text-amber-600 dark:text-amber-400'
                        : 'text-emerald-600 dark:text-emerald-400'
                    }`}
                  >
                    {avgPct}%
                  </span>
                </div>

                {/* Mastery progress bar */}
                <div className="w-full bg-muted rounded-full h-2 overflow-hidden mb-3">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      avgPct < 40 ? 'bg-rose-500' : avgPct < 70 ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, Math.max(0, avgPct))}%` }}
                  />
                </div>

                {/* Struggling student stat */}
                <div className="flex items-center gap-1.5 text-xs text-rose-700 dark:text-rose-300 font-medium">
                  <AlertCircle className="h-3.5 w-3.5 text-rose-500 flex-shrink-0" />
                  <span>
                    <strong>{gap.struggling_student_count} students</strong> (
                    {gap.struggling_percentage}%) below mastery
                  </span>
                </div>
              </div>

              {gap.common_misconceptions && gap.common_misconceptions.length > 0 && (
                <div className="mt-4 pt-3 border-t border-border/60 text-[11px] text-muted-foreground">
                  <span className="font-semibold text-foreground block mb-0.5">
                    Primary Flawed Reasoning:
                  </span>
                  <span className="line-clamp-2">
                    {gap.common_misconceptions[0].name} ({gap.common_misconceptions[0].count} students)
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ClassGapsSummary;
