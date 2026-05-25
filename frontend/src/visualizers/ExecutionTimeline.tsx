import { useState, useRef } from 'react';

interface TimelineEntry {
  instr: string;
  cycle: number;
  pc: number;
  registers: Record<string, string>;
  pipeline: any;
}

interface ExecutionTimelineProps {
  history: TimelineEntry[];
}

export default function ExecutionTimeline({ history }: ExecutionTimelineProps) {
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  if (history.length === 0) {
    return <div className="h-full flex items-center justify-center text-gray-600 font-mono text-sm">No execution history</div>;
  }

  const recent = history;
  const rowH = 24;
  const colW = 60;

  return (
    <div className="h-full flex flex-col">
      <div className="text-xs text-cyber-cyan font-mono font-bold mb-2">
        Execution Timeline  <span className="text-gray-500 font-normal">({history.length} entries)</span>
      </div>
      <div ref={scrollRef} className="flex-1 glass-panel overflow-auto">
        <table className="w-full text-[10px] font-mono border-collapse">
          <thead className="sticky top-0 z-10" style={{ background: '#0a0a1a' }}>
            <tr className="text-gray-500 border-b border-cyber-navy/30">
              <th className="text-left px-2 py-1">#</th>
              <th className="text-left px-2 py-1">Instr</th>
              <th className="text-left px-2 py-1">PC</th>
              <th className="text-left px-2 py-1">Cycle</th>
              <th className="text-left px-2 py-1">R0</th>
              <th className="text-left px-2 py-1">R1</th>
              <th className="text-left px-2 py-1">R2</th>
              <th className="text-left px-2 py-1">R3</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((entry, i) => (
              <tr
                key={i}
                className="border-b border-cyber-navy/10 hover:bg-cyber-navy/20 transition-colors cursor-pointer"
                style={{ background: hoverIdx === i ? '#0f346033' : 'transparent' }}
                onMouseEnter={() => setHoverIdx(i)}
                onMouseLeave={() => setHoverIdx(null)}
              >
                <td className="px-2 py-1 text-gray-600">{i + 1}</td>
                <td className="px-2 py-1 text-cyber-cyan">{entry.instr}</td>
                <td className="px-2 py-1 text-cyber-amber">{entry.pc}</td>
                <td className="px-2 py-1 text-gray-400">{entry.cycle}</td>
                <td className={`px-2 py-1 ${entry.registers['R0'] !== '0' ? 'text-cyber-neon' : 'text-gray-700'}`}>{entry.registers['R0'] || '0'}</td>
                <td className={`px-2 py-1 ${entry.registers['R1'] !== '0' ? 'text-cyber-neon' : 'text-gray-700'}`}>{entry.registers['R1'] || '0'}</td>
                <td className={`px-2 py-1 ${entry.registers['R2'] !== '0' ? 'text-cyber-neon' : 'text-gray-700'}`}>{entry.registers['R2'] || '0'}</td>
                <td className={`px-2 py-1 ${entry.registers['R3'] !== '0' ? 'text-cyber-neon' : 'text-gray-700'}`}>{entry.registers['R3'] || '0'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
