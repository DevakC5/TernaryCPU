import { motion } from 'framer-motion';
import { SystemSnapshot } from '../types';

interface DatapathVisualizerProps {
  snapshot: SystemSnapshot | null;
}

interface BusPulse {
  id: string;
  x1: number; y1: number; x2: number; y2: number;
  active: boolean;
  color: string;
}

function DatapathSVG({ pulses }: { pulses: BusPulse[] }) {
  return (
    <svg className="w-full h-full" viewBox="0 0 600 400">
      <defs>
        <filter id="glow-dp">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <marker id="arrow-cyan" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
          <polygon points="0 0, 6 2, 0 4" fill="#00ff88" />
        </marker>
        <marker id="arrow-purple" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">
          <polygon points="0 0, 6 2, 0 4" fill="#8888ff" />
        </marker>
      </defs>

      {/* Background grid */}
      <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
        <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#0f3460" strokeWidth="0.5" opacity="0.3" />
      </pattern>
      <rect width="600" height="400" fill="url(#grid)" />

      {/* Static connection paths */}
      <g stroke="#0f3460" strokeWidth="1" fill="none" opacity="0.5">
        {/* CPU ↔ Memory */}
        <path d="M 120,140 L 120,280 L 300,280" />
        <path d="M 120,260 L 120,280" />

        {/* CPU ↔ ALU */}
        <path d="M 120,180 L 200,180" />

        {/* CPU ↔ Registers */}
        <path d="M 120,120 L 120,80" />

        {/* Pipeline ↔ Memory */}
        <path d="M 300,120 L 300,280" />

        {/* Memory ↔ Cache */}
        <path d="M 300,280 L 480,280" />
        <path d="M 480,120 L 480,280" />

        {/* Cache ↔ Databus */}
        <path d="M 480,200 L 550,200" />
      </g>

      {/* Animated pulse paths */}
      {pulses.map(p => (
        p.active && (
          <motion.g key={p.id}>
            <motion.line
              x1={p.x1} y1={p.y1} x2={p.x2} y2={p.y2}
              stroke={p.color}
              strokeWidth="2"
              strokeDasharray="4 4"
              filter="url(#glow-dp)"
              markerEnd={p.color === '#00ff88' ? 'url(#arrow-cyan)' : 'url(#arrow-purple)'}
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
            />
            <motion.circle
              r="3" fill={p.color} filter="url(#glow-dp)"
              initial={{ offsetDistance: '0%' }}
              animate={{ offsetDistance: '100%' }}
              style={{ offsetPath: `path("M ${p.x1},${p.y1} L ${p.x2},${p.y2}")` }}
              transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
            />
          </motion.g>
        )
      ))}

      {/* Component boxes */}
      {/* CPU Core */}
      <motion.g
        animate={{ filter: pulses.some(p => p.active && p.id.includes('cpu')) ? 'url(#glow-dp)' : 'none' }}
      >
        <rect x="70" y="100" width="100" height="60" rx="6" fill="#0f3460" stroke="#00ff88" strokeWidth="1.5" />
        <text x="120" y="135" textAnchor="middle" fill="#00ff88" fontSize="12" fontFamily="JetBrains Mono, monospace" fontWeight="bold">CPU</text>
      </motion.g>

      {/* ALU */}
      <motion.g
        animate={{ filter: pulses.some(p => p.id.includes('alu')) ? 'url(#glow-dp)' : 'none' }}
      >
        <rect x="200" y="155" width="80" height="50" rx="6" fill="#442200" stroke="#884400" strokeWidth="1.5" />
        <text x="240" y="180" textAnchor="middle" fill="#ff8844" fontSize="11" fontFamily="JetBrains Mono, monospace" fontWeight="bold">ALU</text>
      </motion.g>

      {/* Registers */}
      <motion.g
        animate={{ filter: pulses.some(p => p.id.includes('reg')) ? 'url(#glow-dp)' : 'none' }}
      >
        <rect x="70" y="50" width="100" height="40" rx="6" fill="#16213e" stroke="#8888ff" strokeWidth="1.5" />
        <text x="120" y="74" textAnchor="middle" fill="#8888ff" fontSize="10" fontFamily="JetBrains Mono, monospace">Registers</text>
      </motion.g>

      {/* Memory */}
      <motion.g
        animate={{ filter: pulses.some(p => p.id.includes('mem')) ? 'url(#glow-dp)' : 'none' }}
      >
        <rect x="250" y="250" width="100" height="60" rx="6" fill="#16213e" stroke="#00ffcc" strokeWidth="1.5" />
        <text x="300" y="285" textAnchor="middle" fill="#00ffcc" fontSize="11" fontFamily="JetBrains Mono, monospace" fontWeight="bold">Memory</text>
      </motion.g>

      {/* Cache */}
      <motion.g
        animate={{ filter: pulses.some(p => p.id.includes('cache')) ? 'url(#glow-dp)' : 'none' }}
      >
        <rect x="430" y="160" width="100" height="50" rx="6" fill="#16213e" stroke="#4488ff" strokeWidth="1.5" />
        <text x="480" y="185" textAnchor="middle" fill="#4488ff" fontSize="11" fontFamily="JetBrains Mono, monospace" fontWeight="bold">Cache</text>
      </motion.g>

      {/* DMA */}
      <motion.g
        animate={{ filter: pulses.some(p => p.id.includes('dma')) ? 'url(#glow-dp)' : 'none' }}
      >
        <rect x="430" y="300" width="80" height="40" rx="6" fill="#16213e" stroke="#ff8844" strokeWidth="1.5" />
        <text x="470" y="325" textAnchor="middle" fill="#ff8844" fontSize="10" fontFamily="JetBrains Mono, monospace">DMA</text>
      </motion.g>

      {/* Pipeline labels */}
      <g fontSize="8" fontFamily="JetBrains Mono, monospace" fill="#555">
        <text x="180" y="180">RAW</text>
        <text x="180" y="275">data</text>
        <text x="390" y="195">bus</text>
        <text x="440" y="280">DMA</text>
      </g>
    </svg>
  );
}

export default function DatapathVisualizer({ snapshot }: DatapathVisualizerProps) {
  if (!snapshot) {
    return (
      <div className="h-full flex items-center justify-center text-gray-600 font-mono text-sm">
        No data — load a program to see datapaths
      </div>
    );
  }

  const instr = snapshot.current_instruction;
  const opcode = instr.split(' ')[0] || '';
  const hasAluOp = ['ADD', 'SUB', 'MUL', 'DIV', 'AND', 'OR', 'NOT', 'CMP'].includes(opcode);
  const hasMemOp = ['LOAD', 'STOREM', 'LOADM', 'PUSH', 'POP'].includes(opcode);
  const hasBranch = ['JMP', 'JZ', 'JNZ', 'CALL', 'RET'].includes(opcode);
  const hasDma = snapshot.dma?.active;
  const hasRegOp = opcode.length > 0 && !hasAluOp && !hasMemOp && !hasBranch;

  const pulses: BusPulse[] = [
    { id: 'cpu-reg', x1: 120, y1: 120, x2: 120, y2: 90, active: hasRegOp || hasAluOp, color: '#8888ff' },
    { id: 'cpu-alu', x1: 130, y1: 140, x2: 200, y2: 180, active: hasAluOp, color: '#ff8844' },
    { id: 'cpu-mem', x1: 120, y1: 160, x2: 120, y2: 260, active: hasMemOp, color: '#00ffcc' },
    { id: 'mem-cache', x1: 310, y1: 280, x2: 460, y2: 200, active: hasMemOp, color: '#4488ff' },
    { id: 'dma-mem', x1: 470, y1: 300, x2: 350, y2: 280, active: !!hasDma, color: '#ff8844' },
    { id: 'cpu-branch', x1: 120, y1: 130, x2: 120, y2: 110, active: hasBranch, color: '#ff4488' },
  ];

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-cyber-cyan font-mono font-bold">CPU Datapath</span>
        <div className="flex gap-2 text-[10px] font-mono">
          {pulses.map(p => (
            <span
              key={p.id}
              className={`px-1.5 py-0.5 rounded ${p.active ? 'text-white' : 'text-gray-700'}`}
              style={{ background: p.active ? `${p.color}33` : 'transparent' }}
            >
              {p.id.split('-')[0]}
            </span>
          ))}
        </div>
      </div>
      <div className="flex-1 glass-panel overflow-hidden">
        <DatapathSVG pulses={pulses} />
      </div>
    </div>
  );
}
