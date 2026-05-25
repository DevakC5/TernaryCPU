import { motion, AnimatePresence } from 'framer-motion';
import { PipelineData, PipelineStage } from '../types';

interface PipelineVisualizerProps {
  pipeline: PipelineData | null;
  cycle: number;
}

const STAGE_NAMES = ['IF', 'ID', 'EX', 'MEM', 'WB'] as const;
const STAGE_COLORS: Record<string, string> = {
  IF: '#004488',
  ID: '#006644',
  EX: '#884400',
  MEM: '#440088',
  WB: '#008844',
};

function StageBox({ stage, name, isActive }: { stage: PipelineStage; name: string; isActive: boolean }) {
  const color = STAGE_COLORS[name] || '#333';
  const bgColor = stage.stalled ? '#882222' : stage.bubble ? '#1a1a2e' : color;

  return (
    <motion.div
      className="relative rounded border font-mono flex flex-col items-center justify-center overflow-hidden"
      style={{
        minWidth: 100,
        minHeight: 72,
        borderColor: `${color}66`,
        background: `${bgColor}99`,
      }}
      animate={{
        scale: isActive ? 1.03 : 1,
        borderColor: isActive ? '#00ff88' : `${color}66`,
        boxShadow: isActive
          ? `0 0 20px ${color}44, inset 0 0 20px ${color}22`
          : 'none',
      }}
      transition={{ duration: 0.3 }}
    >
      {/* Stage name */}
      <span className="text-[10px] font-bold mb-1" style={{ color }}>{name}</span>

      {/* Instruction */}
      <AnimatePresence mode="wait">
        {!stage.bubble && (
          <motion.span
            key={stage.instruction}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="text-[10px] text-white px-1 truncate max-w-[90px]"
          >
            {stage.opcode || '???'}
          </motion.span>
        )}
      </AnimatePresence>

      {/* Status badges */}
      {stage.stalled && (
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="text-[8px] text-red-400 font-bold mt-0.5"
        >
          STALL
        </motion.span>
      )}
      {stage.bubble && (
        <span className="text-[8px] text-gray-600">bubble</span>
      )}
    </motion.div>
  );
}

function StageArrow({ active }: { active: boolean }) {
  return (
    <div className="flex items-center px-1">
      <motion.svg
        width="24"
        height="16"
        viewBox="0 0 24 16"
        animate={active ? { x: [0, 3, 0] } : {}}
        transition={{ duration: 0.5, repeat: Infinity }}
      >
        <line
          x1="2" y1="8" x2="20" y2="8"
          stroke={active ? '#00ff88' : '#0f3460'}
          strokeWidth="1.5"
        />
        <polygon
          points="20,8 14,3 14,13"
          fill={active ? '#00ff88' : '#0f3460'}
        />
      </motion.svg>
    </div>
  );
}

export default function PipelineVisualizer({ pipeline, cycle }: PipelineVisualizerProps) {
  if (!pipeline) {
    return (
      <div className="h-full flex items-center justify-center text-gray-600 font-mono text-sm">
        <div className="text-center">
          <div className="mb-2">Pipeline idle</div>
          <div className="text-[10px] text-gray-700">Load and run a program to visualize</div>
        </div>
      </div>
    );
  }

  const stages: { name: string; data: PipelineStage }[] = [
    { name: 'IF', data: pipeline.if_stage },
    { name: 'ID', data: pipeline.id_stage },
    { name: 'EX', data: pipeline.ex_stage },
    { name: 'MEM', data: pipeline.mem_stage },
    { name: 'WB', data: pipeline.wb_stage },
  ];

  const activeStage = stages.findIndex(s => !s.data.bubble);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="text-sm text-cyber-cyan font-mono font-bold">
          Pipeline  IF → ID → EX → MEM → WB
        </div>
        <div className="flex gap-4 text-[10px] font-mono text-gray-500">
          <span>Cycle <span className="text-cyber-cyan">{cycle}</span></span>
          <span>Retired: <span className="text-cyber-neon">{pipeline.total_instructions}</span></span>
          <span>Stalls: <span className="text-cyber-magenta">{pipeline.stall_cycles}</span></span>
          <span>Flushes: <span className="text-cyber-amber">{pipeline.flush_count}</span></span>
        </div>
      </div>

      {/* Pipeline stages */}
      <div className="flex-1 flex items-center justify-center gap-0">
        {stages.map((s, i) => (
          <div key={s.name} className="flex items-center">
            <StageBox
              stage={s.data}
              name={s.name}
              isActive={i === activeStage}
            />
            {i < stages.length - 1 && (
              <StageArrow active={!s.data.bubble && !stages[i + 1].data.bubble} />
            )}
          </div>
        ))}
      </div>

      {/* Cycle indicator */}
      <div className="mt-2 h-1 rounded-full bg-cyber-navy/30 overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{
            background: 'linear-gradient(90deg, #00ff88, #8888ff)',
            width: `${Math.min(100, (cycle % 20) * 5)}%`,
          }}
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      </div>
    </div>
  );
}
