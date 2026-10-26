"use client";

import React, { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Send, X, Sparkles, Volume2, Bot, User, Radio } from "lucide-react";
import { sendChatMessage } from "@/lib/api";

interface Message {
  sender: "user" | "agent";
  text: string;
  toolInvoked?: string;
}

interface VoiceAssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function VoiceAssistantModal({ isOpen, onClose }: VoiceAssistantModalProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "agent",
      text: "Hey Swatantra! Main aapka CampusPilot assistant hoon. Aap mujhse puchh sakte hain: 'Meri next class kaunsi hai?', 'Aaj DBMS miss karun toh kya hoga?', ya '75% recovery ke liye kitni classes attend karni padengi?'",
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recognitionSupported, setRecognitionSupported] = useState(true);

  const recognitionRef = useRef<any>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isProcessing]);

  // Initialize Web Speech API for voice recognition
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-IN"; // Supports Indian English & Hinglish accents

        recognition.onstart = () => setIsListening(true);
        recognition.onend = () => setIsListening(false);
        recognition.onerror = () => setIsListening(false);

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          if (transcript) {
            handleSendMessage(transcript);
          }
        };

        recognitionRef.current = recognition;
      } else {
        setRecognitionSupported(false);
      }
    }
  }, []);

  if (!isOpen) return null;

  const toggleListening = () => {
    if (!recognitionRef.current) return;
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
      } catch (e) {
        console.error(e);
      }
    }
  };

  const speakText = (text: string) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "en-IN";
      utterance.rate = 1.05;
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleSendMessage = async (queryText: string) => {
    const text = queryText.trim();
    if (!text) return;

    setInputText("");
    setMessages((prev) => [...prev, { sender: "user", text }]);
    setIsProcessing(true);

    try {
      const res = await sendChatMessage(text);
      setMessages((prev) => [
        ...prev,
        { sender: "agent", text: res.reply, toolInvoked: res.tool_invoked },
      ]);
      // Speak the response aloud naturally
      speakText(res.reply);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: "Sorry, main backend se connect nahi kar paya. Please verify that FastAPI is running.",
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in">
      <div className="w-full max-w-xl h-[560px] rounded-2xl bg-surface border border-indigo-500/30 shadow-2xl flex flex-col justify-between overflow-hidden relative">
        {/* Header */}
        <div className="p-4 border-b border-borderSubtle bg-surfaceHover/50 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-lg bg-agentIndigo flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white flex items-center gap-2">
                <span>CampusPilot AI Voice Agent</span>
                <span className="text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.2 rounded-full">
                  Live
                </span>
              </h3>
              <p className="text-[11px] text-gray-400">Speaks in Hindi, Hinglish, & English</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white p-1 rounded-lg bg-surface border border-borderSubtle"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Messages Scroll Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3.5">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${m.sender === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl p-3 text-xs leading-relaxed ${
                  m.sender === "user"
                    ? "bg-indigo-600 text-white rounded-tr-none shadow-md"
                    : "bg-surfaceHover border border-borderSubtle text-gray-200 rounded-tl-none"
                }`}
              >
                {/* Tool Tag if executed */}
                {m.toolInvoked && (
                  <div className="mb-1.5 inline-flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wider text-voiceCyan bg-cyan-950/40 border border-cyan-500/30 px-2 py-0.5 rounded">
                    <Sparkles className="h-2.5 w-2.5" />
                    <span>Executed Tool: {m.toolInvoked}</span>
                  </div>
                )}
                <p>{m.text}</p>
              </div>

              {/* Speaker action */}
              {m.sender === "agent" && (
                <button
                  onClick={() => speakText(m.text)}
                  className="mt-1 text-[10px] text-gray-400 hover:text-voiceCyan flex items-center gap-1 ml-1"
                >
                  <Volume2 className="h-3 w-3" />
                  <span>Listen Again</span>
                </button>
              )}
            </div>
          ))}

          {isProcessing && (
            <div className="flex items-center gap-2 text-xs text-indigo-300 animate-pulse pl-2">
              <Sparkles className="h-3.5 w-3.5 animate-spin" />
              <span>CampusPilot is reasoning & calculating...</span>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {/* Voice Trigger & Input Footer */}
        <div className="p-4 border-t border-borderSubtle bg-surfaceHover/30 space-y-3">
          {/* Quick Voice Bar */}
          <div className="flex items-center justify-center">
            <button
              onClick={toggleListening}
              className={`relative px-5 py-2.5 rounded-full flex items-center gap-2.5 text-xs font-bold transition-all shadow-xl ${
                isListening
                  ? "bg-rose-600 text-white shadow-rose-500/40 animate-pulse ring-4 ring-rose-500/20"
                  : "bg-gradient-to-r from-agentIndigo to-voiceCyan text-gray-950 hover:brightness-110 shadow-indigo-500/30"
              }`}
            >
              {isListening ? (
                <>
                  <Radio className="h-4 w-4 animate-spin text-white" />
                  <span>Listening... Tap to Stop</span>
                </>
              ) : (
                <>
                  <Mic className="h-4 w-4 text-gray-950" />
                  <span>Tap to Speak (Hinglish / English)</span>
                </>
              )}
            </button>
          </div>

          {/* Text Input Fallback */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage(inputText);
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Or type a question (e.g. 'DBMS miss karun toh attendance kitni hogi?')"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="flex-1 bg-gray-900 border border-borderSubtle rounded-xl px-3.5 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500"
            />
            <button
              type="submit"
              disabled={!inputText.trim()}
              className="p-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-40"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
