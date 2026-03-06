import { useState } from 'react'
import { Calendar } from './components/Calendar'
import { Chat } from './components/Chat'
import { LayoutDashboard, Calendar as CalendarIcon, Kanban, BrainCircuit, Settings, MessageSquare } from 'lucide-react'
import { cn } from './lib/utils'

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
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-muted/20 p-4 flex flex-col gap-6">
        <div className="px-2 py-4">
          <h1 className="text-lg font-bold tracking-tight flex items-center gap-2 text-primary">
            <span className="w-6 h-6 bg-primary rounded-lg shadow-lg shadow-primary/20"></span>
            Notion Soul
          </h1>
        </div>
        
        <nav className="flex-1 space-y-1">
          {sidebarItems.map((item) => (
            <button
              key={item.label}
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
            </button>
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
        <div className="absolute inset-0 overflow-y-auto">
          {activeTab === 'Schedule' && <Calendar />}
          {activeTab === 'Console' && <Chat />}
          {['Overview', 'Kanban', 'Cognitive'].includes(activeTab) && (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
              <BrainCircuit className="w-12 h-12 mb-4 opacity-20" />
              <p className="text-sm font-medium">Coming soon in Phase 2/3...</p>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
