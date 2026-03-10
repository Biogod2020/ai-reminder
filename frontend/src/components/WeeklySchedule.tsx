import { useState, useEffect } from 'react';
import type { ViewData, Task } from '../types/api';
import { cn } from '../lib/utils';
import { Clock, ChevronLeft, ChevronRight } from 'lucide-react';

export function WeeklySchedule() {
  const [viewData, setViewData] = useState<ViewData | null>(null);
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const hours = Array.from({ length: 11 }, (_, i) => 9 + i); 

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000';
        const response = await fetch(`${apiBase}/get_view_data`);
        const data = await response.json();
        setViewData(data);
      } catch (e) { console.error(e); }
    };
    fetchData();
  }, []);

  const getTaskAt = (dayIndex: number, hour: number): Task | undefined => {
    if (!viewData) return undefined;
    return viewData.calendar.find(t => t.time.startsWith(hour.toString()) && (t.id % 7 === dayIndex));
  };

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="flex items-center justify-between px-6 py-3 border-b border-[#e9e9e7] bg-white/80 backdrop-blur sticky top-0 z-10">
        <h2 className="text-[10px] font-black uppercase tracking-[0.2em] text-[#9b9b9b]">Weekly Intelligence Flow</h2>
        <div className="flex items-center gap-4 text-[10px] font-bold text-[#787774] uppercase">
          <ChevronLeft className="w-3 h-3"/> Prev <span className="text-[#37352f]">MAR 2026</span> Next <ChevronRight className="w-3 h-3"/>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-[60px_repeat(7,1fr)] min-w-[900px]">
          <div className="border-r border-[#e9e9e7] bg-[#f7f6f3]/30">
            {hours.map(h => <div key={h} className="h-24 border-b border-[#e9e9e7]/50 text-[10px] text-[#9b9b9b] p-2 text-right">{h}:00</div>)}
          </div>
          {days.map((day, dIdx) => (
            <div key={day} className="border-r border-[#e9e9e7] last:border-r-0">
              <div className="h-10 border-b border-[#e9e9e7] flex items-center justify-center text-[10px] font-black uppercase tracking-[0.2em] text-[#9b9b9b] bg-[#f7f6f3]">{day}</div>
              {hours.map(h => {
                const task = getTaskAt(dIdx, h);
                return (
                  <div key={h} className="h-24 border-b border-[#e9e9e7]/30 p-1 group">
                    {task && (
                      <div className={cn(
                        "h-full w-full rounded-md p-2 text-[10px] border shadow-sm transition-all hover:scale-[1.02]",
                        task.load > 0.7 ? "bg-orange-50 border-orange-100" : "bg-blue-50 border-blue-100"
                      )}>
                        <div className="font-bold truncate text-[#37352f]">{task.title}</div>
                        <div className="mt-1 flex items-center gap-1 text-[#787774] font-medium">
                          <Clock className="w-2 h-2" /> {task.duration}m
                        </div>
                        <div className="absolute bottom-1 right-1 bg-green-500/10 text-green-700 px-1 rounded-[4px] text-[8px] font-black tracking-tighter">
                          +{task.slack}M
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
