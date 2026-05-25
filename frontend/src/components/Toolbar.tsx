import { motion } from 'framer-motion';
import { SystemSnapshot } from '../types';

interface ToolbarProps {
  onStep: () => void;
  onRun: () => void;
  onReset: () => void;
  snapshot: SystemSnapshot | null;
}

export default function Toolbar({ onStep, onRun, onReset, snapshot }: ToolbarProps) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-1">
        <button onClick={onStep} className="cyber-button text-xs px-3 py-1.5" title="Step one cycle">
          Step
        </button>
        <button onClick={onRun} className="cyber-button primary text-xs px-3 py-1.5" title="Run to halt">
          Run
        </button>
        <button onClick={onReset} className="cyber-button danger text-xs px-3 py-1.5" title="Reset CPU">
          Reset
        </button>
      </div>
      <div className="flex items-center gap-3 text-xs font-mono text-gray-500 border-l border-cyber-navy/30 pl-4">
        <span>Cyc: <span className="text-cyber-cyan">{snapshot?.clock_cycle ?? 0}</span></span>
        <span>PC: <span className="text-cyber-amber">{snapshot?.pc ?? 0}</span></span>
        <span>Instr: <span className="text-cyber-neon">{snapshot?.current_instruction ?? '---'}</span></span>
      </div>
    </div>
  );
}
