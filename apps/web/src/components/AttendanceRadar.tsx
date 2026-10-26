"use client";

import React, { useState } from "react";
import { ShieldCheck, AlertTriangle, AlertCircle, ArrowUpRight, Sparkles } from "lucide-react";
import { SubjectAttendance } from "@/lib/api";
import WhatIfModal from "./WhatIfModal";

interface AttendanceRadarProps {
  subjects: SubjectAttendance[];
  loading: boolean;
}

export default function AttendanceRadar({ subjects, loading }: AttendanceRadarProps) {
  const [selectedSubject, setSelectedSubject] = useState<SubjectAttendance | null>(null);

  if (loading) {
    return (
      <div className="rounded-2xl bg-surface border border-borderSubtle p-5 animate-pulse space-y-4">
        <div className="h-5 w-40 bg-gray-800 rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-36 bg-gray-800/60 rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-2xl bg-surface border border-borderSubtle p-5 shadow-lg">
        {/* Section Header */}
        <div className="flex items-center justify-between pb-4 border-b border-borderSubtle mb-5">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <h3 className="font-semibold text-sm text-white">Attendance Intelligence Radar</h3>
          </div>
          <span className="text-xs text-gray-400">
            Min Requirement: <span className="text-white font-bold">75.0%</span>
          </span>
        </div>

        {/* Subjects Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {subjects.map((s) => {
            const isSafe = s.risk_category === "safe";
            const isCaution = s.risk_category === "caution";
            const isCritical = s.risk_category === "critical" || s.risk_category === "unrecoverable";

            return (
              <div
                key={s.subject_code}
                className="p-4 rounded-xl bg-surfaceHover/80 border border-borderSubtle hover:border-gray-700 transition-all flex flex-col justify-between group"
              >
                <div>
                  {/* Subject Name & Code */}
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-bold text-xs text-white group-hover:text-indigo-300 transition-colors line-clamp-1">
                        {s.subject_name}
                      </h4>
                      <span className="text-[10px] text-gray-400 font-medium">{s.subject_code}</span>
                    </div>

                    {/* Percentage Pill */}
                    <div
                      className={`text-sm font-extrabold px-2 py-0.5 rounded-lg ${
                        isSafe
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                          : isCaution
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                          : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                      }`}
                    >
                      {s.current_percentage}%
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-800 h-2 rounded-full mt-3 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isSafe ? "bg-emerald-500" : isCaution ? "bg-amber-500" : "bg-rose-500"
                      }`}
                      style={{ width: `${Math.min(100, s.current_percentage)}%` }}
                    ></div>
                  </div>

                  {/* Attended vs Conducted Metrics */}
                  <div className="flex items-center justify-between text-[11px] text-gray-400 mt-2">
                    <span>
                      Attended: <strong className="text-white">{s.classes_attended}</strong> / {s.classes_conducted}
                    </span>
                    <span>Remaining: {s.remaining_planned_sessions}</span>
                  </div>

                  {/* Status Badge */}
                  <div className="mt-3">
                    {isSafe && (
                      <div className="text-[11px] font-medium text-emerald-400 bg-emerald-950/30 border border-emerald-500/20 px-2 py-1 rounded-lg flex items-center gap-1.5">
                        <ShieldCheck className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                        <span>Can safely skip <strong>{s.safe_future_absences}</strong> more lectures</span>
                      </div>
                    )}
                    {isCaution && (
                      <div className="text-[11px] font-medium text-amber-400 bg-amber-950/30 border border-amber-500/20 px-2 py-1 rounded-lg flex items-center gap-1.5">
                        <AlertTriangle className="h-3.5 w-3.5 text-amber-400 shrink-0" />
                        <span>Narrow margin: Only <strong>{s.safe_future_absences}</strong> safe absence left!</span>
                      </div>
                    )}
                    {isCritical && (
                      <div className="text-[11px] font-medium text-rose-400 bg-rose-950/30 border border-rose-500/20 px-2 py-1 rounded-lg flex items-center gap-1.5">
                        <AlertCircle className="h-3.5 w-3.5 text-rose-400 shrink-0" />
                        <span>Danger Zone: Must recover to 75%</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* What-If Button */}
                <button
                  onClick={() => setSelectedSubject(s)}
                  className="mt-4 w-full py-1.5 px-3 rounded-lg bg-gray-900/60 hover:bg-indigo-600/20 text-gray-300 hover:text-indigo-300 border border-borderSubtle hover:border-indigo-500/30 text-[11px] font-medium transition-all flex items-center justify-center gap-1.5"
                >
                  <Sparkles className="h-3 w-3 text-indigo-400" />
                  <span>Simulate What-If</span>
                  <ArrowUpRight className="h-3 w-3 ml-0.5 opacity-60" />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Modal */}
      <WhatIfModal subject={selectedSubject} onClose={() => setSelectedSubject(null)} />
    </>
  );
}
