import { useRef, useEffect } from 'react';
import { DemoEntry } from '../types';

interface AssemblyEditorProps {
  source: string;
  onChange: (val: string) => void;
  demos: DemoEntry[];
  onDemoSelect: (name: string) => void;
  onLoad: () => void;
  loadResult: { success: boolean; message: string } | null;
  pc: number;
  instructions?: string[];
}

export default function AssemblyEditor({ source, onChange, demos, onDemoSelect, onLoad, loadResult, pc, instructions }: AssemblyEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-2 border-b border-cyber-navy/30">
        <span className="text-xs text-cyber-cyan font-mono">Assembly Editor</span>
        <div className="flex items-center gap-2">
          <select
            onChange={e => onDemoSelect(e.target.value)}
            className="bg-cyber-dark text-gray-400 text-[10px] border border-cyber-navy/30 rounded px-2 py-1 w-28"
          >
            <option value="">Select demo...</option>
            {demos.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
          </select>
          <button onClick={onLoad} className="cyber-button text-[10px] px-2 py-1">
            Load
          </button>
        </div>
      </div>
      <textarea
        ref={textareaRef}
        value={source}
        onChange={e => onChange(e.target.value)}
        className="flex-1 bg-transparent text-cyber-cyan font-mono text-xs p-3 resize-none outline-none border-none focus:ring-0"
        style={{ caretColor: '#00ff88' }}
        spellCheck={false}
      />
      {loadResult && (
        <div className={`px-3 py-1 text-[10px] font-mono border-t border-cyber-navy/30 ${loadResult.success ? 'text-cyber-cyan' : 'text-cyber-red'}`}>
          {loadResult.message}
        </div>
      )}
    </div>
  );
}
