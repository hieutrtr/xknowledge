"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

const useToggle = (initialState = false) => {
  const [state, setState] = useState(initialState)
  const toggle = () => setState((prev) => !prev)
  return [state, toggle] as const
}

export function SideBar() {
  const [isSidebarExpanded, toggleSidebar] = useToggle(false)

  return (
    <div
      className={`bg-gray-800 transition-all duration-300 ${
        isSidebarExpanded ? "w-64" : "w-16"
      }`}
    >
      <Button
        variant="ghost"
        size="icon"
        className="m-2 text-gray-300 hover:bg-gray-700"
        onClick={() => toggleSidebar()}
      >
        {isSidebarExpanded ? (
          <ChevronLeft className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
      </Button>
      {isSidebarExpanded && (
        <div className="p-4 text-gray-300">
          <h2 className="mb-2 text-lg font-semibold">Sidebar Content</h2>
          <p>Your sidebar items go here.</p>
        </div>
      )}
    </div>
  )
}
