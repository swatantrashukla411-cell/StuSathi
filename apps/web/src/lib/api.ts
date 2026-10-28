/**
 * CampusPilot AI Frontend API Client
 * Typed fetch wrappers communicating with the FastAPI backend.
 */

function getApiBase(): string {
  if (typeof window !== "undefined") {
    return "/api/v1";
  }
  const rawBase =
    process.env.API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.BACKEND_API_URL ||
    "http://127.0.0.1:8001";
  const trimmed = rawBase.endsWith("/") ? rawBase.slice(0, -1) : rawBase;
  return trimmed.endsWith("/api/v1") ? trimmed : `${trimmed}/api/v1`;
}

const API_BASE = getApiBase();

export interface TodaySession {
  session_id: number;
  subject_id: number;
  subject_code: string;
  subject_name: string;
  start_time: string;
  end_time: string;
  session_type: string;
  room: string;
  building: string;
  instructor?: string;
  status: "completed" | "ongoing" | "upcoming";
}

export interface TodayScheduleResponse {
  date: string;
  day_name: string;
  day_of_week: number;
  total_classes: number;
  sessions: TodaySession[];
}

export interface NextClassResponse {
  has_upcoming: boolean;
  subject_name?: string;
  subject_code?: string;
  start_time?: string;
  room?: string;
  building?: string;
  instructor?: string;
  minutes_remaining?: number | null;
  message: string;
  is_tomorrow?: boolean;
  day_label?: string;
}

export interface SubjectAttendance {
  subject_code: string;
  subject_name: string;
  classes_conducted: number;
  classes_attended: number;
  classes_missed: number;
  current_percentage: number;
  required_threshold: number;
  remaining_planned_sessions: number;
  safe_future_absences: number;
  risk_category: "safe" | "caution" | "critical" | "unrecoverable";
  explanation: string;
}

export interface SimulateResponse {
  current_percentage: number;
  projected_percentage: number;
  threshold_percentage: number;
  sessions_missed_in_sim: number;
  safe_absences_remaining_after: number;
  risk_category_after: string;
  is_safe: boolean;
  explanation: string;
}

export interface RecoveryResponse {
  current_percentage: number;
  target_threshold: number;
  classes_needed_consecutively: number;
  remaining_sessions_available: number;
  is_recoverable: boolean;
  max_possible_percentage: number;
  explanation: string;
}

export interface GPASummaryResponse {
  current_semester_sgpa?: {
    total_credits: number;
    sgpa: number;
  };
  cumulative_cgpa?: {
    total_completed_credits: number;
    cgpa: number;
  };
  semesters_evaluated: number;
}

export interface TargetGPAResponse {
  current_cgpa: number;
  target_cgpa: number;
  completed_credits: number;
  remaining_credits: number;
  required_future_sgpa: number;
  is_achievable: boolean;
  max_possible_cgpa: number;
  explanation: string;
}

export interface QUMSCaptcha {
  session_token: string;
  captcha_image: string;
  form_token: string;
}

export async function fetchTodaySchedule(userId: number = 1, targetDate?: string): Promise<TodayScheduleResponse> {
  const url = targetDate
    ? `${API_BASE}/timetable/today?user_id=${userId}&target_date=${targetDate}`
    : `${API_BASE}/timetable/today?user_id=${userId}`;
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load today's schedule");
  return res.json();
}

export async function fetchTomorrowSchedule(userId: number = 1): Promise<TodayScheduleResponse> {
  const res = await fetch(`${API_BASE}/timetable/tomorrow?user_id=${userId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load tomorrow's schedule");
  return res.json();
}

export async function fetchNextClass(userId: number = 1): Promise<NextClassResponse> {
  const res = await fetch(`${API_BASE}/timetable/next?user_id=${userId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load next class");
  return res.json();
}

export async function fetchAttendanceSummary(userId: number = 1): Promise<SubjectAttendance[]> {
  const res = await fetch(`${API_BASE}/attendance/summary?user_id=${userId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load attendance summary");
  return res.json();
}

export async function simulateAbsence(payload: {
  classes_conducted: number;
  classes_attended: number;
  remaining_planned_sessions: number;
  sessions_to_miss: number;
  required_threshold?: number;
}): Promise<SimulateResponse> {
  const res = await fetch(`${API_BASE}/attendance/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Simulation failed");
  return res.json();
}

export async function calculateRecovery(payload: {
  classes_conducted: number;
  classes_attended: number;
  remaining_planned_sessions: number;
  target_threshold?: number;
}): Promise<RecoveryResponse> {
  const res = await fetch(`${API_BASE}/attendance/recover`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Recovery calculation failed");
  return res.json();
}

export async function fetchGPASummary(userId: number = 1): Promise<GPASummaryResponse> {
  const res = await fetch(`${API_BASE}/gpa/summary?user_id=${userId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load GPA summary");
  return res.json();
}

export async function solveTargetCGPA(payload: {
  current_cgpa: number;
  completed_credits: number;
  remaining_credits: number;
  target_cgpa: number;
  max_scale?: number;
}): Promise<TargetGPAResponse> {
  const res = await fetch(`${API_BASE}/gpa/target`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Target GPA calculation failed");
  return res.json();
}

export async function fetchQUMSCaptcha(): Promise<QUMSCaptcha> {
  const res = await fetch(`${API_BASE}/integrations/qums/captcha`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch QUMS captcha");
  return res.json();
}

export async function syncQUMS(payload: {
  session_token: string;
  qid: string;
  password: string;
  captcha: string;
  user_id?: number;
}) {
  const res = await fetch(`${API_BASE}/integrations/qums/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "QUMS sync failed");
  }
  return res.json();
}

export async function demoSyncQUMS(userId: number = 1) {
  const res = await fetch(`${API_BASE}/integrations/qums/demo-sync?user_id=${userId}`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Demo sync failed");
  }
  return res.json();
}

export async function sendChatMessage(message: string, userId: number = 1) {
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, user_id: userId }),
  });
  if (!res.ok) throw new Error("Failed to send message to agent");
  return res.json();
}

export interface StudentProfile {
  user_id: number;
  full_name: string;
  email: string;
  program: string;
  active_semester: number;
  created_at: string;
}

export async function loginStudent(emailOrQid: string, password?: string): Promise<StudentProfile> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email_or_qid: emailOrQid, password: password || "student123" }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Student login failed");
  }
  return res.json();
}

export async function registerStudent(payload: {
  full_name: string;
  email_or_qid: string;
  program?: string;
  semester_number?: number;
}): Promise<StudentProfile> {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      full_name: payload.full_name,
      email_or_qid: payload.email_or_qid,
      program: payload.program || "B.Tech Computer Science & Engineering (AI/ML)",
      semester_number: payload.semester_number || 5,
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Registration failed");
  }
  return res.json();
}

export async function fetchRegisteredStudents(): Promise<{ students: StudentProfile[] }> {
  const res = await fetch(`${API_BASE}/auth/students`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load student profiles");
  return res.json();
}

export async function fetchCurrentStudent(userId: number): Promise<StudentProfile> {
  const res = await fetch(`${API_BASE}/auth/me?user_id=${userId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load student profile");
  return res.json();
}
