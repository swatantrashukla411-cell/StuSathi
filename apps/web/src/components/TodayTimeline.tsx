"use client";

import React, { useState, useEffect } from "react";
import { Calendar, Clock, MapPin, CheckCircle, Radio, Moon, Sun } from "lucide-react";
import { TodayScheduleResponse, fetchTomorrowSchedule } from "@/lib/api";

interface TodayTimelineProps {
  schedule: TodayScheduleResponse | null;
  loading: boolean;
  userId?: number;
}

export default function TodayTimeline({ schedule, loading, userId = 1 }: TodayTimelineProps) {
  const [activeTab, setActiveTab] = useState<"today" | "tomorrow">("today");
  const [tomorrowSchedule, setTomorrowSchedule] = useState<TodayScheduleResponse | null>(null);
  const [loadingTomorrow, setLoadingTomorrow] = useState(false);

  // Auto-load tomorrow's schedule in background
  useEffect(() => {
    setLoadingTomorrow(true);
    fetchTomorrowSchedule(userId)
      .then((data) => setTomorrowSchedule(data))
      .catch((e) => console.error("Tomorrow schedule fetch error", e))
      .finally(() => setLoadingTomorrow(false));
  }, [userId]);

  const todaySessions = schedule?.sessions || [];
  const allTodayCompleted =
    todaySessions.length > 0 && todaySessions.every((s) => s.status === "completed");

  // If all today's classes are done, default active tab to tomorrow
  useEffect(() => {
    if (allTodayCompleted) {
      setActiveTab("tomorrow");
    }
  }, [allTodayCompleted]);

  if (loading) {
    return (
      <div className="rounded-2xl bg-surface border border-borderSubtle p-5 animate-pulse space-y-4">
        <div className="h-5 w-32 bg-gray-800 rounded"></div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-800/60 rounded-xl"></div>
          ))}
        </div>
      </div>
    );
  }

  const currentDisplaySchedule = activeTab === "tomorrow" ? tomorrowSchedule : schedule;
  const sessions = currentDisplaySchedule?.sessions || [];

  return (
    <div className="rounded-2xl bg-surface border border-borderSubtle p-5 shadow-lg flex flex-col justify-between">
      <div>
        {/* Header & Day Switcher Tabs */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-borderSubtle/60 mb-4 gap-3">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-indigo-400" />
            <h3 className="font-semibold text-sm text-white">Timetable Schedule</h3>
          </div>

          <div className="flex items-center gap-1.5 bg-gray-900/80 p-1 rounded-xl border border-borderSubtle text-xs">
            <button
              onClick={() => setActiveTab("today")}
              className={`px-3 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
                activeTab === "today"
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              <Sun className="h-3 w-3" />
              <span>Today ({schedule?.day_name || "Today"})</span>
            </button>

            <button
              onClick={() => setActiveTab("tomorrow")}
              className={`px-3 py-1 rounded-lg font-medium transition-all flex items-center gap-1.5 ${
                activeTab === "tomorrow"
                  ? "bg-amber-600/90 text-white shadow-sm"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              <Moon className="h-3 w-3 text-amber-300" />
              <span>Kal ({tomorrowSchedule?.day_name || "Tomorrow"})</span>
            </button>
          </div>
        </div>

        {/* Nighttime / Completed Notice Banner */}
        {allTodayCompleted && activeTab === "today" && (
          <div className="mb-4 p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 flex items-center justify-between text-xs text-indigo-200">
            <div className="flex items-center gap-2">
              <Moon className="h-4 w-4 text-amber-400 shrink-0" />
              <span>Aaj ki sabhi classes over ho chuki hain!</span>
            </div>
            <button
              onClick={() => setActiveTab("tomorrow")}
              className="text-amber-300 underline font-semibold hover:text-amber-200"
            >
              Kal ka schedule dekhein &rarr;
            </button>
          </div>
        )}

        {/* Sessions List */}
        {sessions.length === 0 ? (
          <div className="py-8 text-center text-xs text-gray-400">
            {activeTab === "tomorrow"
              ? "Kal koi classes scheduled nahi hain. Enjoy your day!"
              : "No lectures scheduled for today."}
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.map((s) => {
              const isOngoing = activeTab === "today" && s.status === "ongoing";
              const isCompleted = activeTab === "today" && s.status === "completed";

              return (
                <div
                  key={s.session_id}
                  className={`p-3.5 rounded-xl border transition-all flex items-center justify-between ${
                    isOngoing
                      ? "bg-indigo-950/30 border-indigo-500/40 shadow-md shadow-indigo-500/10"
                      : isCompleted
                      ? "bg-gray-900/40 border-borderSubtle/60 opacity-60"
                      : "bg-surfaceHover/70 border-borderSubtle hover:border-gray-600"
                  }`}
                >
                  {/* Left: Time & Status */}
                  <div className="flex items-center gap-3">
                    <div className="text-center min-w-[58px]">
                      <div className="text-xs font-semibold text-white">{s.start_time}</div>
                      <div className="text-[10px] text-gray-400">{s.end_time}</div>
                    </div>

                    <div className="h-8 w-[1px] bg-borderSubtle mx-1"></div>

                    {/* Class Details */}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white">{s.subject_name}</span>
                        <span className="text-[10px] font-medium text-gray-400 uppercase bg-gray-800 px-1.5 py-0.2 rounded">
                          {s.session_type}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-gray-400 mt-0.5">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3 text-voiceCyan" /> {s.room}
                        </span>
                        {s.instructor && <span>• {s.instructor}</span>}
                      </div>
                    </div>
                  </div>

                  {/* Right: Badge */}
                  <div>
                    {isOngoing && (
                      <span className="flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-full">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                        Ongoing
                      </span>
                    )}
                    {isCompleted && (
                      <span className="flex items-center gap-1 text-[10px] text-gray-400 bg-gray-800/80 px-2 py-0.5 rounded-full">
                        <CheckCircle className="h-3 w-3 text-gray-500" /> Done
                      </span>
                    )}
                    {(!isCompleted && !isOngoing) && (
                      <span className="text-[10px] font-medium text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">
                        {activeTab === "tomorrow" ? "Scheduled" : "Upcoming"}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
