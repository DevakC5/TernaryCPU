import { motion, AnimatePresence } from 'framer-motion';

interface RegistersProps {
  registers: Record<string, string>;
  flags: Record<string, boolean>;
  pc: number;
  sp: number;
}

function TritDigit({ digit, label }: { digit: string; label: string }) {
  return (
    <div className="flex flex-col items-center">
      <span className="text-[8px] text-gray-600 mb-0.5">{label}</span>
      <AnimatePresence mode="popLayout">
        <motion.span
          key={digit}
          initial={{ y: -12, opacity: 0, rotateX: 90 }}
          animate={{ y: 0, opacity: 1, rotateX: 0 }}
          exit={{ y: 12, opacity: 0, rotateX: -90 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className={`font-mono text-sm font-bold ${
            digit === '0' ? 'text-gray-500' :
            digit === '1' ? 'text-cyber-cyan' :
            'text-cyber-purple'
          }`}
        >
          {digit}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}

function TritRegister({ name, value }: { name: string; value: string }) {
  const digits = value.padStart(4, '0').slice(-4).split('');
  return (
    <div className="glass-panel px-2 py-1.5 flex items-center gap-2">
      <span className="text-[10px] text-gray-500 w-6">{name}</span>
      <div className="flex gap-0.5">
        {digits.map((d, i) => (
          <TritDigit key={`${name}-${i}`} digit={d} label={`t${i}`} />
        ))}
      </div>
    </div>
  );
}

export default function RegisterView({ registers, flags, pc, sp }: RegistersProps) {
  const flagEntries = Object.entries(flags);
  return (
    <div className="border-t border-cyber-navy/30 p-2">
      <div className="text-[10px] text-cyber-cyan font-mono mb-2">Registers</div>
      <div className="grid grid-cols-2 gap-1">
        {['R0', 'R1', 'R2', 'R3'].map(r => (
          <TritRegister key={r} name={r} value={registers[r] || '0'} />
        ))}
      </div>
      <div className="flex items-center gap-3 mt-2 text-[10px] font-mono">
        <span className="text-gray-600">PC: <span className="text-cyber-amber">{pc}</span></span>
        <span className="text-gray-600">SP: <span className="text-cyber-magenta">{sp}</span></span>
      </div>
      <div className="flex flex-wrap gap-1 mt-1.5">
        {flagEntries.map(([name, val]) => (
          <span
            key={name}
            className={`text-[9px] px-1.5 py-0.5 rounded font-mono ${
              val ? 'text-cyber-cyan bg-cyber-cyan/10' : 'text-gray-700'
            }`}
          >
            {name}
          </span>
        ))}
      </div>
    </div>
  );
}
