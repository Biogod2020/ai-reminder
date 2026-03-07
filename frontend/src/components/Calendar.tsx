import { useEffect, useState } from 'react';
import type { ViewData } from '../types/api';
import { cn } from '../lib/utils';
import { Clock, Coffee } from 'lucide-react';

export function Calendar() {
  const [viewData, setViewData] = useState<ViewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiBase = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
        const response = await fetch(`${apiBase}/get_view_data`);
        const data = await response.json();
        setViewData(data);
      } catch (error) {
        console.error('Failed to fetch view data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="p-8 text-muted-foreground text-center">Loading schedule...</div>;
  if (!viewData) return <div className="p-8 text-destructive text-center">Failed to load data.</div>;

  return (
    <div className="flex flex-col gap-4 p-6 max-w-4xl mx-auto">
      <h2 className="text-xl font-bold tracking-tight mb-8">Interleaved Schedule</h2>
      <div className="relative border-l border-border ml-4 pl-10 space-y-12">
        {viewData.calendar.map((task) => (
          <div key={task.id} className="relative group">
            <div className="absolute -left-[51px] top-1 bg-background p-1.5 border border-border rounded-full shadow-sm group-hover:border-primary/50 transition-colors">
              <Clock className="w-4 h-4 text-primary" />
            </div>
            <div className="flex flex-col gap-3">
              <div className={cn(
                "p-5 rounded-2xl border bg-card/50 shadow-sm transition-all hover:shadow-md hover:scale-[1.01]",
                task.load > 0.7 ? "border-orange-100 bg-orange-50/10" : "border-blue-100 bg-blue-50/10"
              )}>
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{task.time}</span>
                  <span className={cn(
                    "text-[10px] px-2 py-0.5 rounded-md font-bold border",
                    task.load > 0.7 ? "bg-orange-100/50 border-orange-200 text-orange-700" : "bg-blue-100/50 border-blue-200 text-blue-700"
                  )}>
                    LOAD: {(task.load * 100).toFixed(0)}%
                  </span>
                </div>
                <h3 className="font-bold text-lg tracking-tight">{task.title}</h3>
                <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1.5">
                  <Clock className="w-3 h-3" />
                  {task.duration} mins focus duration
                </p>
              </div>
              
              {/* Slack Visualization */}
              <div className="flex items-center gap-3 ml-4 py-2.5 px-5 rounded-xl bg-muted/30 border border-border/50 group-hover:border-green-200/50 transition-colors">
                <Coffee className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-[11px] font-medium text-muted-foreground">
                  BUFFER: <span className="text-foreground font-bold">{task.slack} mins</span> scientific redundancy
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
