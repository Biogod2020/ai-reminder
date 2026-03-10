import { useState } from 'react';
import { Send, BrainCircuit, Sparkles } from 'lucide-react';
import { cn } from '../lib/utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setIsThinking(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, history: messages }),
      });
      const data = await response.json();
      setMessages((prev) => [...prev, { role: 'assistant', content: data.response, intent: data.intent }]);
    } catch (e) { console.error(e); } finally { setIsThinking(false); }
  };

  return (
    <div className="flex flex-col h-full bg-[#f7f6f3]/95 backdrop-blur-2xl">
      <div className="p-4 border-b border-[#e9e9e7] flex items-center gap-2">
        <Sparkles size={14} className="text-[#2383e2]" />
        <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-[#787774]">Soul Console</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={cn("flex flex-col gap-1", msg.role === 'user' ? "items-end" : "items-start")}>
            <div className={cn(
              "px-3 py-2 rounded-xl text-sm max-w-[90%] shadow-sm transition-all",
              msg.role === 'user' ? "bg-[#2383e2] text-white" : "bg-white border border-[#e9e9e7] text-[#37352f]"
            )}>
              {msg.content}
            </div>
            {msg.intent && <span className="text-[8px] font-bold uppercase tracking-widest text-[#9b9b9b] px-1">Intent: {msg.intent}</span>}
          </div>
        ))}
        {isThinking && (
          <div className="flex items-center gap-2 text-[#2383e2] animate-pulse px-1">
            <BrainCircuit size={14} />
            <span className="text-[10px] font-bold uppercase tracking-tighter">Reasoning...</span>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-[#e9e9e7] bg-white/50">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Talk to your soul..."
            className="w-full bg-white border border-[#e9e9e7] rounded-xl pl-4 pr-10 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 transition-all placeholder:text-[#9b9b9b]"
          />
          <button onClick={handleSend} className="absolute right-3 top-1/2 -translate-y-1/2 text-[#787774] hover:text-[#2383e2] transition-colors">
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
