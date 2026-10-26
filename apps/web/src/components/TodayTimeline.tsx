"use client";

import React from "react";
import { Calendar, Clock, MapPin, CheckCircle, Radio } from "lucide-react";
import { TodayScheduleResponse } from "@/lib/api";

interface TodayTimelineProps {
  schedule: TodayScheduleResponse | null;
  loading: boolean;
}

export default function TodayTimeline({ schedule, loading }: TodayTimelineProps) {
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

  const sessions = schedule?.sessions || [];

  return (
    <div className="rounded-2xl bg-surface border border-borderSubtle p-5 shadow-lg flex flex-col justify-between">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-borderSubtle/60 mb-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-indigo-400" />
            <h3 className="font-semibold text-sm text-white">Today's Schedule</h3>
          </div>
          <span className="text-xs text-gray-400">
            {schedule?.day_name || "Today"} ({sessions.length} Lectures)
          </span>
        </div>

        {/* Sessions List */}
        {sessions.length === 0 ? (
          <div className="py-8 text-center text-xs text-gray-400">
            No lectures scheduled for today.
          </div>
        ) : (
          <div className="space-y-3">
            {sessions.map((s) => {
              const isOngoing = s.status === "ongoing";
              const isCompleted = s.status === "completed";

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
                    {s.status === "upcoming" && (
                      <span className="text-[10px] font-medium text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">
                        Upcoming
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
