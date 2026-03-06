import { useState } from 'react'
import { Calendar } from './components/Calendar'
import { Chat } from './components/Chat'
import { CognitiveMetrics } from './components/CognitiveMetrics'
import { LayoutDashboard, Calendar as CalendarIcon, Kanban, BrainCircuit, Settings, MessageSquare } from 'lucide-react'
import { cn } from './lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

function App() {
  const [activeTab, setActiveTab] = useState('Schedule')

  const sidebarItems = [
    { icon: LayoutDashboard, label: 'Overview' },
    { icon: CalendarIcon, label: 'Schedule' },
    { icon: Kanban, label: 'Kanban' },
    { icon: BrainCircuit, label: 'Cognitive' },
    { icon: MessageSquare, label: 'Console' },
  ]

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-muted/20 p-4 flex flex-col gap-6 z-10">
        <div className="px-2 py-4">
          <motion.h1 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-lg font-bold tracking-tight flex items-center gap-2 text-primary"
          >
            <span className="w-6 h-6 bg-primary rounded-lg shadow-lg shadow-primary/20"></span>
            Notion Soul
          </motion.h1>
        </div>
        
        <nav className="flex-1 space-y-1">
          {sidebarItems.map((item, idx) => (
            <motion.button
              key={item.label}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => setActiveTab(item.label)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                activeTab === item.label 
                  ? "bg-primary/10 text-primary shadow-sm" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className={cn("w-4 h-4", activeTab === item.label ? "text-primary" : "")} />
              {item.label}
            </motion.button>
          ))}
        </nav>

        <div className="mt-auto">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden relative">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="absolute inset-0 overflow-y-auto"
          >
            {activeTab === 'Schedule' && <Calendar />}
            {activeTab === 'Console' && <Chat />}
            {activeTab === 'Cognitive' && <CognitiveMetrics />}
            {['Overview', 'Kanban'].includes(activeTab) && (
              <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                <BrainCircuit className="w-12 h-12 mb-4 opacity-20" />
                <p className="text-sm font-medium italic">Expert intelligence evolving...</p>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  )
}

export default App
