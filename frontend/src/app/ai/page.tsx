'use client';
import React, { useState } from 'react';
import { Bot, Send, Sparkles, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export default function AIPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! I am your AI macro research assistant. Ask me about market conditions, economic indicators, regime analysis, or any macro-economic topic. I can provide data-driven analysis and insights.', timestamp: new Date() },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [useRag, setUseRag] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg: Message = { role: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await api.aiChat(input, useRag);
      const assistantMsg: Message = {
        role: 'assistant',
        content: response?.response || 'Sorry, I could not generate a response.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'AI service is currently unavailable. Please ensure Ollama is running.',
        timestamp: new Date(),
      }]);
    }
    setIsLoading(false);
  };

  const quickPrompts = [
    'Analyze the current macro environment',
    'What is the yield curve signaling?',
    'Compare US vs EU monetary policy',
    'Assess recession probability',
  ];

  return (
    <div className="space-y-6 animate-fade-in h-full flex flex-col">
      <div className="flex items-center gap-3">
        <Bot className="w-6 h-6 text-accent-purple" />
        <h1 className="text-2xl font-bold gradient-text">AI Research Assistant</h1>
      </div>

      {/* Quick prompts */}
      <div className="flex flex-wrap gap-2">
        {quickPrompts.map(p => (
          <button
            key={p}
            onClick={() => setInput(p)}
            className="px-3 py-1.5 bg-dark-800/50 border border-dark-600/30 rounded-lg text-xs text-dark-300 hover:border-accent-purple/30 hover:text-accent-purple transition-all"
          >
            <Sparkles className="w-3 h-3 inline mr-1" />
            {p}
          </button>
        ))}
      </div>

      {/* Chat area */}
      <div className="glass-card flex-1 flex flex-col min-h-[400px]">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] p-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-accent-cyan/10 border border-accent-cyan/20 text-dark-100'
                  : 'bg-dark-800/50 border border-dark-600/20 text-dark-200'
              }`}>
                {msg.role === 'assistant' && <Bot className="w-4 h-4 text-accent-purple mb-2" />}
                <div className="whitespace-pre-wrap">{msg.content}</div>
                <p className="text-[10px] text-dark-400 mt-2">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-dark-800/50 border border-dark-600/20 rounded-2xl p-4">
                <Loader2 className="w-4 h-4 text-accent-purple animate-spin" />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="p-4 border-t border-dark-600/30">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <input
                id="ai-chat-input"
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="Ask about macro conditions, indicators, analysis..."
                className="w-full px-4 py-3 bg-dark-800/50 border border-dark-600/30 rounded-xl text-sm text-dark-100 placeholder-dark-400 focus:outline-none focus:border-accent-purple/50 transition-all"
              />
            </div>
            <button
              onClick={() => setUseRag(!useRag)}
              className={`px-3 rounded-xl text-xs font-medium transition-all ${useRag ? 'bg-accent-purple/20 text-accent-purple border border-accent-purple/30' : 'bg-dark-800/50 text-dark-400 border border-dark-600/30'}`}
            >
              RAG
            </button>
            <button
              onClick={sendMessage}
              disabled={isLoading || !input.trim()}
              className="px-4 py-3 bg-gradient-to-r from-accent-cyan to-accent-purple rounded-xl text-white font-medium text-sm hover:opacity-90 transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
