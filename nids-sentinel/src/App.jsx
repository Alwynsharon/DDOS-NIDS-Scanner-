import React, { useState, useRef } from 'react';
import { 
  Shield, Activity, Database, Zap, RefreshCw, AlertTriangle, 
  ChevronRight, Bell, Terminal, CheckCircle, Clock, FileJson, Download
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';

const API_BASE = "http://127.0.0.1:8000";

const App = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  // States
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [safetyScore, setSafetyScore] = useState(100);
  const [liveStreamData, setLiveStreamData] = useState([]); // Graph Window
  const [allCapturedData, setAllCapturedData] = useState([]); // Full History for Export
  const [anomaliesCount, setAnomaliesCount] = useState(0);
  const [totalFlowsCount, setTotalFlowsCount] = useState(0);
  const [notifications, setNotifications] = useState([]);

  const pollInterval = useRef(null);

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [{ id, message, type }, ...prev]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== id)), 5000);
  };

  const handleStartLive = async () => {
    try {
      await fetch(`${API_BASE}/start_capture`, { method: 'POST' });
      setIsMonitoring(true);
      setLiveStreamData([]);
      setAllCapturedData([]);
      setAnomaliesCount(0);
      setTotalFlowsCount(0);
      setSafetyScore(100);
      addNotification("Live Sensor Activated", "success");

      pollInterval.current = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE}/live_feed`);
          const result = await res.json();
          
          if (result.data && result.data.length > 0) {
            setLiveStreamData(prev => [...prev, ...result.data].slice(-50));
            setAllCapturedData(prev => [...prev, ...result.data]);
            setAnomaliesCount(result.anomaly_count);
            setTotalFlowsCount(result.total_count);
            setSafetyScore(result.current_safety);
          }
        } catch (e) { console.error(e); }
      }, 500);
    } catch (error) { addNotification("Sensor Error", "danger"); }
  };

  const handleStopLive = async () => {
    clearInterval(pollInterval.current);
    await fetch(`${API_BASE}/stop_capture`, { method: 'POST' });
    setIsMonitoring(false);
    addNotification("Sensor Stopped", "info");
  };

  // --- EXPORT FUNCTIONS ---
  const handleExportJSON = () => {
    if (allCapturedData.length === 0) {
        addNotification("No data to export", "warning");
        return;
    }
    const blob = new Blob([JSON.stringify(allCapturedData, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `live_capture_${Date.now()}.json`;
    link.click();
    addNotification("JSON Export downloaded", "success");
  };

  const handleExportCSV = () => {
    if (allCapturedData.length === 0) {
        addNotification("No data to export", "warning");
        return;
    }
    const headers = ["ID", "Source", "Dest", "PPS", "Score", "Label"];
    const rows = allCapturedData.map(d => 
        `${d.id},${d.src_ip},${d.dest_ip},${d.pps},${d.raw_score},${d.label}`
    );
    const csvContent = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `live_capture_${Date.now()}.csv`;
    link.click();
    addNotification("CSV Export downloaded", "success");
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 50) return 'text-amber-400';
    return 'text-rose-500';
  };

  return (
    <div className="flex min-h-screen bg-[#050505] text-slate-300 font-sans">
      
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-[#0a0a0a] border-r border-white/5 flex flex-col p-6 z-50 shadow-2xl">
        <div className="flex items-center gap-3 mb-10 px-2">
          <div className="p-2 bg-indigo-600 rounded-lg shadow-lg">
            <Shield className="text-white" size={20} />
          </div>
          <span className="text-lg font-black tracking-tighter text-white italic uppercase">DDOS SCANNER</span>
        </div>
        <nav className="space-y-1">
          <button onClick={() => setActiveTab('overview')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'overview' ? 'bg-white/5 text-white border border-white/10' : 'text-slate-500 hover:text-slate-300'}`}>
            <Activity size={18} /> <span className="text-sm font-medium">Live Monitor</span>
          </button>
          <button onClick={() => setActiveTab('matrix')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeTab === 'matrix' ? 'bg-white/5 text-white border border-white/10' : 'text-slate-500 hover:text-slate-300'}`}>
            <Database size={18} /> <span className="text-sm font-medium">Flow Matrix</span>
          </button>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="pl-64 flex-1 min-h-screen p-8 max-w-7xl mx-auto">
        
        {/* Header */}
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-2 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
            <Terminal size={12}/> <span>System Active</span> <ChevronRight size={10} /> <span className="text-white">{activeTab}</span>
          </div>
          <div className="flex items-center gap-4">
            <Bell size={18} className="text-slate-500" />
          </div>
        </header>

        {activeTab === 'overview' && (
          <div className="space-y-8 animate-in fade-in duration-700">
            
            {/* MAIN CONTROL PANEL */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              
              {/* CARD 1: LIVE SENSOR */}
              <div className="lg:col-span-2 bg-[#0a0a0a] border border-white/5 rounded-3xl p-8 relative overflow-hidden group hover:border-indigo-500/20 transition-all">
                 <div className="absolute top-0 right-0 p-8 opacity-5 text-indigo-500"><Zap size={100} /></div>
                 <h2 className="text-xl font-bold text-white mb-2 italic">Real-Time Threat Detection</h2>
                 <p className="text-slate-500 mb-6 text-xs">Hybrid Engine: Rules (SYN/UDP) + Unsupervised ML (Isolation Forest)</p>
                 {!isMonitoring ? (
                   <button onClick={handleStartLive} className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 uppercase text-xs tracking-widest transition-all">
                     <Zap size={16} /> Activate Sensor
                   </button>
                 ) : (
                   <button onClick={handleStopLive} className="w-full py-4 bg-rose-600 hover:bg-rose-500 text-white font-bold rounded-xl flex items-center justify-center gap-2 uppercase text-xs tracking-widest animate-pulse">
                     <RefreshCw size={16} className="animate-spin" /> Stop Sensor
                   </button>
                 )}
              </div>

               {/* CARD 2: SAFETY GAUGE */}
               <div className="bg-[#0a0a0a] border border-white/5 rounded-3xl p-8 flex flex-col items-center justify-center text-center">
                <div className={`text-7xl font-black mb-4 ${getScoreColor(safetyScore)}`}>{Math.round(safetyScore)}</div>
                <h3 className="text-white font-bold text-sm italic">Network Safety Index</h3>
                <p className="text-slate-600 text-[10px] mt-2 uppercase tracking-wider">Normalized Risk Score</p>
              </div>

            </div>

            {/* TELEMETRY CHART */}
            <div className="bg-[#0a0a0a] border border-white/5 p-8 rounded-3xl shadow-inner relative overflow-hidden h-72">
                <div className="absolute top-4 left-6 z-10"><h3 className="font-bold text-white text-sm flex items-center gap-2 italic"><Activity size={16} className="text-indigo-400" /> Live Telemetry</h3></div>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={liveStreamData}>
                    <defs>
                      <linearGradient id="colorAnom" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" vertical={false} />
                    <XAxis dataKey="id" hide />
                    {/* Y-Axis scaled for -0.5 (Attack) to 0.5 (Normal) */}
                    <YAxis domain={[-1, 1]} hide /> 
                    <Tooltip contentStyle={{ backgroundColor: '#000', border: '1px solid #222' }} />
                    <Area type="monotone" dataKey="raw_score" stroke="#6366f1" strokeWidth={2} fill="url(#colorAnom)" isAnimationActive={false}/>
                  </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* STATS */}
            <div className="grid grid-cols-4 gap-6">
              {[
                { label: 'Packets Scanned', value: totalFlowsCount, icon: Terminal, color: 'text-indigo-400' },
                { label: 'Active Threats', value: anomaliesCount, icon: AlertTriangle, color: 'text-rose-500' },
                { label: 'System Status', value: isMonitoring ? 'Monitoring' : 'Standby', icon: CheckCircle, color: isMonitoring ? 'text-emerald-400' : 'text-slate-500' },
                { label: 'Protocol', value: 'TCP/IP', icon: Clock, color: 'text-slate-500' }
              ].map((stat, i) => (
                <div key={i} className="bg-[#0a0a0a] border border-white/5 p-6 rounded-2xl">
                   <div className="flex justify-between mb-2"><p className="text-[10px] font-black text-slate-600 uppercase tracking-widest">{stat.label}</p><stat.icon size={14} className={stat.color} /></div>
                   <p className="text-xl font-bold text-white">{stat.value}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'matrix' && (
          <div className="space-y-6 animate-in slide-in-from-bottom-4">
             <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-xl font-bold text-white italic">Flow Matrix</h2>
                    <p className="text-xs text-slate-500">Live captured flows. Export for forensic analysis.</p>
                </div>
                <div className="flex gap-2">
                    <button onClick={handleExportJSON} className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-white/10 transition-all hover:text-indigo-400">
                      <FileJson size={12} /> Export JSON
                    </button>
                    <button onClick={handleExportCSV} className="flex items-center gap-2 px-4 py-2 bg-indigo-600 rounded-xl text-[10px] font-black uppercase tracking-widest text-white shadow-lg shadow-indigo-600/20 hover:bg-indigo-500 transition-all">
                      <Download size={12} /> Export CSV
                    </button>
                 </div>
             </div>
             <div className="bg-[#0a0a0a] border border-white/5 rounded-3xl overflow-hidden shadow-2xl">
              <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
                <table className="w-full text-left text-[11px]">
                    <thead className="bg-white/[0.02] border-b border-white/5 text-slate-500 font-black uppercase tracking-widest sticky top-0 bg-[#0a0a0a]">
                    <tr><th className="px-6 py-5">Source IP</th><th className="px-6 py-5">Dest IP</th><th className="px-6 py-5">PPS</th><th className="px-6 py-5 text-right">Label</th></tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 font-mono">
                    {liveStreamData.slice().reverse().map((row, idx) => (
                        <tr key={idx} className="hover:bg-white/[0.01]">
                        <td className="px-6 py-4 text-slate-400">{row.src_ip}</td>
                        <td className="px-6 py-4 text-slate-400">{row.dest_ip}</td>
                        <td className="px-6 py-4 text-slate-500">{Math.round(row.pps)}</td>
                        <td className="px-6 py-4 text-right"><span className={`px-2 py-1 rounded text-[9px] font-bold uppercase ${row.raw_score < 0 ? 'text-rose-500 bg-rose-500/10' : 'text-emerald-500 bg-emerald-500/10'}`}>{row.label}</span></td>
                        </tr>
                    ))}
                    {liveStreamData.length === 0 && (
                        <tr><td colSpan="4" className="px-6 py-20 text-center opacity-30">Waiting for live traffic...</td></tr>
                    )}
                    </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

      </main>

      {/* Notifications */}
      <div className="fixed bottom-8 right-8 space-y-3 z-[100]">
        {notifications.map(n => (
          <div key={n.id} className={`px-6 py-4 rounded-2xl border flex items-center gap-4 shadow-2xl animate-in slide-in-from-right-10 ${n.type === 'danger' ? 'bg-rose-950/20 border-rose-500/50 text-rose-500' : 'bg-[#0a0a0a] border-white/10 text-slate-200'}`}>
            <CheckCircle size={18} /> <span className="text-xs font-black uppercase tracking-wider">{n.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;