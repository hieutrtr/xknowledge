"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input" 
import { ScrollArea } from "@/components/ui/scroll-area"
import { Image, Mic, Send } from "lucide-react"

export function ChatInterface() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! How can I assist you today?" },
  ])
  const [inputMessage, setInputMessage] = useState("")

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setMessages([...messages, { role: "user", content: inputMessage }])
      setInputMessage("")
    }
  }

  return (
    <div className="flex flex-col bg-gray-900 p-4">
      <h2 className="mb-4 text-xl font-semibold text-white">Chatbot</h2>
      <ScrollArea className="flex-1 rounded-lg border border-gray-700 bg-gray-800 p-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`mb-4 ${
              message.role === "user" ? "text-right" : "text-left"
            }`}
          >
            <span
              className={`inline-block rounded-lg px-4 py-2 ${
                message.role === "user"
                  ? "bg-blue-600 text-white" 
                  : "bg-gray-700 text-gray-300"
              }`}
            >
              {message.content}
            </span>
          </div>
        ))}  
      </ScrollArea>
      <div className="mt-4 flex items-center space-x-2">
        <Button variant="outline" size="icon" className="bg-gray-800 text-gray-300 hover:bg-gray-700">
          <Image className="h-4 w-4" />
          <span className="sr-only">Upload image</span>
        </Button>
        <Button variant="outline" size="icon" className="bg-gray-800 text-gray-300 hover:bg-gray-700">
          <Mic className="h-4 w-4" />
          <span className="sr-only">Voice chat</span>
        </Button>
        <Input 
          type="text"
          placeholder="Type your message..." 
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter") handleSendMessage()
          }}
          className="bg-gray-800 text-white border-gray-700"
        />
        <Button onClick={handleSendMessage} className="bg-blue-600 text-white hover:bg-blue-700">
          <Send className="mr-2 h-4 w-4" />
          Send
        </Button>
      </div>
    </div>  
  )
}