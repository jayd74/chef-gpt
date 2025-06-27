import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ChatbotWidget from "@/components/ChatbotWidget";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ChefGPT",
  description:
    "ChefGPT is a tool that helps you find recipes and ingredients for your meals.",
  icons: {
    icon: "/chefgpt.png",
    shortcut: "/chefgpt.png",
    apple: "/chefgpt.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <ChatbotWidget />
      </body>
    </html>
  );
}
