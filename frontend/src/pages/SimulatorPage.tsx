import { useState, useCallback, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useWebSocket } from '../websocket/useWebSocket';
import Toolbar from '../components/Toolbar';
import PipelineVisualizer from '../visualizers/PipelineVisualizer';
import DatapathVisualizer from '../visualizers/DatapathVisualizer';
import RegisterView from '../components/Registers';
import CacheHeatmap from '../visualizers/CacheHeatmap';
import BranchPredictor from '../visualizers/BranchPredictor';
import WaveformViewer from '../visualizers/WaveformViewer';
import ExecutionTimeline from '../visualizers/ExecutionTimeline';
import BusVisualizer from '../visualizers/BusVisualizer';
import AssemblyEditor from '../components/AssemblyEditor';

type TabId = 'pipeline' | 'datapath' | 'cache' | 'branch' | 'waveform' | 'timeline' | 'bus';

export default function SimulatorPage() {
  const { snapshot, demos, connected, loadResult, loadProgram, step, run, reset } = useWebSocket();
  const [activeTab, setActiveTab] = useState<TabId>('pipeline');
  const [source, setSource] = useState('');
  const [executionHistory, setExecutionHistory] = useState<any[]>([]);
  const [signalHistory, setSignalHistory] = useState<Record<string, number[]>>({});
  const prevSnapshotRef = useRef<any>(null);

  // Load default demo on connect
  useEffect(() => {
    if (demos.length > 0 && !source) {
      const defaultDemo = demos[0];
      setSource(defaultDemo.source);
    }
  }, [demos, source]);

  // Track execution history for timeline
  useEffect(() => {
    if (!snapshot) return;
    const prev = prevSnapshotRef.current;
    if (prev && snapshot.cycle !== prev.cycle) {
      setExecutionHistory(h => [...h.slice(-100), {
        instr: snapshot.current_instruction,
        cycle: snapshot.clock_cycle,
        pc: snapshot.pc,
        registers: { ...snapshot.registers },
        pipeline: snapshot.pipeline,
      }]);
    }
    prevSnapshotRef.current = snapshot;
  }, [snapshot]);

  // Build signal data for waveform viewer
  useEffect(() => {
    if (!snapshot) return;
    const signals: Record<string, number> = {
      clk: snapshot.clock_cycle % 2,
      pc: snapshot.pc,
      sp: snapshot.sp,
      halted: snapshot.halted ? 1 : 0,
      cache_hit: snapshot.dcache ? (snapshot.dcache.hit_rate > 0.8 ? 1 : 0) : 0,
      branch_taken: 0,
      int: snapshot.interrupt ? snapshot.interrupt.pending : 0,
      dma: snapshot.dma?.active ? 1 : 0,
      bus: snapshot.bus && snapshot.bus.utilization > 0.3 ? 1 : 0,
    };
    setSignalHistory(prev => {
      const next: Record<string, number[]> = {};
      for (const [k, v] of Object.entries(signals)) {
        next[k] = [...(prev[k] || []).slice(-120), v];
      }
      return next;
    });
  }, [snapshot]);

  const handleLoad = useCallback(() => {
    if (source.trim()) {
      loadProgram(source);
      setExecutionHistory([]);
      setSignalHistory({});
    }
  }, [source, loadProgram]);

  const handleDemoSelect = useCallback((name: string) => {
    const demo = demos.find(d => d.name === name);
    if (demo) setSource(demo.source);
  }, [demos]);

  const tabs: { id: TabId; label: string }[] = [
    { id: 'pipeline', label: 'Pipeline' },
    { id: 'datapath', label: 'Datapath' },
    { id: 'cache', label: 'Cache' },
    { id: 'branch', label: 'Branch' },
    { id: 'timeline', label: 'Timeline' },
    { id: 'waveform', label: 'Waveform' },
    { id: 'bus', label: 'Bus' },
  ];

  return (
    <div className="h-screen bg-cyber-dark flex flex-col overflow-hidden">
      <div className="crt-overlay" />

      {/* Header */}
      <header className="flex-shrink-0 glass-panel rounded-none border-x-0 border-t-0 px-4 py-2 flex items-center justify-between z-20">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-display font-bold text-cyber-cyan">
            Ternary<span className="text-cyber-purple">CPU</span>
          </h1>
          <span className="text-[10px] text-gray-600">v1.0</span>
          <div className="flex items-center gap-2 ml-4">
            <span className={`pulse-dot ${connected ? 'bg-cyber-cyan' : 'bg-cyber-red'}`} />
            <span className="text-xs text-gray-500">{connected ? 'CONNECTED' : 'DISCONNECTED'}</span>
          </div>
        </div>
        <Toolbar
          onStep={() => step(1)}
          onRun={run}
          onReset={reset}
          snapshot={snapshot}
        />
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel: Assembly Editor */}
        <div className="w-80 flex-shrink-0 border-r border-cyber-navy/30 flex flex-col">
          <AssemblyEditor
            source={source}
            onChange={setSource}
            demos={demos}
            onDemoSelect={handleDemoSelect}
            onLoad={handleLoad}
            loadResult={loadResult}
            pc={snapshot?.pc ?? -1}
            instructions={snapshot ? undefined : undefined}
          />
          <RegisterView registers={snapshot?.registers ?? {}} flags={snapshot?.flags ?? {}} pc={snapshot?.pc ?? 0} sp={snapshot?.sp ?? 0} />
        </div>

        {/* Center: Visualization Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tab bar */}
          <div className="flex-shrink-0 flex border-b border-cyber-navy/30 bg-cyber-dark/80 px-2">
            {tabs.map(t => (
              <button
                key={t.id}
                onClick={() => setActiveTab(t.id)}
                className={`px-4 py-2 text-xs font-mono transition-all border-b-2 ${
                  activeTab === t.id
                    ? 'text-cyber-cyan border-cyber-cyan'
                    : 'text-gray-600 border-transparent hover:text-gray-400'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <div className="flex-1 overflow-auto p-3">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                {activeTab === 'pipeline' && (
                  <PipelineVisualizer pipeline={snapshot?.pipeline ?? null} cycle={snapshot?.clock_cycle ?? 0} />
                )}
                {activeTab === 'datapath' && (
                  <DatapathVisualizer snapshot={snapshot} />
                )}
                {activeTab === 'cache' && (
                  <div className="grid grid-cols-2 gap-4 h-full">
                    <CacheHeatmap cache={snapshot?.dcache ?? null} label="Data Cache (D$)" />
                    <CacheHeatmap cache={snapshot?.icache ?? null} label="Instruction Cache (I$)" />
                  </div>
                )}
                {activeTab === 'branch' && (
                  <BranchPredictor branch={snapshot?.branch ?? null} />
                )}
                {activeTab === 'timeline' && (
                  <ExecutionTimeline history={executionHistory} />
                )}
                {activeTab === 'waveform' && (
                  <WaveformViewer signals={signalHistory} />
                )}
                {activeTab === 'bus' && (
                  <BusVisualizer bus={snapshot?.bus ?? null} dma={snapshot?.dma ?? null} />
                )}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Status bar */}
      <footer className="flex-shrink-0 border-t border-cyber-navy/30 px-4 py-1 flex items-center justify-between text-[10px] text-gray-600">
        <span>
          {snapshot
            ? `Cycle ${snapshot.clock_cycle}  |  PC ${snapshot.pc}  |  ${snapshot.current_instruction || 'idle'}`
            : 'Waiting for snapshot...'}
        </span>
        <span>{snapshot?.halted ? 'HALTED' : 'RUNNING'}</span>
      </footer>
    </div>
  );
}
