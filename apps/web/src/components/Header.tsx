"use client";

import React from "react";
import { Sparkles, GraduationCap, RefreshCw, Mic } from "lucide-react";

interface HeaderProps {
  onOpenQUMS: () => void;
  onOpenVoice: () => void;
  isVoiceActive: boolean;
}

export default function Header({ onOpenQUMS, onOpenVoice, isVoiceActive }: HeaderProps) {
  return (
    <header className="border-b border-borderSubtle bg-surface/80 backdrop-blur-md sticky top-0 z-40 px-4 lg:px-8 py-3.5 flex items-center justify-between">
      {/* Brand & Identity */}
      <div className="flex items-center gap-3">
        <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-agentIndigo to-voiceCyan flex items-center justify-center shadow-lg shadow-agentIndigo/20">
          <Sparkles className="h-5 w-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg text-white tracking-tight">CampusPilot AI</span>
            <span className="text-[10px] font-semibold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 px-1.5 py-0.5 rounded">
              Voice-First
            </span>
          </div>
          <p className="text-xs text-gray-400">Personal Academic Co-Pilot for Students</p>
        </div>
      </div>

      {/* Student Profile & Quick Actions */}
      <div className="flex items-center gap-3">
        {/* Student Profile Pill */}
        <div className="hidden sm:flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-surfaceHover border border-borderSubtle">
          <div className="h-7 w-7 rounded-full bg-emerald-500/20 text-emerald-400 font-semibold text-xs flex items-center justify-center">
            SS
          </div>
          <div className="text-left">
            <div className="text-xs font-medium text-gray-200">Swatantra Shukla</div>
            <div className="text-[11px] text-gray-400">B.Tech CSE (AI/ML) • Sem 5</div>
          </div>
        </div>

        {/* Sync QUMS Button */}
        <button
          onClick={onOpenQUMS}
          className="flex items-center gap-2 text-xs font-medium px-3 py-2 rounded-lg bg-indigo-600/10 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/20 transition-colors"
          title="Sync attendance directly from Quantum University QUMS Portal"
        >
          <RefreshCw className="h-3.5 w-3.5 text-indigo-400" />
          <span>Sync QUMS</span>
        </button>

        {/* Voice Trigger Orb */}
        <button
          onClick={onOpenVoice}
          className={`flex items-center gap-2 text-xs font-medium px-3.5 py-2 rounded-lg transition-all shadow-md ${
            isVoiceActive
              ? "bg-voiceCyan text-gray-950 font-semibold shadow-voiceCyan/30 animate-pulse"
              : "bg-gradient-to-r from-agentIndigo to-indigo-600 text-white hover:brightness-110 shadow-indigo-500/20"
          }`}
        >
          <Mic className="h-3.5 w-3.5" />
          <span className="hidden md:inline">Voice Agent</span>
        </button>
      </div>
    </header>
  );
}
