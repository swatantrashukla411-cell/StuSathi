"use client";

import React, { useState, useEffect, useCallback } from "react";
import Header from "@/components/Header";
import NextClassHero from "@/components/NextClassHero";
import TodayTimeline from "@/components/TodayTimeline";
import AttendanceRadar from "@/components/AttendanceRadar";
import GPAOrbit from "@/components/GPAOrbit";
import QUMSSyncModal from "@/components/QUMSSyncModal";
import VoiceAssistantModal from "@/components/VoiceAssistantModal";
import StudentAuthModal from "@/components/StudentAuthModal";

import {
  fetchTodaySchedule,
  fetchNextClass,
  fetchAttendanceSummary,
  fetchGPASummary,
  fetchCurrentStudent,
  TodayScheduleResponse,
  NextClassResponse,
  SubjectAttendance,
  GPASummaryResponse,
  StudentProfile,
} from "@/lib/api";
import { Mic, Sparkles } from "lucide-react";

export default function DashboardPage() {
  const [student, setStudent] = useState<StudentProfile | null>(null);
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
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  // Initialize active student profile from localStorage or default to student 1 (Swatantra)
  useEffect(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("campuspilot_active_student");
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setStudent(parsed);
          return;
        } catch (e) {}
      }
    }
    // Fallback load default profile
    fetchCurrentStudent(1)
      .then((st) => {
        setStudent(st);
        if (typeof window !== "undefined") {
          localStorage.setItem("campuspilot_active_student", JSON.stringify(st));
        }
      })
      .catch(() => {
        // Fallback default
        setStudent({
          user_id: 1,
          full_name: "Swatantra Shukla",
          email: "swatantrashukla411@gmail.com",
          program: "B.Tech Computer Science & Engineering (AI/ML)",
          active_semester: 5,
          created_at: new Date().toISOString(),
        });
      });
  }, []);

  const loadAllData = useCallback(async (userId: number) => {
    setLoadingNext(true);
    setLoadingSchedule(true);
    setLoadingAttendance(true);
    setLoadingGPA(true);

    // 1. Next Class
    fetchNextClass(userId)
      .then((data) => setNextClass(data))
      .catch((e) => console.error("Next class load error", e))
      .finally(() => setLoadingNext(false));

    // 2. Today's Schedule
    fetchTodaySchedule(userId)
      .then((data) => setSchedule(data))
      .catch((e) => console.error("Schedule load error", e))
      .finally(() => setLoadingSchedule(false));

    // 3. Attendance Summary
    fetchAttendanceSummary(userId)
      .then((data) => setSubjects(data))
      .catch((e) => console.error("Attendance load error", e))
      .finally(() => setLoadingAttendance(false));

    // 4. GPA Summary
    fetchGPASummary(userId)
      .then((data) => setGpaData(data))
      .catch((e) => console.error("GPA load error", e))
      .finally(() => setLoadingGPA(false));
  }, []);

  useEffect(() => {
    if (student?.user_id) {
      loadAllData(student.user_id);
    }
  }, [student?.user_id, loadAllData]);

  const handleStudentChange = (newStudent: StudentProfile) => {
    setStudent(newStudent);
    if (typeof window !== "undefined") {
      localStorage.setItem("campuspilot_active_student", JSON.stringify(newStudent));
    }
    loadAllData(newStudent.user_id);
  };

  return (
    <div className="min-h-screen bg-background text-gray-100 flex flex-col pb-20 relative">
      {/* Header */}
      <Header
        onOpenQUMS={() => setIsQUMSOpen(true)}
        onOpenVoice={() => setIsVoiceOpen(true)}
        onOpenAuth={() => setIsAuthOpen(true)}
        isVoiceActive={isVoiceOpen}
        student={student}
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

      {/* Student Account & Authentication Switcher Modal */}
      <StudentAuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        currentStudent={student}
        onStudentChange={handleStudentChange}
      />

      {/* QUMS Sync Modal */}
      <QUMSSyncModal
        isOpen={isQUMSOpen}
        onClose={() => setIsQUMSOpen(false)}
        onSyncSuccess={() => student?.user_id && loadAllData(student.user_id)}
        userId={student?.user_id || 1}
      />

      {/* Voice Assistant Modal */}
      <VoiceAssistantModal
        isOpen={isVoiceOpen}
        onClose={() => setIsVoiceOpen(false)}
        userId={student?.user_id || 1}
        studentName={student?.full_name}
      />
    </div>
  );
}
