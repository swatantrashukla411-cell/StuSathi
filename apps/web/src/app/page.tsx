"use client";

import React, { useState, useEffect } from "react";
import Header from "@/components/Header";
import NextClassHero from "@/components/NextClassHero";
import TodayTimeline from "@/components/TodayTimeline";
import AttendanceRadar from "@/components/AttendanceRadar";
import GPAOrbit from "@/components/GPAOrbit";
import QUMSSyncModal from "@/components/QUMSSyncModal";
import VoiceAssistantModal from "@/components/VoiceAssistantModal";

import {
  fetchTodaySchedule,
  fetchNextClass,
  fetchAttendanceSummary,
  fetchGPASummary,
  TodayScheduleResponse,
  NextClassResponse,
  SubjectAttendance,
  GPASummaryResponse,
} from "@/lib/api";
import { Mic, Sparkles } from "lucide-react";

export default function DashboardPage() {
  const [schedule, setSchedule] = useState<TodayScheduleResponse | null>(null);
  const [nextClass, setNextClass] = useState<NextClassResponse | null>(null);
  const [subjects, setSubjects] = useState<SubjectAttendance[]>([]);
  const [gpaData, setGpaData] = useState<GPASummaryResponse | null>(null);

  const [loadingSchedule, setLoadingSchedule] = useState(true);
  const [loadingNext, setLoadingNext] = useState(true);
  const [loadingAttendance, setLoadingAttendance] = useState(true);
  const [loadingGPA, setLoadingGPA] = useState(true);

  const [isQUMSOpen, setIsQUMSOpen] = useState(false);
  const [isVoiceOpen, setIsVoiceOpen] = useState(false);

  const loadAllData = async () => {
    // 1. Next Class
    fetchNextClass()
      .then((data) => setNextClass(data))
      .catch((e) => console.error("Next class load error", e))
      .finally(() => setLoadingNext(false));

    // 2. Today's Schedule
    fetchTodaySchedule()
      .then((data) => setSchedule(data))
      .catch((e) => console.error("Schedule load error", e))
      .finally(() => setLoadingSchedule(false));

    // 3. Attendance Summary
    fetchAttendanceSummary()
      .then((data) => setSubjects(data))
      .catch((e) => console.error("Attendance load error", e))
      .finally(() => setLoadingAttendance(false));

    // 4. GPA Summary
    fetchGPASummary()
      .then((data) => setGpaData(data))
      .catch((e) => console.error("GPA load error", e))
      .finally(() => setLoadingGPA(false));
  };

  useEffect(() => {
    loadAllData();
  }, []);

  return (
    <div className="min-h-screen bg-background text-gray-100 flex flex-col pb-20 relative">
      {/* Header */}
      <Header
        onOpenQUMS={() => setIsQUMSOpen(true)}
        onOpenVoice={() => setIsVoiceOpen(true)}
        isVoiceActive={isVoiceOpen}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 lg:px-8 py-6 space-y-6">
        {/* Next Class Countdown Hero */}
        <NextClassHero data={nextClass} loading={loadingNext} />

        {/* 2-Column Section: Schedule & GPA Orbit */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TodayTimeline schedule={schedule} loading={loadingSchedule} />
          <GPAOrbit data={gpaData} loading={loadingGPA} />
        </div>

        {/* Attendance Intelligence Radar */}
        <AttendanceRadar subjects={subjects} loading={loadingAttendance} />
      </main>

      {/* Floating Bottom-Right Voice Orb */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => setIsVoiceOpen(true)}
          className="group relative h-14 w-14 rounded-full bg-gradient-to-tr from-agentIndigo to-voiceCyan text-gray-950 flex items-center justify-center shadow-2xl shadow-agentIndigo/40 hover:scale-105 transition-all animate-pulse-glow"
          title="Tap to talk to CampusPilot Voice Agent"
        >
          <Mic className="h-6 w-6 text-gray-950 group-hover:scale-110 transition-transform" />
          <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-emerald-400 border-2 border-background"></span>
        </button>
      </div>

      {/* QUMS Sync Modal */}
      <QUMSSyncModal
        isOpen={isQUMSOpen}
        onClose={() => setIsQUMSOpen(false)}
        onSyncSuccess={loadAllData}
      />

      {/* Voice Assistant Modal */}
      <VoiceAssistantModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
      />
    </div>
  );
}
