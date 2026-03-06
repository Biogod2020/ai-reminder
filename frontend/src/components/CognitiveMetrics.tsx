import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Brain, Zap, Activity } from 'lucide-react';

const data = [
  { time: '08:00', energy: 0.6, load: 0.2 },
  { time: '10:00', energy: 0.9, load: 0.7 },
  { time: '12:00', energy: 0.7, load: 0.4 },
  { time: '14:00', energy: 0.4, load: 0.2 },
  { time: '16:00', energy: 0.8, load: 0.8 },
  { time: '18:00', energy: 0.6, load: 0.3 },
  { time: '20:00', energy: 0.3, load: 0.1 },
];

export function CognitiveMetrics() {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Cognitive Analytics</h2>
          <p className="text-muted-foreground">Real-time UMP energy peaks and CLT load monitoring.</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-100">
            <Zap className="w-4 h-4 text-blue-600" />
            <span className="text-xs font-bold text-blue-700 uppercase">UMP Peak</span>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-50 border border-orange-100">
            <Activity className="w-4 h-4 text-orange-600" />
            <span className="text-xs font-bold text-orange-700 uppercase">CLT Load</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 p-6 rounded-3xl border border-border bg-card shadow-sm h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorEnergy" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2383e2" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="#2383e2" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                axisLine={false} 
                tickLine={false} 
                tick={{fontSize: 12, fill: '#9b9b9b'}} 
              />
              <YAxis hide domain={[0, 1]} />
              <Tooltip 
                contentStyle={{borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
              />
              <Area 
                type="monotone" 
                dataKey="energy" 
                stroke="#2383e2" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorEnergy)" 
              />
              <Area 
                type="monotone" 
                dataKey="load" 
                stroke="#f97316" 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorLoad)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-6">
          <div className="p-6 rounded-3xl border border-border bg-blue-50/20">
            <Brain className="w-8 h-8 text-blue-600 mb-4" />
            <h3 className="text-lg font-bold mb-1 text-blue-900">Mental Reserve</h3>
            <p className="text-sm text-blue-700/70 mb-4">Your current cognitive capacity is at a safe margin.</p>
            <div className="w-full bg-blue-100 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{width: '65%'}}></div>
            </div>
          </div>

          <div className="p-6 rounded-3xl border border-border bg-orange-50/20">
            <Activity className="w-8 h-8 text-orange-600 mb-4" />
            <h3 className="text-lg font-bold mb-1 text-orange-900">Load Pressure</h3>
            <p className="text-sm text-orange-700/70">Moderate external load detected from pending tasks.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
