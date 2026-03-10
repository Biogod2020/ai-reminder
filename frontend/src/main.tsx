import { StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import { LayoutDashboard, BrainCircuit, PanelRightOpen, PanelRightClose, Send, Clock, ChevronLeft, ChevronRight, Sparkles, CheckCircle2, Loader2, XCircle } from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { motion, AnimatePresence } from 'framer-motion'
import './index.css'

// --- Utils ---
function cn(...inputs: ClassValue[]) { return twMerge(clsx(inputs)) }

// --- Types ---
interface SubTask { title: string; duration_minutes: number; estimated_cognitive_load: number; slack_minutes: number; }
interface Message { role: 'user' | 'assistant'; content: string; intent?: string; actions?: SubTask[]; }
interface Task { id: number; time: string; title: string; load: number; duration: number; slack: number; isDraft?: boolean; }
interface ViewData { calendar: Task[]; }

// --- Markdown-lite Formatter ---
function FormattedText({ text }: { text: string }) {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return (
    <span className="whitespace-pre-wrap">
      {parts.map((part, i) => 
        part.startsWith('**') && part.endsWith('**') 
          ? <strong key={i} className="font-black text-[#2383e2]">{part.slice(2, -2)}</strong> 
          : part
      )}
    </span>
  );
}

// --- Main App Component ---
function App() {
  const [activeTab, setActiveTab] = useState('Overview')
  const [isConsoleOpen, setIsConsoleOpen] = useState(true)
  const [viewData, setViewData] = useState<ViewData | null>(null)
  const [draftTasks, setDraftTasks] = useState<Task[]>([])
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Soul initialized. I am reasoning about your cognitive peaks. How can I align your goals today?" }
  ])
  const [input, setInput] = useState('')
  const [isThinking, setIsThinking] = useState(false)

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const hours = Array.from({ length: 11 }, (_, i) => 9 + i)

  const refreshData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/get_view_data')
      const data = await response.json()
      setViewData(data)
    } catch (e) { console.error(e) }
  }

  useEffect(() => { refreshData() }, [])

  const handleSend = async (overrideInput?: string) => {
    const text = overrideInput || input
    if (!text.trim()) return
    
    const userMsg: Message = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setIsThinking(true)

    try {
      const r = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, history: messages.slice(-5).map(m => ({role: m.role, content: m.content})) })
      })
      const data = await r.json()
      
      const newMsg: Message = { 
        role: 'assistant', 
        content: data.response, 
        intent: data.intent,
        actions: data.proposed_actions 
      }
      setMessages(prev => [...prev, newMsg])

      if (data.proposed_actions) {
        const drafts: Task[] = data.proposed_actions.map((st: SubTask, i: number) => ({
          id: 9000 + i,
          time: `${9 + (i % 10)}:00`, 
          title: st.title,
          load: st.estimated_cognitive_load,
          duration: st.duration_minutes,
          slack: st.slack_minutes,
          isDraft: true
        }))
        setDraftTasks(drafts)
      }
    } catch (e) { 
      setMessages(prev => [...prev, { role: 'assistant', content: "Cognitive bridge interrupted. Please check backend status." }])
    } finally {
      setIsThinking(false)
    }
  }

  const commitDraft = async () => {
    setDraftTasks([])
    await refreshData()
    setMessages(prev => [...prev, { role: 'assistant', content: "Plan committed to your Digital Soul. Your schedule is now scientifically aligned." }])
  }

  return (
    <div className="flex h-screen w-full bg-white text-[#37352f] overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-[#e9e9e7] bg-[#f7f6f3] p-4 flex flex-col gap-6 z-20">
        <div className="px-2 py-4 flex items-center gap-3">
          <div className="w-8 h-8 bg-[#2383e2] rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
            <Sparkles className="text-white w-4 h-4" />
          </div>
          <span className="font-bold text-xs uppercase tracking-widest">Soul Center</span>
        </div>
        <nav className="flex-1 space-y-1">
          {['Overview', 'Cognitive'].map((label) => (
            <button key={label} onClick={() => setActiveTab(label)}
              className={cn("w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all",
                activeTab === label ? "bg-white shadow-sm text-[#2383e2]" : "text-[#787774] hover:bg-[#ebebe9]")}
            >
              {label === 'Overview' ? <LayoutDashboard size={16}/> : <BrainCircuit size={16}/>}
              {label}
            </button>
          ))}
        </nav>
      </aside>

      <div className="flex-1 flex overflow-hidden relative">
        {/* Main Grid Area */}
        <main className="flex-1 flex flex-col overflow-hidden relative bg-white">
          <header className="h-14 border-b border-[#e9e9e7] flex items-center justify-between px-6 bg-white/80 backdrop-blur z-10">
            <div className="flex items-center gap-3">
              <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9b9b9b]">Weekly Intelligence Flow</h2>
              {draftTasks.length > 0 && (
                <div id="draft-indicator" className="flex items-center gap-2 px-2 py-0.5 bg-amber-100 text-amber-700 rounded text-[9px] font-black animate-pulse">
                  DRAFT PREVIEW ACTIVE
                </div>
              )}
            </div>
            <div className="flex items-center gap-4 text-[10px] font-bold text-[#787774] uppercase">
              <ChevronLeft size={12}/> Prev <span className="text-[#37352f]">MAR 2026</span> Next <ChevronRight size={12}/>
            </div>
          </header>

          <div className="flex-1 overflow-auto">
            <div className="grid grid-cols-[60px_repeat(7,1fr)] min-w-[900px]">
              <div className="border-r border-[#e9e9e7] bg-[#f7f6f3]/30">
                {hours.map(h => <div key={h} className="h-24 border-b border-[#e9e9e7]/50 text-[10px] text-[#9b9b9b] p-2 text-right">{h}:00</div>)}
              </div>
              {days.map((day, dIdx) => (
                <div key={day} className="border-r border-[#e9e9e7] last:border-r-0">
                  <div className="h-10 border-b border-[#e9e9e7] flex items-center justify-center text-[10px] font-bold uppercase tracking-widest text-[#9b9b9b] bg-[#f7f6f3]">{day}</div>
                  {hours.map(h => {
                    const allVisibleTasks = [...(viewData?.calendar || []), ...draftTasks]
                    const task = allVisibleTasks.find(t => t.time.startsWith(h.toString()) && (t.id % 7 === dIdx));
                    return (
                      <div key={h} className="h-24 border-b border-[#e9e9e7]/30 p-1 group">
                        {task && (
                          <motion.div initial={task.isDraft ? { opacity: 0, scale: 0.95 } : {}} animate={{ opacity: 1, scale: 1 }}
                            className={cn("h-full w-full rounded-md p-2 text-[10px] border shadow-sm transition-all",
                            task.isDraft ? "border-dashed border-blue-400 bg-blue-50/30 opacity-70" : (task.load > 0.7 ? "bg-orange-50 border-orange-100" : "bg-blue-50 border-blue-100"))}>
                            <div className="font-bold truncate" data-testid={task.isDraft ? "draft-task" : "task"}>
                              {task.isDraft && "[DRAFT] "}{task.title}
                            </div>
                            <div className="mt-1 flex items-center gap-1 opacity-60"><Clock size={8}/> {task.duration}m</div>
                          </motion.div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </main>

        {/* Sidebar Console */}
        <AnimatePresence>
          {isConsoleOpen && (
            <motion.aside initial={{ x: 400 }} animate={{ x: 0 }} exit={{ x: 400 }}
              className="w-[420px] border-l border-[#e9e9e7] bg-[#f7f6f3]/95 backdrop-blur-3xl flex flex-col z-30 shadow-2xl"
            >
              <div className="p-4 border-b border-[#e9e9e7] font-black text-[10px] uppercase tracking-[0.2em] text-[#787774] flex items-center justify-between">
                <div className="flex items-center gap-2"><Sparkles size={12} className="text-[#2383e2]"/> Soul Console</div>
                <div className="text-[8px] bg-green-500/10 text-green-600 px-1.5 py-0.5 rounded border border-green-200 uppercase font-black">Reasoning Active</div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-hide">
                {messages.map((m, i) => (
                  <div key={i} className={cn("flex flex-col gap-2", m.role === 'user' ? "items-end" : "items-start")}>
                    <div className={cn("px-4 py-2.5 rounded-2xl text-sm max-w-[95%] shadow-sm leading-relaxed", 
                      m.role === 'user' ? "bg-[#2383e2] text-white rounded-tr-none" : "bg-white border border-[#e9e9e7] text-[#37352f] rounded-tl-none")}>
                      <FormattedText text={m.content} />
                    </div>
                    
                    {/* Alignment Cards */}
                    {m.actions && draftTasks.length > 0 && (
                      <div id="alignment-panel" className="w-full flex flex-col gap-3 mt-4 bg-white/50 p-4 rounded-2xl border border-blue-100 shadow-inner">
                        <div className="text-[10px] font-black text-blue-600 uppercase tracking-widest">Proposed Scientific Alignment</div>
                        <div className="flex flex-col gap-2">
                          {m.actions.slice(0,4).map((task, tIdx) => (
                            <div key={tIdx} className="flex items-center gap-2 text-[11px] font-bold text-[#37352f] opacity-80 bg-white/80 p-2 rounded-lg border border-[#e9e9e7]">
                              <CheckCircle2 size={12} className="text-blue-500 shrink-0" /> 
                              <span className="truncate">{task.title}</span>
                            </div>
                          ))}
                          {m.actions.length > 4 && <div className="text-[9px] opacity-50 font-black px-2">+ {m.actions.length - 4} ADDITIONAL STEPS IN PREVIEW</div>}
                        </div>
                        <div className="flex gap-2 mt-2">
                          <button onClick={commitDraft} id="confirm-commit-btn" className="flex-1 py-2.5 bg-[#2383e2] text-white text-[10px] font-black rounded-xl shadow-lg shadow-blue-100 hover:scale-[1.02] transition-all flex items-center justify-center gap-2 uppercase tracking-widest">
                            Confirm & Commit Plan
                          </button>
                          <button onClick={() => setDraftTasks([])} className="p-2 border border-[#e9e9e7] rounded-xl hover:bg-red-50 hover:text-red-500 transition-colors bg-white">
                            <XCircle size={18} />
                          </button>
                        </div>
                      </div>
                    )}

                    {m.intent && <span className="text-[9px] uppercase font-black text-[#9b9b9b] tracking-[0.2em] px-1 opacity-50">Logic: {m.intent}</span>}
                  </div>
                ))}
                {isThinking && (
                  <div id="thinking-indicator" className="flex items-center gap-3 text-[#2383e2] animate-pulse px-1">
                    <Loader2 size={16} className="animate-spin" />
                    <span className="text-[10px] font-black uppercase tracking-widest">Deep Soul Reasoning...</span>
                  </div>
                )}
              </div>

              <div className="p-4 border-t border-[#e9e9e7] bg-white/50 backdrop-blur">
                <div className="relative">
                  <input type="text" value={input} onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSend()}
                    placeholder="Talk to your digital soul..."
                    className="w-full bg-white border border-[#e9e9e7] rounded-2xl pl-4 pr-12 py-3 text-sm focus:outline-none focus:ring-4 focus:ring-blue-50 transition-all shadow-sm"
                  />
                  <button onClick={() => handleSend()} className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 bg-[#2383e2] text-white rounded-lg hover:scale-105 transition-all shadow-md shadow-blue-100">
                    <Send size={14}/>
                  </button>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        <button onClick={() => setIsConsoleOpen(!isConsoleOpen)}
          className="absolute right-4 top-4 p-2 bg-white border border-[#e9e9e7] rounded-full shadow-xl z-40 hover:scale-110 transition-all"
        >
          {isConsoleOpen ? <PanelRightClose size={16}/> : <PanelRightOpen size={16}/>}
        </button>
      </div>
    </div>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
