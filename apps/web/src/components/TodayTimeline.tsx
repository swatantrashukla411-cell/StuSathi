"use client";

import React, { useState, useEffect } from "react";
import { Calendar, Clock, MapPin, CheckCircle, Radio, Moon, Sun, ChevronRight } from "lucide-react";
import { TodayScheduleResponse, fetchTodaySchedule, fetchTomorrowSchedule } from "@/lib/api";

interface TodayTimelineProps {
  schedule: TodayScheduleResponse | null;
  loading: boolean;
  userId?: number;
}

// Full weekly schedule template for Quantum University Semester 5
export const WEEKLY_TIMETABLE: Record<string, { day_name: string; day_of_week: number; sessions: any[] }> = {
  monday: {
    day_name: "Monday",
    day_of_week: 1,
    sessions: [
      {
        session_id: 101,
        subject_id: 1,
        subject_code: "CS35303",
        subject_name: "Design and Analysis of Algorithm (S)",
        start_time: "09:00 AM",
        end_time: "10:00 AM",
        session_type: "lecture",
        room: "Room 304",
        building: "Block B",
        instructor: "Dr. R. K. Sharma",
        status: "upcoming",
      },
      {
        session_id: 102,
        subject_id: 8,
        subject_code: "CS35304",
        subject_name: "Foundation of Cloud Computing(S)",
        start_time: "10:15 AM",
        end_time: "11:15 AM",
        session_type: "lecture",
        room: "Room 201",
        building: "Block A",
        instructor: "AMIT KUMAR",
        status: "upcoming",
      },
      {
        session_id: 103,
        subject_id: 3,
        subject_code: "CS35363",
        subject_name: "Design and Analysis of Algorithm Lab(L)",
        start_time: "11:30 AM",
        end_time: "01:00 PM",
        session_type: "lab",
        room: "Lab 304",
        building: "Block B",
        instructor: "Dr. R. K. Sharma",
        status: "upcoming",
      },
      {
        session_id: 104,
        subject_id: 6,
        subject_code: "SE35369",
        subject_name: "Technical Skills Development-IV(L)",
        start_time: "02:00 PM",
        end_time: "03:00 PM",
        session_type: "lecture",
        room: "Room 105",
        building: "Block B",
        instructor: "VIVEK KUMAR",
        status: "upcoming",
      },
    ],
  },
  tuesday: {
    day_name: "Tuesday",
    day_of_week: 2,
    sessions: [
      {
        session_id: 201,
        subject_id: 7,
        subject_code: "CS35365",
        subject_name: "Scala for Data Science - Tools and Techniques(L)",
        start_time: "09:00 AM",
        end_time: "10:00 AM",
        session_type: "lecture",
        room: "Room 302",
        building: "Block B",
        instructor: "BHANU PARTAP",
        status: "upcoming",
      },
      {
        session_id: 202,
        subject_id: 1,
        subject_code: "CS35303",
        subject_name: "Design and Analysis of Algorithm (S)",
        start_time: "10:15 AM",
        end_time: "11:15 AM",
        session_type: "lecture",
        room: "Room 304",
        building: "Block B",
        instructor: "Dr. R. K. Sharma",
        status: "upcoming",
      },
      {
        session_id: 203,
        subject_id: 9,
        subject_code: "CS35364",
        subject_name: "Advance Machine Learning Practical with Python(L)",
        start_time: "11:30 AM",
        end_time: "12:30 PM",
        session_type: "lab",
        room: "AI Lab 1",
        building: "Block B",
        instructor: "Dr. K. S. Verma",
        status: "upcoming",
      },
      {
        session_id: 204,
        subject_id: 10,
        subject_code: "JM3015",
        subject_name: "Event Management(L)",
        start_time: "02:00 PM",
        end_time: "03:00 PM",
        session_type: "lecture",
        room: "Room 205",
        building: "Block A",
        instructor: "Prof. Anjali Roy",
        status: "upcoming",
      },
    ],
  },
  wednesday: {
    day_name: "Wednesday",
    day_of_week: 3,
    sessions: [
      {
        session_id: 301,
        subject_id: 4,
        subject_code: "AE35362",
        subject_name: "Corporate Communication(L)",
        start_time: "09:00 AM",
        end_time: "10:00 AM",
        session_type: "lecture",
        room: "Room 108",
        building: "Block A",
        instructor: "Dr. N. Sengupta",
        status: "upcoming",
      },
      {
        session_id: 302,
        subject_id: 8,
        subject_code: "CS35304",
        subject_name: "Foundation of Cloud Computing(S)",
        start_time: "10:15 AM",
        end_time: "11:15 AM",
        session_type: "lecture",
        room: "Room 201",
        building: "Block A",
        instructor: "AMIT KUMAR",
        status: "upcoming",
      },
      {
        session_id: 303,
        subject_id: 2,
        subject_code: "CS35378",
        subject_name: "Mini Project - III(L)",
        start_time: "11:30 AM",
        end_time: "01:00 PM",
        session_type: "lab",
        room: "Project Lab",
        building: "Block B",
        instructor: "Prof. Saurabh Singh",
        status: "upcoming",
      },
      {
        session_id: 304,
        subject_id: 6,
        subject_code: "SE35369",
        subject_name: "Technical Skills Development-IV(L)",
        start_time: "02:00 PM",
        end_time: "03:00 PM",
        session_type: "lecture",
        room: "Room 105",
        building: "Block B",
        instructor: "VIVEK KUMAR",
        status: "upcoming",
      },
    ],
  },
  thursday: {
    day_name: "Thursday",
    day_of_week: 4,
    sessions: [
      {
        session_id: 401,
        subject_id: 7,
        subject_code: "CS35365",
        subject_name: "Scala for Data Science(L)",
        start_time: "09:00 AM",
        end_time: "10:00 AM",
        session_type: "lecture",
        room: "Room 302",
        building: "Block B",
        instructor: "BHANU PARTAP",
        status: "upcoming",
      },
      {
        session_id: 402,
        subject_id: 9,
        subject_code: "CS35364",
        subject_name: "Advance Machine Learning Practical(L)",
        start_time: "10:15 AM",
        end_time: "11:15 AM",
        session_type: "lab",
        room: "AI Lab 1",
        building: "Block B",
        instructor: "Dr. K. S. Verma",
        status: "upcoming",
      },
      {
        session_id: 403,
        subject_id: 1,
        subject_code: "CS35303",
        subject_name: "Design and Analysis of Algorithm (S)",
        start_time: "11:30 AM",
        end_time: "12:30 PM",
        session_type: "lecture",
        room: "Room 304",
        building: "Block B",
        instructor: "Dr. R. K. Sharma",
        status: "upcoming",
      },
      {
        session_id: 404,
        subject_id: 5,
        subject_code: "SI35375",
        subject_name: "Summer Internship II Evaluation(L)",
        start_time: "02:00 PM",
        end_time: "03:00 PM",
        session_type: "presentation",
        room: "Seminar Hall",
        building: "Block B",
        instructor: "Mentor Committee",
        status: "upcoming",
      },
    ],
  },
    friday: {
      day_name: "Friday",
      day_of_week: 5,
      sessions: [
        {
          session_id: 501,
          subject_id: 8,
          subject_code: "CS35304",
          subject_name: "Foundation of Cloud Computing(S)",
          start_time: "09:00 AM",
          end_time: "10:00 AM",
          session_type: "lecture",
          room: "Room 201",
          building: "Block A",
          instructor: "AMIT KUMAR",
          status: "upcoming",
        },
        {
          session_id: 502,
          subject_id: 4,
          subject_code: "AE35362",
          subject_name: "Corporate Communication(L)",
          start_time: "10:15 AM",
          end_time: "11:15 AM",
          session_type: "lecture",
          room: "Room 108",
          building: "Block A",
          instructor: "Dr. N. Sengupta",
          status: "upcoming",
        },
        {
          session_id: 503,
          subject_id: 3,
          subject_code: "CS35363",
          subject_name: "Design and Analysis of Algorithm Lab(L)",
          start_time: "11:30 AM",
          end_time: "01:00 PM",
          session_type: "lab",
          room: "Lab 304",
          building: "Block B",
          instructor: "Dr. R. K. Sharma",
          status: "upcoming",
        },
        {
          session_id: 504,
          subject_id: 10,
          subject_code: "JM3015",
          subject_name: "Event Management(L)",
          start_time: "02:00 PM",
          end_time: "03:00 PM",
          session_type: "lecture",
          room: "Room 205",
          building: "Block A",
          instructor: "Prof. Anjali Roy",
          status: "upcoming",
        },
      ],
    },
    saturday: {
      day_name: "Saturday",
      day_of_week: 6,
      sessions: [
        {
          session_id: 601,
          subject_id: 3,
          subject_code: "CS35363",
          subject_name: "Design and Analysis of Algorithm Lab(L)",
          start_time: "10:50 AM",
          end_time: "11:45 AM",
          session_type: "lab",
          room: "Lab E-202",
          building: "Block E",
          instructor: "Dr. R. K. Sharma",
          status: "upcoming",
        },
        {
          session_id: 602,
          subject_id: 5,
          subject_code: "SI35375",
          subject_name: "Summer Internship II(L)",
          start_time: "11:45 AM",
          end_time: "12:40 PM",
          session_type: "lecture",
          room: "Room A-009",
          building: "Block A",
          instructor: "Mentor Committee",
          status: "upcoming",
        },
        {
          session_id: 603,
          subject_id: 10,
          subject_code: "JM3015",
          subject_name: "Event Management(L)",
          start_time: "01:35 PM",
          end_time: "02:30 PM",
          session_type: "lecture",
          room: "Room F-204",
          building: "Block F",
          instructor: "Prof. Anjali Roy",
          status: "upcoming",
        },
        {
          session_id: 604,
          subject_id: 10,
          subject_code: "JM3015",
          subject_name: "Event Management(L)",
          start_time: "02:30 PM",
          end_time: "03:25 PM",
          session_type: "lecture",
          room: "Room F-204",
          building: "Block F",
          instructor: "Prof. Anjali Roy",
          status: "upcoming",
        },
      ],
    },
  };

  type ViewMode = "today" | "tomorrow" | "monday" | "tuesday" | "wednesday" | "thursday" | "friday" | "saturday";

  export default function TodayTimeline({ schedule, loading, userId = 1 }: TodayTimelineProps) {
    const today = new Date();
    const currentDayOfWeek = today.getDay(); // 0 is Sunday, 1..6 is Mon..Sat
    const currentHour = today.getHours();
    const isSunday = currentDayOfWeek === 0;
    const isNighttime = currentHour >= 17;

    // Intelligent default tab:
    // If Sunday, default to Monday
    // If Saturday evening, default to Monday
    // If weekday evening, default to tomorrow
    // Otherwise, today!
    const getDefaultTab = (): ViewMode => {
      if (isSunday) return "monday";
      if (isNighttime) {
        if (currentDayOfWeek === 6) return "monday";
        return "tomorrow";
      }
      return "today";
    };

    const [activeTab, setActiveTab] = useState<ViewMode>(getDefaultTab());
    const [tomorrowSchedule, setTomorrowSchedule] = useState<TodayScheduleResponse | null>(null);

    // Auto-load tomorrow's schedule
    useEffect(() => {
      fetchTomorrowSchedule(userId)
        .then((data) => setTomorrowSchedule(data))
        .catch((e) => console.error("Tomorrow schedule fetch error", e));
    }, [userId]);

    // Compute sessions to display
    let displayTitle = "Today's Schedule";
    let displaySessions: any[] = [];

    if (activeTab === "today") {
      displayTitle = `Today (${schedule?.day_name || "Today"})`;
      displaySessions = schedule?.sessions || [];
    } else if (activeTab === "tomorrow") {
      const tomorrowDayName = tomorrowSchedule?.day_name || "Tomorrow";
      displayTitle = `Kal / Tomorrow (${tomorrowDayName})`;
      displaySessions = tomorrowSchedule?.sessions || [];
    } else {
      const dayData = WEEKLY_TIMETABLE[activeTab];
      if (dayData) {
        displayTitle = `${dayData.day_name}'s Timetable`;
        displaySessions = dayData.sessions;
      }
    }

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

    return (
      <div className="rounded-2xl bg-surface border border-borderSubtle p-5 shadow-lg flex flex-col justify-between">
        <div>
          {/* Header & Day Selector Bar */}
          <div className="flex flex-col gap-3 pb-4 border-b border-borderSubtle mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-indigo-400" />
                <h3 className="font-semibold text-sm text-white">Quantum University Timetable</h3>
              </div>
              <span className="text-[11px] text-gray-400 font-medium bg-gray-900 px-2 py-0.5 rounded border border-borderSubtle">
                Sem 5 • CSE
              </span>
            </div>

            {/* Day Navigation Pills */}
            <div className="flex items-center gap-1 overflow-x-auto pb-1 scrollbar-none text-xs">
              <button
                onClick={() => setActiveTab("today")}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all shrink-0 flex items-center gap-1 ${
                  activeTab === "today"
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-gray-400 hover:text-gray-200 bg-gray-900/60"
                }`}
              >
                <Sun className="h-3 w-3" />
                <span>Today</span>
              </button>

              <button
                onClick={() => setActiveTab("tomorrow")}
                className={`px-2.5 py-1 rounded-lg font-medium transition-all shrink-0 flex items-center gap-1 ${
                  activeTab === "tomorrow"
                    ? "bg-amber-600 text-white shadow-sm"
                    : "text-gray-400 hover:text-gray-200 bg-gray-900/60"
                }`}
              >
                <Moon className="h-3 w-3" />
                <span>Kal</span>
              </button>

              <div className="h-4 w-[1px] bg-gray-800 mx-0.5 shrink-0"></div>

              {(["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"] as ViewMode[]).map((dayKey) => {
                const dayName = dayKey.slice(0, 3).toUpperCase();
                const isSelected = activeTab === dayKey;
                return (
                  <button
                    key={dayKey}
                    onClick={() => setActiveTab(dayKey)}
                    className={`px-2.5 py-1 rounded-lg font-medium transition-all shrink-0 ${
                      isSelected
                        ? "bg-voiceCyan text-gray-950 font-bold shadow-sm"
                        : "text-gray-400 hover:text-gray-200 hover:bg-gray-800 bg-gray-900/40 border border-borderSubtle/60"
                    }`}
                  >
                    {dayName}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Sunday Off Notice Banner */}
          {isSunday && activeTab === "today" && (
            <div className="mb-4 p-3 rounded-xl bg-amber-950/30 border border-amber-500/30 flex items-center justify-between text-xs text-amber-200">
              <div className="flex items-center gap-2">
                <Sun className="h-4 w-4 text-amber-400 shrink-0" />
                <span>Aaj Sunday hai — College Off! Monday se classes resume hongi.</span>
              </div>
              <button
                onClick={() => setActiveTab("monday")}
                className="text-voiceCyan underline font-semibold hover:brightness-120"
              >
                Monday ka schedule dekhein &rarr;
              </button>
            </div>
          )}

          {/* Saturday Evening Classes Completed Banner */}
          {currentDayOfWeek === 6 && isNighttime && activeTab === "today" && (
            <div className="mb-4 p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 flex items-center justify-between text-xs text-indigo-200">
              <div className="flex items-center gap-2">
                <Moon className="h-4 w-4 text-amber-400 shrink-0" />
                <span>Aaj Saturday ki classes complete ho chuki hain! Kal Sunday off hai.</span>
              </div>
              <button
                onClick={() => setActiveTab("monday")}
                className="text-amber-300 underline font-semibold hover:text-amber-200"
              >
                Monday ka schedule dekhein &rarr;
              </button>
            </div>
          )}

          {/* Weekday Evening Classes Over Banner */}
          {!isSunday && currentDayOfWeek !== 6 && isNighttime && activeTab === "today" && (
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
        {displaySessions.length === 0 ? (
          <div className="py-8 text-center text-xs text-gray-400 space-y-2">
            <p>Is din koi lectures scheduled nahi hain (Weekend / Holiday).</p>
            <button
              onClick={() => setActiveTab("monday")}
              className="text-indigo-400 underline font-medium hover:text-indigo-300"
            >
              Upcoming Monday ka schedule dekhein
            </button>
          </div>
        ) : (
          <div className="space-y-2.5">
            {displaySessions.map((s, idx) => (
              <div
                key={s.session_id || idx}
                className="p-3.5 rounded-xl border border-borderSubtle bg-surfaceHover/70 hover:border-gray-600 transition-all flex items-center justify-between"
              >
                {/* Left: Time & Divider */}
                <div className="flex items-center gap-3">
                  <div className="text-center min-w-[62px]">
                    <div className="text-xs font-semibold text-white">{s.start_time}</div>
                    <div className="text-[10px] text-gray-400">{s.end_time}</div>
                  </div>

                  <div className="h-8 w-[1px] bg-borderSubtle mx-0.5"></div>

                  {/* Class Details */}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white line-clamp-1">{s.subject_name}</span>
                      <span className="text-[9px] font-semibold text-indigo-300 uppercase bg-indigo-950/60 border border-indigo-500/30 px-1.5 py-0.2 rounded">
                        {s.session_type || "Lecture"}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-gray-400 mt-0.5">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3 text-voiceCyan" /> {s.room}, {s.building}
                      </span>
                      {s.instructor && <span className="hidden sm:inline">• {s.instructor}</span>}
                    </div>
                  </div>
                </div>

                {/* Right: Code / Status badge */}
                <div className="text-right shrink-0">
                  <span className="text-[10px] font-mono text-gray-400 bg-gray-900 px-2 py-0.5 rounded border border-borderSubtle">
                    {s.subject_code}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
