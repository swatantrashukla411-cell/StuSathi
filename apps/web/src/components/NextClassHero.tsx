"use client";

import React, { useEffect, useState } from "react";
import { Clock, MapPin, User, CheckCircle2, Moon, Sparkles } from "lucide-react";
import { NextClassResponse } from "@/lib/api";

interface NextClassHeroProps {
  data: NextClassResponse | null;
  loading: boolean;
}

export default function NextClassHero({ data, loading }: NextClassHeroProps) {
  const [seconds, setSeconds] = useState(0);

  // Live seconds ticker for the countdown visual
  useEffect(() => {
    const timer = setInterval(() => {
      setSeconds((prev) => (prev + 1) % 60);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  if (loading) {
    return (
      <div className="w-full h-44 rounded-2xl bg-surface border border-borderSubtle animate-pulse p-6 flex flex-col justify-between">
        <div className="h-6 w-48 bg-gray-800 rounded"></div>
        <div className="h-10 w-96 bg-gray-800 rounded"></div>
        <div className="h-6 w-64 bg-gray-800 rounded"></div>
      </div>
    );
  }

  if (!data || !data.has_upcoming) {
    return (
      <div className="w-full rounded-2xl bg-gradient-to-r from-surface to-surfaceHover border border-borderSubtle p-6 flex items-center justify-between shadow-xl">
        <div className="flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <CheckCircle2 className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">All Clear!</h3>
            <p className="text-sm text-gray-400">
              {data?.message || "No upcoming classes scheduled. Great time to review notes or relax."}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const isNightOrFuture =
    data.minutes_remaining === null ||
    data.minutes_remaining === undefined ||
    data.is_tomorrow ||
    (data.message && data.message.toLowerCase().includes("no more classes"));

  const mins = data.minutes_remaining ?? 0;
  const isUrgent = !isNightOrFuture && mins <= 15 && mins > 0;

  return (
    <div
      className={`w-full rounded-2xl p-6 shadow-2xl relative overflow-hidden group border transition-all ${
        isNightOrFuture
          ? "bg-gradient-to-br from-[#0c1222] via-[#121c38] to-[#0c1222] border-indigo-500/30"
          : isUrgent
          ? "bg-gradient-to-br from-surface via-[#2a131b] to-surface border-rose-500/40"
          : "bg-gradient-to-br from-surface via-[#141b2d] to-surface border-indigo-500/20"
      }`}
    >
      {/* Decorative Glow */}
      <div
        className={`absolute top-0 right-0 -mt-12 -mr-12 w-64 h-64 rounded-full blur-3xl transition-all ${
          isNightOrFuture
            ? "bg-amber-500/10 group-hover:bg-amber-500/15"
            : "bg-agentIndigo/10 group-hover:bg-agentIndigo/15"
        }`}
      ></div>

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
        {/* Left Side: Countdown & Class Name */}
        <div className="space-y-2.5">
          <div className="flex items-center gap-2.5">
            {isNightOrFuture ? (
              <>
                <span className="text-xs font-semibold px-2.5 py-1 rounded-full flex items-center gap-1.5 bg-amber-500/15 text-amber-300 border border-amber-500/30">
                  <Moon className="h-3.5 w-3.5 text-amber-400" />
                  {data.day_label ? `${data.day_label}'s First Class` : "Tomorrow's First Class"}
                </span>
                <span className="text-xs text-amber-200/80 font-medium">
                  Starts at {data.start_time}
                </span>
              </>
            ) : (
              <>
                <span
                  className={`text-xs font-semibold px-2.5 py-1 rounded-full flex items-center gap-1.5 ${
                    isUrgent
                      ? "bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse"
                      : "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                  }`}
                >
                  <Clock className="h-3.5 w-3.5" />
                  {mins === 0 ? "Class is Starting Now" : `Starts in ${mins} Minutes`}
                </span>
                <span className="text-xs text-gray-400">({data.start_time || "Upcoming"})</span>
              </>
            )}
          </div>

          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
              <span>{data.subject_name}</span>
              {data.subject_code && (
                <span className="text-sm font-medium text-gray-400 bg-gray-800/80 px-2 py-0.5 rounded">
                  {data.subject_code}
                </span>
              )}
            </h2>
            <p className="text-sm text-indigo-200/80 mt-1">{data.message}</p>
          </div>

          {/* Location & Faculty Chips */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-gray-300 pt-1">
            <div className="flex items-center gap-1.5 bg-gray-900/60 border border-borderSubtle px-2.5 py-1.5 rounded-lg">
              <MapPin className="h-3.5 w-3.5 text-voiceCyan" />
              <span className="font-medium text-white">{data.room}</span>
              <span className="text-gray-400">({data.building})</span>
            </div>

            {data.instructor && (
              <div className="flex items-center gap-1.5 bg-gray-900/60 border border-borderSubtle px-2.5 py-1.5 rounded-lg">
                <User className="h-3.5 w-3.5 text-indigo-400" />
                <span>{data.instructor}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Side: Night Clock or Minute Countdown Dial */}
        <div className="hidden lg:flex flex-col items-center justify-center p-4 rounded-xl bg-gray-900/50 border border-borderSubtle min-w-[145px]">
          {isNightOrFuture ? (
            <>
              <div className="text-3xl font-extrabold text-amber-300 tracking-tight">
                {data.start_time}
              </div>
              <div className="text-[11px] uppercase tracking-wider text-amber-400/90 font-semibold mt-1 flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                <span>{data.day_label || "Tomorrow"}</span>
              </div>
            </>
          ) : (
            <>
              <div className="text-4xl font-extrabold text-white tracking-tight">
                {mins}
                <span className="text-lg text-indigo-400 font-medium ml-1">m</span>
              </div>
              <div className="text-[11px] uppercase tracking-wider text-gray-400 font-semibold mt-0.5">
                Countdown
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
