"use client";

import React, { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Send, X, Sparkles, Volume2, Bot, User, Radio, AlertCircle, VolumeX } from "lucide-react";
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
      text: "Hey Swatantra! Main aapka CampusPilot AI assistant hoon. Aap mujhse bolkar puchh sakte hain: 'Meri next class kab hai?', 'DBMS me kitne bunk safe hain?', ya '75% attendance ke liye kya karna hoga?'",
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [liveInterim, setLiveInterim] = useState("");
  const [voiceError, setVoiceError] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const accumulatedSpeechRef = useRef<string>("");
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isProcessing, liveInterim]);

  // Clean up audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
      }
    };
  }, []);

  // Initialize Web Speech API for voice recognition with auto-stop silence detection
  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = true; // Stay alive to catch whole sentence
        recognition.interimResults = true; // Stream words in real time
        recognition.lang = "en-IN"; // Supports Indian English & Hinglish accents

        recognition.onstart = () => {
          setIsListening(true);
          setVoiceError(null);
          setLiveInterim("");
          accumulatedSpeechRef.current = "";
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognition.onerror = (event: any) => {
          setIsListening(false);
          if (event.error === "not-allowed" || event.error === "permission-denied") {
            setVoiceError("Microphone permission blocked. Please click the lock icon in the browser address bar to allow microphone access.");
          } else if (event.error === "no-speech") {
            setVoiceError("No speech detected. Please tap the mic and try speaking again.");
          }
        };

        recognition.onresult = (event: any) => {
          // Clear any pending silence timer because user is actively speaking!
          if (silenceTimeoutRef.current) {
            clearTimeout(silenceTimeoutRef.current);
          }

          let finalTranscript = "";
          let interimTranscript = "";

          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              finalTranscript += event.results[i][0].transcript;
            } else {
              interimTranscript += event.results[i][0].transcript;
            }
          }

          const currentWords = (finalTranscript || interimTranscript).trim();
          if (currentWords) {
            accumulatedSpeechRef.current = currentWords;
            setLiveInterim(currentWords);

            // 🎯 AUTO-STOP ON SILENCE:
            // When user stops speaking for 1.3 seconds, automatically stop & send!
            silenceTimeoutRef.current = setTimeout(() => {
              if (recognitionRef.current) {
                try {
                  recognitionRef.current.stop();
                } catch (e) {}
              }
              setIsListening(false);
              const textToSend = accumulatedSpeechRef.current.trim();
              setLiveInterim("");
              accumulatedSpeechRef.current = "";
              if (textToSend) {
                handleSendMessage(textToSend);
              }
            }, 1300);
          }
        };

        recognitionRef.current = recognition;
      }
    }
  }, []);

  if (!isOpen) return null;

  // Primary: Edge Neural High-Fidelity Voice Stream (zero OS dependency)
  // Fallback: Browser Web Speech API
  const playSpeech = (text: string) => {
    try {
      // Stop any existing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }

      const cleanText = text
        .replace(/[*_#`~[\]()]/g, "")
        .replace(/https?:\/\/\S+/g, "")
        .trim();

      // Use backend neural stream
      const audioUrl = `/api/v1/agent/tts?text=${encodeURIComponent(cleanText)}&voice=hi-IN-SwaraNeural`;
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      setIsSpeaking(true);

      audio.onended = () => {
        setIsSpeaking(false);
      };

      audio.onerror = () => {
        // Fallback to browser SpeechSynthesis
        fallbackBrowserTTS(cleanText);
      };

      const playPromise = audio.play();
      if (playPromise !== undefined) {
        playPromise.catch(() => {
          fallbackBrowserTTS(cleanText);
        });
      }
    } catch (e) {
      fallbackBrowserTTS(text);
    }
  };

  const fallbackBrowserTTS = (text: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setIsSpeaking(false);
      return;
    }
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.resume();
      window.speechSynthesis.speak(utterance);
    } catch (e) {
      setIsSpeaking(false);
    }
  };

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setVoiceError("Voice recognition not supported. Please use Google Chrome or Microsoft Edge.");
      return;
    }
    setVoiceError(null);
    stopSpeaking();

    if (isListening) {
      if (silenceTimeoutRef.current) clearTimeout(silenceTimeoutRef.current);
      recognitionRef.current.stop();
      setIsListening(false);
      const textToSend = accumulatedSpeechRef.current.trim();
      setLiveInterim("");
      accumulatedSpeechRef.current = "";
      if (textToSend) {
        handleSendMessage(textToSend);
      }
    } else {
      try {
        accumulatedSpeechRef.current = "";
        setLiveInterim("");
        recognitionRef.current.start();
      } catch (e: any) {
        console.error("Speech start error:", e);
      }
    }
  };

  const handleSendMessage = async (queryText: string) => {
    const text = queryText.trim();
    if (!text) return;

    setInputText("");
    setVoiceError(null);
    setLiveInterim("");
    stopSpeaking();

    setMessages((prev) => [...prev, { sender: "user", text }]);
    setIsProcessing(true);

    try {
      const res = await sendChatMessage(text);
      setMessages((prev) => [
        ...prev,
        { sender: "agent", text: res.reply, toolInvoked: res.tool_invoked },
      ]);
      // Speak the response using natural neural voice!
      playSpeech(res.reply);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "agent",
          text: "Sorry, main backend se connect nahi kar paya. Please verify that FastAPI is running on port 8001.",
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  };

  const quickPrompts = [
    "Next class kab hai?",
    "DBMS me kitne bunk safe hain?",
    "Meri overall attendance kaisi hai?",
    "Target 8.5 CGPA ke liye kitna SGPA chahiye?",
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4 animate-in fade-in">
      <div className="w-full max-w-xl h-[600px] rounded-2xl bg-surface border border-indigo-500/30 shadow-2xl flex flex-col justify-between overflow-hidden relative">
        {/* Header */}
        <div className="p-4 border-b border-borderSubtle bg-surfaceHover/50 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className={`h-8 w-8 rounded-lg bg-agentIndigo flex items-center justify-center shadow-lg transition-all ${isSpeaking ? "scale-110 shadow-cyan-500/50 ring-2 ring-cyan-400" : "shadow-indigo-500/20"}`}>
              <Bot className="h-4 w-4 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-white flex items-center gap-2">
                <span>CampusPilot AI Voice Agent</span>
                <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${isSpeaking ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40 animate-pulse" : isListening ? "bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse" : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"}`}>
                  {isSpeaking ? "Speaking (Neural Audio) 🔊" : isListening ? "Listening (Auto-stops on pause) 🎙️" : "Live"}
                </span>
              </h3>
              <p className="text-[11px] text-gray-400">Natural Hindi/Hinglish Neural Voice & Auto-Silence Detection</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Quick Speaker Audio Test Button */}
            <button
              onClick={() => playSpeech("Namaste Swatantra! CampusPilot audio system bilkul perfect chal raha hai. Aap batao main aapki kya madad kar sakta hoon?")}
              className="text-[11px] font-semibold text-voiceCyan hover:text-white px-2.5 py-1 rounded-lg bg-cyan-950/40 border border-cyan-500/30 flex items-center gap-1.5 transition-all hover:bg-cyan-900/50"
              title="Test speaker sound"
            >
              <Volume2 className="h-3 w-3" />
              <span>Test Audio 🔊</span>
            </button>

            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                className="text-[11px] text-rose-400 hover:text-white px-2 py-1 rounded-lg bg-rose-950/40 border border-rose-500/30 flex items-center gap-1"
                title="Stop audio playback"
              >
                <VolumeX className="h-3 w-3" />
                <span>Stop</span>
              </button>
            )}

            <button
              onClick={() => {
                stopSpeaking();
                onClose();
              }}
              className="text-gray-400 hover:text-white p-1 rounded-lg bg-surface border border-borderSubtle"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Warning / Error banner if any */}
        {voiceError && (
          <div className="px-4 py-2 bg-amber-500/15 border-b border-amber-500/30 flex items-center gap-2 text-amber-300 text-xs">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{voiceError}</span>
          </div>
        )}

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
                <p className="whitespace-pre-line">{m.text}</p>
              </div>

              {/* Speaker action */}
              {m.sender === "agent" && (
                <button
                  onClick={() => playSpeech(m.text)}
                  className="mt-1 text-[10px] text-gray-400 hover:text-voiceCyan flex items-center gap-1 ml-1 transition-colors"
                >
                  <Volume2 className="h-3 w-3" />
                  <span>Tap to Speak 🔊</span>
                </button>
              )}
            </div>
          ))}

          {/* Real-time live transcript banner while speaking */}
          {isListening && liveInterim && (
            <div className="p-2.5 rounded-xl bg-cyan-950/30 border border-cyan-500/30 text-xs text-cyan-200 flex items-center gap-2 animate-pulse">
              <Radio className="h-3.5 w-3.5 text-cyan-400 animate-spin flex-shrink-0" />
              <span>Hearing: &quot;{liveInterim}&quot;</span>
            </div>
          )}

          {isProcessing && (
            <div className="flex items-center gap-2 text-xs text-indigo-300 animate-pulse pl-2">
              <Sparkles className="h-3.5 w-3.5 animate-spin" />
              <span>CampusPilot is reasoning & generating exact academic math...</span>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {/* Quick Suggestion Chips */}
        <div className="px-4 py-1.5 border-t border-borderSubtle/50 flex items-center gap-1.5 overflow-x-auto text-[11px] no-scrollbar">
          <span className="text-gray-500 flex-shrink-0 text-[10px] uppercase font-bold">Try:</span>
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(p)}
              disabled={isProcessing}
              className="flex-shrink-0 px-2.5 py-1 rounded-full bg-surfaceHover hover:bg-indigo-950/50 border border-borderSubtle hover:border-indigo-500/40 text-gray-300 hover:text-white transition-all disabled:opacity-50"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Voice Trigger & Input Footer */}
        <div className="p-4 border-t border-borderSubtle bg-surfaceHover/30 space-y-3">
          {/* Quick Voice Bar */}
          <div className="flex flex-col items-center justify-center gap-1">
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
                  <span>Listening... (Will auto-send when you pause)</span>
                </>
              ) : (
                <>
                  <Mic className="h-4 w-4 text-gray-950" />
                  <span>Tap to Speak (Auto-stops when you pause)</span>
                </>
              )}
            </button>
            <span className="text-[10px] text-gray-500">
              {isListening ? "Pause speaking for 1.3s to automatically submit" : "Bolne ke baad rukein, yeh khud-b-khud submit ho jayega"}
            </span>
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
              placeholder="Or type a question (e.g. 'Next class kab hai?')"
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
