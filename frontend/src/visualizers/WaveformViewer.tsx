import { useRef, useState, useEffect } from 'react';

interface WaveformViewerProps {
  signals: Record<string, number[]>;
}

const SIGNAL_COLORS: Record<string, string> = {
  clk: '#00ff88',
  pc: '#ffcc00',
  sp: '#ff8844',
  halted: '#ff4444',
  cache_hit: '#4488ff',
  branch_taken: '#8888ff',
  int: '#ff4488',
  dma: '#ff8844',
  bus: '#44aaff',
};

export default function WaveformViewer({ signals }: WaveformViewerProps) {
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);
  const signalNames = Object.keys(signals);

  const colW = 20 * zoom;
  const rowH = 28;
  const labelW = 80;
  const totalCycles = Math.max(...signalNames.map(n => signals[n]?.length || 0), 0);
  const cyclesToShow = 40;

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const handler = (e: WheelEvent) => {
      if (e.ctrlKey) {
        e.preventDefault();
        setZoom(z => Math.max(0.4, Math.min(5, z - e.deltaY * 0.01)));
      } else {
        setOffset(o => Math.max(0, Math.min(totalCycles - 10, o + (e.deltaY > 0 ? 1 : -1))));
      }
    };
    el.addEventListener('wheel', handler, { passive: false });
    return () => el.removeEventListener('wheel', handler);
  }, [totalCycles]);

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-cyber-cyan font-mono font-bold">Signal Waveform</span>
        <div className="flex items-center gap-2 text-[10px] font-mono text-gray-500">
          <span>Zoom:</span>
          <input type="range" min="40" max="300" value={zoom * 100}
            onChange={e => setZoom(Number(e.target.value) / 100)} className="w-20" />
        </div>
      </div>
      <div ref={containerRef} className="flex-1 glass-panel overflow-auto">
        <div style={{ minWidth: labelW + cyclesToShow * colW }}>
          {/* Header */}
          <div className="sticky top-0 z-10 flex" style={{ background: '#0a0a1a', height: 24, borderBottom: '1px solid #0f3460' }}>
            <div style={{ width: labelW }} />
            {Array.from({ length: cyclesToShow }, (_, i) => (
              <div key={i} className="flex-shrink-0 flex items-center justify-center text-[9px] font-mono text-gray-600" style={{ width: colW }}>
                {offset + i}
              </div>
            ))}
          </div>
          {/* Rows */}
          {signalNames.map(name => {
            const values = signals[name] || [];
            const color = SIGNAL_COLORS[name] || '#00ff88';
            return (
              <div key={name} style={{ height: rowH, display: 'flex', alignItems: 'center', borderBottom: '1px solid #0a0a1a' }}>
                <div className="flex-shrink-0 flex items-center px-2 text-[10px] font-mono font-bold" style={{ width: labelW, color }}>
                  {name}
                </div>
                <div className="flex" style={{ height: rowH }}>
                  {Array.from({ length: cyclesToShow }, (_, ci) => {
                    const idx = offset + ci;
                    const val = idx < values.length ? values[idx] : 0;
                    const isHigh = val > 0;
                    const midY = rowH / 2;
                    if (name === 'clk') {
                      const halfW = Math.max(colW / 2, 4);
                      return (
                        <div key={ci} style={{ width: colW, height: rowH, position: 'relative' }}>
                          <svg width={colW} height={rowH}>
                            <line x1={0} y1={midY - 6} x2={halfW} y2={midY - 6} stroke={isHigh ? color : '#333'} strokeWidth={1.5} />
                            <line x1={halfW} y1={midY - 6} x2={halfW} y2={midY + 6} stroke={isHigh ? color : '#333'} strokeWidth={1.5} />
                            <line x1={halfW} y1={midY + 6} x2={colW} y2={midY + 6} stroke={isHigh ? color : '#333'} strokeWidth={1.5} />
                          </svg>
                        </div>
                      );
                    }
                    return (
                      <div key={ci} style={{ width: colW, height: rowH, display: 'flex', alignItems: 'center', justifyContent: 'center', borderLeft: '1px solid #0f346020' }}>
                        <div style={{ width: colW - 4, height: isHigh ? 8 : 2, borderRadius: 1, backgroundColor: isHigh ? color : '#333' }} />
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
          {signalNames.length === 0 && (
            <div className="flex items-center justify-center h-32 text-gray-600 font-mono text-xs">No signal data</div>
          )}
        </div>
      </div>
    </div>
  );
}
