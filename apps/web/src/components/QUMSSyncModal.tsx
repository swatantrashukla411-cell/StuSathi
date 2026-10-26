"use client";

import React, { useState, useEffect } from "react";
import { X, RefreshCw, Shield, Lock, User, CheckCircle2, AlertTriangle, Eye, EyeOff } from "lucide-react";
import { fetchQUMSCaptcha, syncQUMS, QUMSCaptcha } from "@/lib/api";

interface QUMSSyncModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSyncSuccess: () => void;
}

export default function QUMSSyncModal({ isOpen, onClose, onSyncSuccess }: QUMSSyncModalProps) {
  const [captchaData, setCaptchaData] = useState<QUMSCaptcha | null>(null);
  const [qid, setQid] = useState("");
  const [password, setPassword] = useState("");
  const [captcha, setCaptcha] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [loadingCaptcha, setLoadingCaptcha] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const loadCaptcha = async () => {
    setLoadingCaptcha(true);
    setErrorMsg(null);
    try {
      const data = await fetchQUMSCaptcha();
      setCaptchaData(data);
    } catch (err: any) {
      setErrorMsg(err.message || "Unable to connect to Quantum University QUMS server. Please check your internet.");
    } finally {
      setLoadingCaptcha(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      loadCaptcha();
      setErrorMsg(null);
      setSuccessMsg(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!captchaData) return;

    if (!qid.trim() || !password.trim() || !captcha.trim()) {
      setErrorMsg("Please fill in QID, Password, and the Captcha code.");
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await syncQUMS({
        session_token: captchaData.session_token,
        qid: qid.trim(),
        password: password.trim(),
        captcha: captcha.trim(),
      });
      setSuccessMsg(res.message || "Attendance & schedule successfully synced from QUMS!");
      setTimeout(() => {
        onSyncSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      setErrorMsg(err.message || "Sync failed. Please verify your QID, password, and captcha.");
      loadCaptcha(); // refresh captcha on failed attempt
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in">
      <div className="w-full max-w-md rounded-2xl bg-surface border border-indigo-500/30 shadow-2xl p-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white p-1 rounded-lg bg-surfaceHover border border-borderSubtle"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 pb-4 border-b border-borderSubtle">
          <div className="h-10 w-10 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
            <RefreshCw className="h-5 w-5 text-indigo-400" />
          </div>
          <div>
            <h3 className="font-bold text-base text-white">Quantum University (QUMS) Sync</h3>
            <p className="text-xs text-gray-400">Live attendance & schedule extraction</p>
          </div>
        </div>

        {/* Alerts */}
        {errorMsg && (
          <div className="mt-4 p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="mt-4 p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="mt-4 space-y-3.5">
          {/* QID Input */}
          <div>
            <label className="text-xs font-semibold text-gray-300 block mb-1">
              Quantum ID (QID / Roll Number)
            </label>
            <div className="relative">
              <User className="absolute left-3 top-3 h-4 w-4 text-gray-500" />
              <input
                type="text"
                placeholder="e.g. 220101001"
                value={qid}
                onChange={(e) => setQid(e.target.value)}
                className="w-full bg-gray-900 border border-borderSubtle rounded-xl pl-9 pr-3 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          {/* Password Input */}
          <div>
            <label className="text-xs font-semibold text-gray-300 block mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-500" />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="QUMS portal password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-gray-900 border border-borderSubtle rounded-xl pl-9 pr-10 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2.5 text-gray-500 hover:text-gray-300"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* Live Captcha Section */}
          <div>
            <label className="text-xs font-semibold text-gray-300 block mb-1">
              Live QUMS Captcha
            </label>
            <div className="flex items-center gap-2">
              <div className="h-10 flex-1 bg-white rounded-xl overflow-hidden flex items-center justify-center border border-borderSubtle">
                {loadingCaptcha ? (
                  <span className="text-xs text-gray-600 animate-pulse">Loading Captcha...</span>
                ) : captchaData?.captcha_image ? (
                  <img
                    src={captchaData.captcha_image}
                    alt="QUMS Captcha"
                    className="h-9 object-contain"
                  />
                ) : (
                  <span className="text-xs text-red-500">Failed to load</span>
                )}
              </div>

              <button
                type="button"
                onClick={loadCaptcha}
                disabled={loadingCaptcha}
                title="Refresh Captcha"
                className="h-10 px-3 rounded-xl bg-surfaceHover border border-borderSubtle text-gray-300 hover:text-white"
              >
                <RefreshCw className={`h-4 w-4 ${loadingCaptcha ? "animate-spin" : ""}`} />
              </button>
            </div>

            <input
              type="text"
              placeholder="Enter characters from image above"
              value={captcha}
              onChange={(e) => setCaptcha(e.target.value)}
              className="mt-2 w-full bg-gray-900 border border-borderSubtle rounded-xl px-3 py-2 text-xs text-white uppercase placeholder-gray-500 focus:outline-none focus:border-indigo-500 text-center tracking-widest font-bold"
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full mt-4 py-2.5 px-4 rounded-xl bg-gradient-to-r from-agentIndigo to-indigo-600 hover:brightness-110 text-white text-xs font-semibold transition-all shadow-lg shadow-agentIndigo/20 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {submitting ? (
              <>
                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                <span>Logging into QUMS & Extracting Attendance...</span>
              </>
            ) : (
              <span>⚡ Authenticate & Sync My Data</span>
            )}
          </button>
        </form>

        {/* Security Disclaimers */}
        <div className="mt-4 pt-3 border-t border-borderSubtle/60 flex items-start gap-2 text-[10px] text-gray-400">
          <Shield className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
          <span>
            <strong>Zero Password Storage:</strong> Your QUMS password is kept purely in temporary memory during this single request to fetch records, and is never saved to the database.
          </span>
        </div>
      </div>
    </div>
  );
}
