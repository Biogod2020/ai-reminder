import { Calendar } from './components/Calendar'
import { LayoutDashboard, Calendar as CalendarIcon, Kanban, BrainCircuit, Settings, MessageSquare } from 'lucide-react'
import { cn } from './lib/utils'

function App() {
  const sidebarItems = [
    { icon: LayoutDashboard, label: 'Overview', active: false },
    { icon: CalendarIcon, label: 'Schedule', active: true },
    { icon: Kanban, label: 'Kanban', active: false },
    { icon: BrainCircuit, label: 'Cognitive', active: false },
    { icon: MessageSquare, label: 'Console', active: false },
  ]

  return (
    <div className="flex h-screen w-full bg-background/80 text-foreground overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border bg-muted/30 p-4 flex flex-col gap-6">
        <div className="px-2 py-4">
          <h1 className="text-lg font-bold tracking-tight flex items-center gap-2">
            <span className="w-6 h-6 bg-primary rounded-lg"></span>
            Notion Soul
          </h1>
        </div>
        
        <nav className="flex-1 space-y-1">
          {sidebarItems.map((item) => (
            <button
              key={item.label}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                item.active 
                  ? "bg-primary/10 text-primary" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="mt-auto">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground">
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-background/50">
        <Calendar />
      </main>
    </div>
  )
}

export default App
