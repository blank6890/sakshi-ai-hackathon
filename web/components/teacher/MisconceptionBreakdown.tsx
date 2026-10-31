'use client';

import React, { useState } from 'react';
import { Lightbulb, Users, ChevronDown, ChevronUp, AlertOctagon } from 'lucide-react';

export interface FrequentMisconception {
  misconception_id: string;
  name: string;
  description: string;
  remedial_feedback?: string;
  concept_ids?: string[];
  count: number;
  affected_students: string[];
}

export interface MisconceptionBreakdownProps {
  misconceptions?: FrequentMisconception[];
  loading?: boolean;
}

export function MisconceptionBreakdown({
  misconceptions = [],
  loading = false,
}: MisconceptionBreakdownProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="rounded-xl border border-border bg-card p-5 shadow-sm animate-pulse h-28"
          >
            <div className="h-5 w-1/3 bg-muted rounded mb-2" />
            <div className="h-4 w-3/4 bg-muted rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (misconceptions.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-card p-6 text-card-foreground shadow-sm">
        <p className="text-sm text-muted-foreground">
          No widespread reasoning misconceptions detected in this cohort.
        </p>
      </div>
    );
  }

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="space-y-4">
      <p className="text-xs text-muted-foreground">
        Ranked flawed reasoning patterns inferred from incorrect answer explanations and prior tests
      </p>

      <div className="space-y-3">
        {misconceptions.map((item, index) => {
          const rank = index + 1;
          const isExpanded = expandedId === item.misconception_id;

          return (
            <div
              key={item.misconception_id}
              className="rounded-xl border border-border bg-card p-5 shadow-sm transition-all hover:border-border/80"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="flex items-start gap-3">
                  <span className="flex-shrink-0 inline-flex items-center justify-center h-6 w-6 rounded-full text-xs font-bold bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30">
                    #{rank}
                  </span>
                  <div>
                    <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                      {item.name}
                    </h4>
                    <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                      {item.description}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                  <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border border-rose-200 dark:border-rose-900/60">
                    <Users className="h-3 w-3" />
                    {item.count} {item.count === 1 ? 'student' : 'students'}
                  </span>
                </div>
              </div>

              {/* Remedial Teaching Tip */}
              {item.remedial_feedback && (
                <div className="mt-3.5 rounded-lg bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200/60 dark:border-amber-900/40 p-3 text-xs">
                  <div className="flex items-center gap-1.5 font-semibold text-amber-900 dark:text-amber-300 mb-1">
                    <Lightbulb className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
                    <span>Remedial Teaching Strategy</span>
                  </div>
                  <p className="text-amber-900/90 dark:text-amber-200/90 leading-relaxed">
                    {item.remedial_feedback}
                  </p>
                </div>
              )}

              {/* Affected students disclosure */}
              {item.affected_students && item.affected_students.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-border/50">
                  <button
                    type="button"
                    onClick={() => toggleExpand(item.misconception_id)}
                    className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <span>
                      {isExpanded ? 'Hide' : 'View'} affected students ({item.affected_students.length})
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="h-3 w-3" />
                    ) : (
                      <ChevronDown className="h-3 w-3" />
                    )}
                  </button>

                  {isExpanded && (
                    <div className="mt-2 flex flex-wrap gap-1.5 pt-1">
                      {item.affected_students.map((studentName) => (
                        <span
                          key={studentName}
                          className="px-2 py-0.5 rounded-md text-[11px] bg-muted text-muted-foreground border border-border"
                        >
                          {studentName}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default MisconceptionBreakdown;
