import { useState } from 'react'
import { WeeklySchedule } from './components/WeeklySchedule'
import { Chat } from './components/Chat'
import { LayoutDashboard, Calendar as CalendarIcon, BrainCircuit, Settings, PanelRightOpen, PanelRightClose } from 'lucide-react'
import { cn } from './lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

function App() {
  const [isConsoleOpen, setIsConsoleOpen] = useState(true)

  return (
    <div className="flex h-screen w-full bg-[#ffffff] text-[#37352f] overflow-hidden font-sans">
      {/* --- Sidebar --- */}
      <aside className="w-20 lg:w-64 border-r border-[#e9e9e7] bg-[#f7f6f3] p-4 flex flex-col gap-6 z-20">
        <div className="px-2 py-4 flex items-center gap-3">
          <div className="w-8 h-8 bg-[#2383e2] rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
            <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
          </div>
          <span className="hidden lg:block font-black text-[10px] uppercase tracking-[0.3em] text-[#37352f]">Soul Center</span>
        </div>
        
        <nav className="flex-1 space-y-2">
          {[{ icon: LayoutDashboard, label: 'Overview' }, { icon: CalendarIcon, label: 'History' }, { icon: BrainCircuit, label: 'Cognitive' }].map((item) => (
            <button
              key={item.label}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all",
                item.label === 'Overview' ? "bg-white shadow-sm text-[#2383e2]" : "text-[#787774] hover:bg-[#ebebe9]"
              )}
            >
              <item.icon className="w-5 h-5 shrink-0" />
              <span className="hidden lg:block">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="mt-auto pt-4 border-t border-[#e9e9e7]/50">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-[#787774] hover:bg-[#ebebe9]">
            <Settings className="w-5 h-5 shrink-0" />
            <span className="hidden lg:block">Settings</span>
          </button>
        </div>
      </aside>

      {/* --- Main Content Area --- */}
      <div className="flex-1 flex overflow-hidden relative bg-white">
        <main className="flex-1 overflow-hidden">
          <WeeklySchedule />
        </main>

        {/* --- Sidebar Console --- */}
        <AnimatePresence>
          {isConsoleOpen && (
            <motion.aside
              initial={{ x: 400, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 400, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="w-[380px] border-l border-[#e9e9e7] z-10"
            >
              <Chat />
            </motion.aside>
          )}
        </AnimatePresence>

        {/* --- Toggle Console Button --- */}
        <button 
          onClick={() => setIsConsoleOpen(!isConsoleOpen)}
          className="absolute right-4 top-4 p-2 bg-white/80 backdrop-blur border border-[#e9e9e7] rounded-full shadow-lg hover:bg-[#f7f6f3] transition-colors z-30"
        >
          {isConsoleOpen ? <PanelRightClose size={16} /> : <PanelRightOpen size={16} />}
        </button>
      </div>
    </div>
  )
}

export default App
