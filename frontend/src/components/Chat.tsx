import { useState } from 'react';
import { Send, BrainCircuit, Sparkles } from 'lucide-react';
import { cn } from '../lib/utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  intent?: string;
  actions?: any[];
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
      const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
      const response = await fetch(`${apiBase}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input, history: messages }),
      });
      
      const data = await response.json();
      const assistantMsg: Message = {
        role: 'assistant',
        content: data.response,
        intent: data.intent,
        actions: data.proposed_actions,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error('Chat failed:', error);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto p-6">
      <h2 className="text-xl font-bold tracking-tight mb-6 flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-primary" />
        Universal Soul Console
      </h2>

      <div className="flex-1 overflow-y-auto space-y-6 mb-6 pr-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={cn(
            "flex flex-col gap-2",
            msg.role === 'user' ? "items-end" : "items-start"
          )}>
            <div className={cn(
              "px-4 py-2 rounded-2xl max-w-[85%] text-sm",
              msg.role === 'user' 
                ? "bg-primary text-white rounded-tr-none"
                : "bg-muted border border-border text-foreground rounded-tl-none"
            )}>
              {msg.content}
            </div>
            {msg.intent && (
              <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-widest ml-1">
                Intent: {msg.intent}
              </span>
            )}
          </div>
        ))}

        {isThinking && (
          <div className="flex items-center gap-3 text-primary animate-pulse">
            <BrainCircuit className="w-5 h-5" />
            <span className="text-sm font-medium">Soul is reasoning...</span>
          </div>
        )}
      </div>

      <div className="relative group">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask your digital soul..."
          className="w-full bg-muted/50 border border-border rounded-2xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all"
        />
        <button
          onClick={handleSend}
          className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-muted-foreground hover:text-primary transition-colors"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
