import { motion } from 'framer-motion';
import { CacheData, CacheLine } from '../types';

interface CacheHeatmapProps {
  cache: CacheData | null;
  label: string;
}

function CacheCell({ line, index }: { line: CacheLine; index: number }) {
  const color = !line.valid
    ? '#1a1a2e'
    : line.dirty
      ? '#444400'
      : '#004422';

  return (
    <motion.div
      className="rounded-sm border"
      style={{
        width: 14,
        height: 14,
        backgroundColor: color,
        borderColor: line.valid ? '#333' : '#1a1a2e',
      }}
      initial={{ scale: 0 }}
      animate={{ scale: 1, backgroundColor: color }}
      transition={{ duration: 0.2, delay: (index % 32) * 0.01 }}
      title={`Line ${index}: tag=${line.tag}, valid=${line.valid}, dirty=${line.dirty}`}
    />
  );
}

export default function CacheHeatmap({ cache, label }: CacheHeatmapProps) {
  if (!cache) {
    return (
      <div className="glass-panel p-4 flex items-center justify-center text-gray-600 font-mono text-xs">
        No cache data
      </div>
    );
  }

  const cols = 16;
  const rows = Math.ceil(cache.lines.length / cols);

  return (
    <div className="glass-panel p-3 flex flex-col h-full">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-cyber-cyan font-mono font-bold">{label}</span>
        <div className="flex gap-3 text-[9px] font-mono text-gray-500">
          <span>Hits: <span className="text-cyber-cyan">{cache.hits}</span></span>
          <span>Misses: <span className="text-cyber-red">{cache.misses}</span></span>
          <span>Rate: <span className="text-cyber-neon">{(cache.hit_rate * 100).toFixed(0)}%</span></span>
        </div>
      </div>
      <div className="flex-1 flex flex-col justify-center">
        <div className="grid gap-0.5" style={{ gridTemplateColumns: `repeat(${cols}, 14px)` }}>
          {cache.lines.map((line, i) => (
            <CacheCell key={i} line={line} index={i} />
          ))}
        </div>
      </div>
      <div className="flex gap-4 mt-2 text-[9px] font-mono text-gray-600">
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#004422]" /> Valid</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#444400]" /> Dirty</span>
        <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded-sm bg-[#1a1a2e]" /> Invalid</span>
      </div>
    </div>
  );
}
