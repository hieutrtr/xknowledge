"use client"

import { SideBar } from "@/components/SideBar"
import { Result } from "@/components/Result"
import { ChatInterface } from "@/components/ChatInterface"

export default function App() {
  return (
    <div className="grid h-screen grid-cols-[auto_1fr_1fr] bg-black text-white">
      <SideBar />
      <Result />
      <ChatInterface />
    </div>
  )
}