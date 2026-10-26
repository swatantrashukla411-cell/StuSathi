"use client";

import React, { useState } from "react";
import { X, Calculator, ShieldCheck, AlertTriangle, ArrowRight, Check } from "lucide-react";
import { SubjectAttendance, simulateAbsence, calculateRecovery } from "@/lib/api";

interface WhatIfModalProps {
  subject: SubjectAttendance | null;
  onClose: () => void;
}

export default function WhatIfModal({ subject, onClose }: WhatIfModalProps) {
  const [sessionsToMiss, setSessionsToMiss] = useState(1);
  const [simResult, setSimResult] = useState<any>(null);
  const [recoveryResult, setRecoveryResult] = useState<any>(null);
  const [loadingSim, setLoadingSim] = useState(false);
  const [loadingRec, setLoadingRec] = useState(false);

  if (!subject) return null;

  const handleSimulate = async (missCount: number) => {
    setSessionsToMiss(missCount);
    setLoadingSim(true);
    try {
      const res = await simulateAbsence({
        classes_conducted: subject.classes_conducted,
        classes_attended: subject.classes_attended,
        remaining_planned_sessions: subject.remaining_planned_sessions,
        sessions_to_miss: missCount,
        required_threshold: subject.required_threshold,
      });
      setSimResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSim(false);
    }
  };

  const handleCalculateRecovery = async () => {
    setLoadingRec(true);
    try {
      const res = await calculateRecovery({
        classes_conducted: subject.classes_conducted,
        classes_attended: subject.classes_attended,
        remaining_planned_sessions: subject.remaining_planned_sessions,
        target_threshold: 75.0,
      });
      setRecoveryResult(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingRec(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in">
      <div className="w-full max-w-lg rounded-2xl bg-surface border border-borderSubtle shadow-2xl p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white p-1 rounded-lg bg-surfaceHover border border-borderSubtle"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-2.5 pb-4 border-b border-borderSubtle">
          <div className="h-9 w-9 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
            <Calculator className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-base text-white">{subject.subject_name}</h3>
            <p className="text-xs text-gray-400">
              Current Attendance: <span className="font-bold text-white">{subject.current_percentage}%</span> ({subject.classes_attended}/{subject.classes_conducted} attended)
            </p>
          </div>
        </div>

        {/* Section 1: What-If Absence Simulator */}
        <div className="py-5 space-y-4">
          <div>
            <label className="text-xs font-semibold text-gray-300 block mb-2">
              If I skip upcoming lectures, what happens?
            </label>
            <div className="grid grid-cols-4 gap-2">
              {[1, 2, 3, 4].map((count) => (
                <button
                  key={count}
                  onClick={() => handleSimulate(count)}
                  className={`py-2 px-3 text-xs font-semibold rounded-xl border transition-all ${
                    sessionsToMiss === count
                      ? "bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-500/20"
                      : "bg-surfaceHover text-gray-300 border-borderSubtle hover:bg-gray-800"
                  }`}
                >
                  Skip {count} {count === 1 ? "Class" : "Classes"}
                </button>
              ))}
            </div>
          </div>

          {/* Simulation Output Card */}
          {simResult && (
            <div
              className={`p-4 rounded-xl border transition-all ${
                simResult.is_safe
                  ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-300"
                  : "bg-rose-950/20 border-rose-500/30 text-rose-300"
              }`}
            >
              <div className="flex items-center justify-between text-xs font-bold mb-1">
                <span className="flex items-center gap-1.5">
                  {simResult.is_safe ? <ShieldCheck className="h-4 w-4 text-emerald-400" /> : <AlertTriangle className="h-4 w-4 text-rose-400" />}
                  {simResult.is_safe ? "Safe Attendance Projection" : "Danger: Drops Below 75% Threshold"}
                </span>
                <span className="text-sm font-extrabold text-white">
                  {simResult.current_percentage}% <ArrowRight className="inline h-3 w-3 mx-0.5" /> {simResult.projected_percentage}%
                </span>
              </div>
              <p className="text-xs opacity-90 leading-relaxed mt-2">{simResult.explanation}</p>
            </div>
          )}

          {/* Section 2: Attendance Recovery Target */}
          <div className="pt-2 border-t border-borderSubtle">
            <button
              onClick={handleCalculateRecovery}
              disabled={loadingRec}
              className="w-full py-2.5 px-4 rounded-xl bg-surfaceHover hover:bg-gray-800 border border-borderSubtle text-xs font-semibold text-gray-200 transition-colors flex items-center justify-center gap-2"
            >
              <span>Calculate 75% Recovery Target</span>
            </button>

            {recoveryResult && (
              <div className="mt-3 p-3.5 rounded-xl bg-gray-900/60 border border-borderSubtle text-xs text-gray-300">
                <div className="font-semibold text-white mb-1">
                  {recoveryResult.is_recoverable
                    ? `Must Attend Next ${recoveryResult.classes_needed_consecutively} Classes Consecutively`
                    : "Mathematically Unrecoverable"}
                </div>
                <p className="text-[11px] text-gray-400">{recoveryResult.explanation}</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-borderSubtle flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-gray-800 text-gray-200 text-xs font-medium hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
