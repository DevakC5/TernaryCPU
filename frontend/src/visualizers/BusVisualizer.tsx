import { motion } from 'framer-motion';
import { BusData, DMAData } from '../types';

interface BusVisualizerProps {
  bus: BusData | null;
  dma: DMAData | null;
}

function BusNode({ name, x, y, color, active }: { name: string; x: number; y: number; color: string; active: boolean }) {
  return (
    <g>
      <motion.rect
        x={x} y={y} width={60} height={30} rx={6}
        fill={active ? `${color}44` : '#16213e'}
        stroke={active ? color : '#0f3460'}
        strokeWidth={1.5}
        animate={active ? { stroke: [color, '#00ff88', color], transition: { duration: 1, repeat: Infinity } } : {}}
      />
      <text x={x + 30} y={y + 19} textAnchor="middle" fill={active ? color : '#555'} fontSize={10} fontFamily="JetBrains Mono, monospace" fontWeight="bold">
        {name}
      </text>
    </g>
  );
}

export default function BusVisualizer({ bus, dma }: BusVisualizerProps) {
  const utilPct = bus ? Math.round(bus.utilization * 100) : 0;
  const utilColor = utilPct > 50 ? '#ff8844' : utilPct > 20 ? '#00ff88' : '#333';

  return (
    <div className="h-full flex flex-col gap-3">
      {/* Stats cards */}
      <div className="grid grid-cols-4 gap-3">
        <div className="glass-panel px-3 py-2">
          <div className="text-[10px] text-gray-500 font-mono">Transfers</div>
          <div className="text-white font-mono text-lg">{bus?.transfers ?? 0}</div>
        </div>
        <div className="glass-panel px-3 py-2">
          <div className="text-[10px] text-gray-500 font-mono">Pending</div>
          <div className="text-cyber-amber font-mono text-lg">{bus?.pending ?? 0}</div>
        </div>
        <div className="glass-panel px-3 py-2">
          <div className="text-[10px] text-gray-500 font-mono">Utilization</div>
          <div className="font-mono text-lg" style={{ color: utilColor }}>{utilPct}%</div>
        </div>
        <div className="glass-panel px-3 py-2">
          <div className="text-[10px] text-gray-500 font-mono">DMA Active</div>
          <div className={!!dma?.active ? 'text-cyber-cyan font-mono text-lg' : 'text-gray-700 font-mono text-lg'}>
            {!!dma?.active ? 'YES' : 'NO'}
          </div>
        </div>
      </div>

      {/* Bandwidth bar */}
      <div className="glass-panel p-3">
        <div className="flex justify-between text-[10px] font-mono text-gray-500 mb-1">
          <span>Bus Bandwidth</span>
          <span>{utilPct}%</span>
        </div>
        <div className="h-5 rounded bg-cyber-dark overflow-hidden border border-cyber-navy/30">
          <motion.div
            className="h-full rounded"
            style={{ background: `linear-gradient(90deg, #004488, ${utilColor})` }}
            animate={{ width: `${utilPct}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </div>
      </div>

      {/* Bus Diagram */}
      <div className="glass-panel flex-1 p-4 flex items-center justify-center">
        <svg viewBox="0 0 500 300" className="w-full h-full max-w-[500px]">
          {/* Center BUS */}
          <motion.rect
            x={200} y={130} width={100} height={40} rx={8}
            fill={bus && bus.utilization > 0 ? '#00448844' : '#1a1a2e'}
            stroke={bus && bus.utilization > 0 ? '#004488' : '#0f3460'}
            strokeWidth={2}
            animate={bus && bus.utilization > 0 ? { boxShadow: '0 0 20px #004488' } as any : {}}
          />
          <text x={250} y={155} textAnchor="middle" fill={bus && bus.utilization > 0 ? '#4488ff' : '#555'} fontSize={12} fontFamily="JetBrains Mono, monospace" fontWeight="bold">BUS</text>

          {/* Connection lines */}
          <g stroke="#0f3460" strokeWidth={1} opacity={0.5}>
            <line x1={200} y1={150} x2={140} y2={100} />
            <line x1={200} y1={150} x2={140} y2={200} />
            <line x1={300} y1={150} x2={360} y2={100} />
            <line x1={300} y1={150} x2={360} y2={200} />
          </g>

          {/* Nodes */}
          <BusNode name="CPU" x={80} y={85} color="#00ff88" active={!!(bus && bus.utilization > 0)} />
          <BusNode name="DMA" x={80} y={185} color="#ff8844" active={dma !== null && dma.active} />
          <BusNode name="VRAM" x={360} y={85} color="#88ff88" active={false} />
          <BusNode name="ACCEL" x={360} y={185} color="#8888ff" active={false} />
        </svg>
      </div>
    </div>
  );
}
