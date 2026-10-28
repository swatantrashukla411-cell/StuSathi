"use client";

import React from "react";
import { Sparkles, GraduationCap, RefreshCw, Mic, UserCircle2 } from "lucide-react";
import { StudentProfile } from "@/lib/api";

interface HeaderProps {
  onOpenQUMS: () => void;
  onOpenVoice: () => void;
  onOpenAuth: () => void;
  isVoiceActive: boolean;
  student: StudentProfile | null;
}

export default function Header({
  onOpenQUMS,
  onOpenVoice,
  onOpenAuth,
  isVoiceActive,
  student,
}: HeaderProps) {
  const getInitials = (name?: string) => {
    if (!name) return "ST";
    const parts = name.split(" ");
    return parts.length > 1 ? `${parts[0][0]}${parts[1][0]}`.toUpperCase() : name.slice(0, 2).toUpperCase();
  };

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
          <p className="text-xs text-gray-400">Personal Academic Co-Pilot for College Students</p>
        </div>
      </div>

      {/* Student Profile & Quick Actions */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        {/* Student Profile Pill / Switcher */}
        <button
          onClick={onOpenAuth}
          className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-surfaceHover hover:bg-surface border border-borderSubtle hover:border-indigo-500/40 transition-all text-left group"
          title="Click to Switch Student Profile or Register"
        >
          <div className="h-7 w-7 rounded-full bg-emerald-500/20 text-emerald-400 font-bold text-xs flex items-center justify-center border border-emerald-500/30">
            {getInitials(student?.full_name)}
          </div>
          <div className="hidden sm:block text-left">
            <div className="text-xs font-semibold text-gray-100 group-hover:text-voiceCyan transition-colors flex items-center gap-1">
              <span>{student?.full_name || "Swatantra Shukla"}</span>
              <span className="text-[10px] text-gray-400 group-hover:text-gray-300">▼</span>
            </div>
            <div className="text-[10px] text-gray-400">
              Sem {student?.active_semester || 5} • {student?.program?.split("(")[0]?.trim() || "B.Tech CSE"}
            </div>
          </div>
        </button>

        {/* Sync QUMS Button */}
        <button
          onClick={onOpenQUMS}
          className="flex items-center gap-1.5 text-xs font-semibold px-3 py-2 rounded-xl bg-indigo-600/10 text-indigo-300 border border-indigo-500/30 hover:bg-indigo-600/20 transition-all"
          title="Sync attendance directly from Quantum University QUMS Portal"
        >
          <RefreshCw className="h-3.5 w-3.5 text-indigo-400" />
          <span className="hidden md:inline">Sync QUMS</span>
        </button>

        {/* Voice Trigger Orb */}
        <button
          onClick={onOpenVoice}
          className={`flex items-center gap-2 text-xs font-semibold px-3.5 py-2 rounded-xl transition-all shadow-md ${
            isVoiceActive
              ? "bg-voiceCyan text-gray-950 font-bold shadow-voiceCyan/30 animate-pulse"
              : "bg-gradient-to-r from-agentIndigo to-indigo-600 text-white hover:brightness-110 shadow-indigo-500/20"
          }`}
        >
          <Mic className="h-3.5 w-3.5" />
          <span className="hidden sm:inline">Voice Agent</span>
        </button>
      </div>
    </header>
  );
}
