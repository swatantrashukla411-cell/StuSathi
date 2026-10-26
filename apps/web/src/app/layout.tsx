import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CampusPilot AI — Voice-First Personal Academic Agent",
  description: "Next-generation academic co-pilot with timetable intelligence, attendance danger radar, and real-time voice orchestration.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-gray-100 min-h-screen antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
