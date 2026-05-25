import { motion } from 'framer-motion';
import { BranchData } from '../types';

interface BranchPredictorProps {
  branch: BranchData | null;
}

const COUNTER_STATES = ['00 (Strong NT)', '01 (Weak NT)', '10 (Weak T)', '11 (Strong T)'];

export default function BranchPredictor({ branch }: BranchPredictorProps) {
  if (!branch) {
    return <div className="h-full flex items-center justify-center text-gray-600 font-mono text-sm">No branch predictor data</div>;
  }

  const accuracyPct = (branch.accuracy * 100).toFixed(1);
  const accuracyColor = branch.accuracy >= 0.8 ? '#00ff88' : '#ff4444';

  // Find the most common counter value for visualization
  const counterValues = Object.values(branch.counters);
  const avgCounter = counterValues.length > 0
    ? counterValues.reduce((a, b) => a + b, 0) / counterValues.length
    : 2;

  return (
    <div className="h-full flex flex-col gap-3">
      {/* Stats row */}
      <div className="flex gap-4 text-xs font-mono">
        <div className="glass-panel px-3 py-2 flex-1">
          <div className="text-gray-500 text-[10px]">Mode</div>
          <div className="text-cyber-cyan font-bold">{branch.mode}</div>
        </div>
        <div className="glass-panel px-3 py-2 flex-1">
          <div className="text-gray-500 text-[10px]">Predictions</div>
          <div className="text-white font-bold">{branch.predictions}</div>
        </div>
        <div className="glass-panel px-3 py-2 flex-1">
          <div className="text-gray-500 text-[10px]">Mispredicts</div>
          <div className="text-cyber-magenta font-bold">{branch.mispredictions}</div>
        </div>
        <div className="glass-panel px-3 py-2 flex-1">
          <div className="text-gray-500 text-[10px]">Accuracy</div>
          <div className="font-bold" style={{ color: accuracyColor }}>{accuracyPct}%</div>
        </div>
      </div>

      {/* Accuracy bar */}
      <div className="glass-panel p-3">
        <div className="flex justify-between text-[10px] font-mono text-gray-500 mb-1">
          <span>Branch Prediction Accuracy</span>
          <span>{accuracyPct}%</span>
        </div>
        <div className="h-4 rounded bg-cyber-dark overflow-hidden border border-cyber-navy/30">
          <motion.div
            className="h-full rounded"
            style={{
              background: `linear-gradient(90deg, ${accuracyColor}44, ${accuracyColor})`,
              width: `${accuracyPct}%`,
            }}
            animate={{ width: `${accuracyPct}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* State machine visualization */}
      <div className="glass-panel p-3 flex-1">
        <div className="text-[10px] text-gray-500 font-mono mb-3">2-bit Saturating Counter State Machine</div>
        <div className="flex items-center justify-center gap-2 h-full">
          {[0, 1, 2, 3].map(state => {
            const isCurrent = Math.round(avgCounter) === state;
            return (
              <div key={state} className="flex flex-col items-center gap-2">
                <motion.div
                  className="w-20 h-14 rounded border-2 flex items-center justify-center font-mono text-xs"
                  style={{
                    borderColor: isCurrent ? '#00ff88' : '#0f3460',
                    backgroundColor: isCurrent ? '#00ff8811' : 'transparent',
                  }}
                  animate={isCurrent ? { scale: [1, 1.05, 1], boxShadow: ['0 0 0px #00ff88', '0 0 15px #00ff88', '0 0 0px #00ff88'] } : {}}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <span className={isCurrent ? 'text-white' : 'text-gray-600'}>{state}</span>
                </motion.div>
                <span className="text-[8px] text-gray-600 text-center">{COUNTER_STATES[state]}</span>
                {state < 3 && (
                  <div className="flex gap-3 text-[8px] text-gray-700 font-mono">
                    <span>↑T</span>
                    <span>↓NT</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
