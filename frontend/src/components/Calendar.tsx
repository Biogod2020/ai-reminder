import { useEffect, useState } from 'react';
import { Task, ViewData } from '../types/api';
import { cn } from '../lib/utils';
import { Clock, Coffee } from 'lucide-react';

export function Calendar() {
  const [viewData, setViewData] = useState<ViewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/get_view_data');
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

  if (loading) return <div className="p-8 text-muted-foreground">Loading schedule...</div>;
  if (!viewData) return <div className="p-8 text-destructive">Failed to load data.</div>;

  return (
    <div className="flex flex-col gap-4 p-6">
      <h2 className="text-xl font-bold tracking-tight mb-4">Interleaved Schedule</h2>
      <div className="relative border-l-2 border-border ml-4 pl-8 space-y-8">
        {viewData.calendar.map((task) => (
          <div key={task.id} className="relative">
            <div className="absolute -left-[41px] top-1 bg-background p-1 border-2 border-border rounded-full">
              <Clock className="w-4 h-4 text-primary" />
            </div>
            <div className="flex flex-col gap-2">
              <div className={cn(
                "p-4 rounded-xl border bg-card shadow-sm transition-all hover:shadow-md",
                task.load > 0.7 ? "border-orange-200 bg-orange-50/30" : "border-blue-200 bg-blue-50/30"
              )}>
                <div className="flex justify-between items-start mb-1">
                  <span className="text-sm font-medium text-muted-foreground">{task.time}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-background border border-border">
                    Load: {(task.load * 100).toFixed(0)}%
                  </span>
                </div>
                <h3 className="font-semibold text-lg">{task.title}</h3>
                <p className="text-sm text-muted-foreground mt-1">{task.duration} mins duration</p>
              </div>
              
              {/* Slack Visualization */}
              <div className="flex items-center gap-3 ml-4 py-2 px-4 rounded-lg bg-green-50/20 border border-green-100/50">
                <Coffee className="w-4 h-4 text-green-600/70" />
                <span className="text-xs font-medium text-green-700/70">
                  Scientific Slack: {task.slack} mins redundancy
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
