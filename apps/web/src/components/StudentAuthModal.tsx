"use client";

import React, { useState, useEffect } from "react";
import { X, User, UserPlus, LogIn, CheckCircle2, Sparkles, BookOpen, GraduationCap, Shield } from "lucide-react";
import { loginStudent, registerStudent, fetchRegisteredStudents, StudentProfile } from "@/lib/api";

interface StudentAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentStudent: StudentProfile | null;
  onStudentChange: (student: StudentProfile) => void;
}

export default function StudentAuthModal({
  isOpen,
  onClose,
  currentStudent,
  onStudentChange,
}: StudentAuthModalProps) {
  const [tab, setTab] = useState<"switch" | "register">("switch");

  // Sign in form state
  const [loginId, setLoginId] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Register form state
  const [fullName, setFullName] = useState("");
  const [registerId, setRegisterId] = useState("");
  const [program, setProgram] = useState("B.Tech Computer Science & Engineering (AI/ML)");
  const [semesterNumber, setSemesterNumber] = useState(5);

  const [availableStudents, setAvailableStudents] = useState<StudentProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Load existing student profiles
  useEffect(() => {
    if (isOpen) {
      loadStudents();
      setErrorMsg(null);
    }
  }, [isOpen]);

  const loadStudents = async () => {
    try {
      const res = await fetchRegisteredStudents();
      setAvailableStudents(res.students);
    } catch (e) {
      console.warn("Could not load student list:", e);
    }
  };

  if (!isOpen) return null;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginId.trim()) {
      setErrorMsg("Please enter your College QID or Email ID.");
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    try {
      const student = await loginStudent(loginId.trim(), loginPassword.trim() || undefined);
      onStudentChange(student);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to log in student.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegisterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !registerId.trim()) {
      setErrorMsg("Please provide both your Full Name and College QID.");
      return;
    }

    setLoading(true);
    setErrorMsg(null);
    try {
      const newStudent = await registerStudent({
        full_name: fullName.trim(),
        email_or_qid: registerId.trim(),
        program,
        semester_number: semesterNumber,
      });
      onStudentChange(newStudent);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in">
      <div className="w-full max-w-lg rounded-2xl bg-surface border border-indigo-500/30 shadow-2xl overflow-hidden relative">
        {/* Header */}
        <div className="p-5 border-b border-borderSubtle bg-surfaceHover/50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
              <GraduationCap className="h-5 w-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="font-bold text-base text-white">Student Account & Profile</h3>
              <p className="text-xs text-gray-400">Multi-tenant academic session management</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1.5 rounded-lg bg-surface border border-borderSubtle"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-borderSubtle bg-gray-900/40">
          <button
            onClick={() => {
              setTab("switch");
              setErrorMsg(null);
            }}
            className={`flex-1 py-3 text-xs font-semibold flex items-center justify-center gap-2 border-b-2 transition-all ${
              tab === "switch"
                ? "border-indigo-500 text-indigo-400 bg-indigo-950/20"
                : "border-transparent text-gray-400 hover:text-white"
            }`}
          >
            <LogIn className="h-3.5 w-3.5" />
            <span>Sign In / Switch Student</span>
          </button>

          <button
            onClick={() => {
              setTab("register");
              setErrorMsg(null);
            }}
            className={`flex-1 py-3 text-xs font-semibold flex items-center justify-center gap-2 border-b-2 transition-all ${
              tab === "register"
                ? "border-indigo-500 text-indigo-400 bg-indigo-950/20"
                : "border-transparent text-gray-400 hover:text-white"
            }`}
          >
            <UserPlus className="h-3.5 w-3.5" />
            <span>+ New Student Registration</span>
          </button>
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="mx-5 mt-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            {errorMsg}
          </div>
        )}

        {/* Tab 1: Sign in / Switch */}
        {tab === "switch" && (
          <div className="p-5 space-y-5">
            {/* Quick Switch from Registered Students */}
            {availableStudents.length > 0 && (
              <div className="space-y-2">
                <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                  Quick Select Active Student Profile:
                </label>
                <div className="space-y-2 max-h-44 overflow-y-auto pr-1">
                  {availableStudents.map((st) => (
                    <div
                      key={st.user_id}
                      onClick={() => {
                        onStudentChange(st);
                        onClose();
                      }}
                      className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                        currentStudent?.user_id === st.user_id
                          ? "bg-indigo-950/40 border-indigo-500/50 shadow-md ring-1 ring-indigo-500/30"
                          : "bg-surfaceHover/50 border-borderSubtle hover:border-indigo-500/30 hover:bg-surfaceHover"
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-agentIndigo to-voiceCyan flex items-center justify-center text-xs font-bold text-gray-950">
                          {st.full_name[0]}
                        </div>
                        <div>
                          <p className="text-xs font-bold text-white flex items-center gap-1.5">
                            <span>{st.full_name}</span>
                            {currentStudent?.user_id === st.user_id && (
                              <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                                Active
                              </span>
                            )}
                          </p>
                          <p className="text-[11px] text-gray-400">
                            Sem {st.active_semester} • {st.email}
                          </p>
                        </div>
                      </div>

                      <button className="text-xs text-voiceCyan hover:underline font-semibold">
                        {currentStudent?.user_id === st.user_id ? "Selected" : "Switch →"}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Custom QID / Email Login */}
            <form onSubmit={handleLoginSubmit} className="space-y-3 pt-2 border-t border-borderSubtle">
              <label className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">
                Or Sign In with QID / College Email:
              </label>

              <div className="space-y-2">
                <input
                  type="text"
                  placeholder="Enter QID (e.g. 22010199) or College Email"
                  value={loginId}
                  onChange={(e) => setLoginId(e.target.value)}
                  className="w-full bg-gray-900 border border-borderSubtle rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
                />

                <input
                  type="password"
                  placeholder="Password (optional for demo / instant login)"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full bg-gray-900 border border-borderSubtle rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !loginId.trim()}
                className="w-full py-2.5 rounded-xl bg-gradient-to-r from-agentIndigo to-indigo-600 hover:brightness-110 text-white font-bold text-xs shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-40"
              >
                {loading ? "Authenticating..." : "Sign In & Open Dashboard"}
              </button>
            </form>
          </div>
        )}

        {/* Tab 2: Register New Student */}
        {tab === "register" && (
          <form onSubmit={handleRegisterSubmit} className="p-5 space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-300">Student Full Name *</label>
              <input
                type="text"
                placeholder="e.g. Aman Verma"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                className="w-full bg-gray-900 border border-borderSubtle rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-gray-300">Quantum University QID / Email *</label>
              <input
                type="text"
                placeholder="e.g. 22010450 or aman.v@quantumuniversity.edu.in"
                value={registerId}
                onChange={(e) => setRegisterId(e.target.value)}
                required
                className="w-full bg-gray-900 border border-borderSubtle rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-300">Current Semester</label>
                <select
                  value={semesterNumber}
                  onChange={(e) => setSemesterNumber(Number(e.target.value))}
                  className="w-full bg-gray-900 border border-borderSubtle rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8].map((s) => (
                    <option key={s} value={s}>
                      Semester {s}
                    </option>
                  ))}
                </select>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-gray-300">Degree & Branch</label>
                <select
                  value={program}
                  onChange={(e) => setProgram(e.target.value)}
                  className="w-full bg-gray-900 border border-borderSubtle rounded-xl px-3 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="B.Tech Computer Science & Engineering (AI/ML)">B.Tech CSE (AI/ML)</option>
                  <option value="B.Tech Computer Science & Engineering">B.Tech CSE Core</option>
                  <option value="B.Tech Mechanical Engineering">B.Tech Mechanical</option>
                  <option value="BCA Computer Applications">BCA</option>
                  <option value="MCA Masters in Computer Applications">MCA</option>
                </select>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-[11px] text-indigo-300 flex items-start gap-2">
              <Sparkles className="h-4 w-4 text-voiceCyan flex-shrink-0 mt-0.5" />
              <span>
                Registering will automatically initialize your Semester timetable, 5 core subjects, and 75% attendance tracking radar!
              </span>
            </div>

            <button
              type="submit"
              disabled={loading || !fullName.trim() || !registerId.trim()}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-agentIndigo to-voiceCyan hover:brightness-110 text-gray-950 font-bold text-xs shadow-lg shadow-indigo-500/25 transition-all disabled:opacity-40"
            >
              {loading ? "Creating Profile..." : "Create Account & Launch Dashboard"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
