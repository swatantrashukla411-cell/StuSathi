"use client";

import React, { useState, useEffect } from "react";
import { GraduationCap, TrendingUp, Sliders, AlertCircle, CheckCircle } from "lucide-react";
import { GPASummaryResponse, solveTargetCGPA, TargetGPAResponse } from "@/lib/api";

interface GPAOrbitProps {
  data: GPASummaryResponse | null;
  loading: boolean;
}

export default function GPAOrbit({ data, loading }: GPAOrbitProps) {
  const currentCGPA = data?.cumulative_cgpa?.cgpa ?? 8.40;
  const completedCredits = data?.cumulative_cgpa?.total_completed_credits ?? 24.0;
  const remainingCredits = 76.0;

  const [targetCGPA, setTargetCGPA] = useState<number>(8.80);
  const [solverResult, setSolverResult] = useState<TargetGPAResponse | null>(null);

  useEffect(() => {
    let active = true;
    solveTargetCGPA({
      current_cgpa: currentCGPA,
      completed_credits: completedCredits,
      remaining_credits: remainingCredits,
      target_cgpa: targetCGPA,
    })
      .then((res) => {
        if (active) setSolverResult(res);
      })
      .catch((err) => console.error(err));

    return () => {
      active = false;
    };
  }, [targetCGPA, currentCGPA, completedCredits]);

  if (loading) {
    return (
      <div className="rounded-2xl bg-surface border border-borderSubtle p-5 animate-pulse space-y-4">
        <div className="h-5 w-32 bg-gray-800 rounded"></div>
        <div className="h-20 bg-gray-800/60 rounded-xl"></div>
      </div>
    );
  }

  const isAchievable = solverResult?.is_achievable ?? true;
  const reqSGPA = solverResult?.required_future_sgpa ?? 0;

  return (
    <div className="rounded-2xl bg-surface border border-borderSubtle p-5 shadow-lg flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-borderSubtle mb-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="h-4 w-4 text-indigo-400" />
            <h3 className="font-semibold text-sm text-white">Academic Performance Orbit</h3>
          </div>
          <span className="text-xs text-gray-400">10-Point Scale</span>
        </div>

        {/* Current Standing Card */}
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div className="p-3.5 rounded-xl bg-surfaceHover border border-borderSubtle text-center">
            <span className="text-[11px] text-gray-400 font-medium">Cumulative CGPA</span>
            <div className="text-2xl font-black text-white mt-0.5">{currentCGPA.toFixed(2)}</div>
            <span className="text-[10px] text-emerald-400 font-medium">Good Standing</span>
          </div>

          <div className="p-3.5 rounded-xl bg-surfaceHover border border-borderSubtle text-center">
            <span className="text-[11px] text-gray-400 font-medium">Earned Credits</span>
            <div className="text-2xl font-black text-white mt-0.5">{completedCredits}</div>
            <span className="text-[10px] text-gray-400">{remainingCredits} remaining</span>
          </div>
        </div>

        {/* Target Slider */}
        <div className="p-4 rounded-xl bg-gray-900/50 border border-borderSubtle">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
              <Sliders className="h-3.5 w-3.5 text-indigo-400" />
              <span>Target Graduation CGPA</span>
            </label>
            <span className="text-sm font-extrabold text-voiceCyan">{targetCGPA.toFixed(2)}</span>
          </div>

          <input
            type="range"
            min="7.5"
            max="9.8"
            step="0.05"
            value={targetCGPA}
            onChange={(e) => setTargetCGPA(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />

          <div className="flex justify-between text-[10px] text-gray-500 font-medium mt-1">
            <span>7.50</span>
            <span>8.50</span>
            <span>9.50</span>
          </div>

          {/* Solver Feedback Result */}
          <div className="mt-3.5 pt-3 border-t border-borderSubtle/60 flex items-center justify-between text-xs">
            <span className="text-gray-400">Required Future SGPA:</span>
            <div className="flex items-center gap-1.5">
              {isAchievable ? (
                <span className="font-extrabold text-white text-sm bg-indigo-500/10 border border-indigo-500/30 px-2 py-0.5 rounded">
                  {reqSGPA.toFixed(2)} SGPA
                </span>
              ) : (
                <span className="text-rose-400 text-xs font-semibold flex items-center gap-1">
                  <AlertCircle className="h-3.5 w-3.5" /> Infeasible (&gt; 10.0)
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
