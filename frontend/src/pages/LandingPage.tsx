import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const TRITS = ['0', '1', '2'];
const FLOATING_COUNT = 30;

function randomTrit() { return TRITS[Math.floor(Math.random() * 3)]; }

interface FloatingTrit {
  id: number;
  x: number;
  y: number;
  value: string;
  speed: number;
  size: number;
  opacity: number;
  delay: number;
}

function FloatingTrits() {
  const [trits, setTrits] = useState<FloatingTrit[]>([]);
  useEffect(() => {
    const items: FloatingTrit[] = Array.from({ length: FLOATING_COUNT }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      value: randomTrit(),
      speed: 0.5 + Math.random() * 2,
      size: 10 + Math.random() * 20,
      opacity: 0.05 + Math.random() * 0.15,
      delay: Math.random() * 5,
    }));
    setTrits(items);
    const interval = setInterval(() => {
      setTrits(prev => prev.map(t => ({
        ...t,
        value: Math.random() > 0.97 ? randomTrit() : t.value,
        y: t.y - 0.1 * t.speed,
        x: t.x + Math.sin(Date.now() / 3000 + t.id) * 0.05,
        ...(t.y < -10 ? { y: 110, x: Math.random() * 100 } : {}),
      })));
    }, 100);
    return () => clearInterval(interval);
  }, []);
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {trits.map(t => (
        <div
          key={t.id}
          className="absolute font-mono text-cyber-cyan select-none"
          style={{
            left: `${t.x}%`,
            top: `${t.y}%`,
            fontSize: `${t.size}px`,
            opacity: t.opacity,
            transform: `translate(-50%, -50%)`,
            transition: 'all 0.1s linear',
          }}
        >{t.value}</div>
      ))}
    </div>
  );
}

function AnimatedDatapath() {
  return (
    <svg className="absolute inset-0 w-full h-full pointer-events-none z-[1]" viewBox="0 0 1200 800" preserveAspectRatio="xMidYMid slice">
      <defs>
        <linearGradient id="glow-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#00ff88" stopOpacity="0" />
          <stop offset="50%" stopColor="#00ff88" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#00ff88" stopOpacity="0" />
        </linearGradient>
        <filter id="glow">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      {[1, 2, 3, 4, 5].map(i => (
        <motion.path
          key={i}
          d={`M ${i * 200},0 Q ${i * 200 + 50},${i * 80} ${i * 200 + 100},${i * 120} T ${i * 200},800`}
          stroke="#00ff88"
          strokeWidth="1"
          fill="none"
          opacity={0.15 / i}
          strokeDasharray="4 8"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 3, delay: i * 0.3, repeat: Infinity, ease: 'linear' }}
        />
      ))}
      <motion.circle
        cx="600" cy="400" r="80"
        fill="none" stroke="#8888ff" strokeWidth="2"
        animate={{ scale: [1, 1.05, 1], opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 3, repeat: Infinity }}
      />
    </svg>
  );
}

export default function LandingPage() {
  const navigate = useNavigate();
  const [glitch, setGlitch] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setGlitch(true);
      setTimeout(() => setGlitch(false), 100);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="relative min-h-screen bg-cyber-dark overflow-hidden">
      <FloatingTrits />
      <AnimatedDatapath />

      {/* Scanline overlay */}
      <div className="crt-overlay" />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6">
        <motion.div
          className="text-center max-w-4xl"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        >
          {/* Badge */}
          <motion.div
            className="inline-block mb-6 px-4 py-1 rounded-full border border-cyber-cyan/30 text-cyber-cyan text-xs font-mono tracking-wider"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            BASE-3 COMPUTER ARCHITECTURE SIMULATOR
          </motion.div>

          {/* Title */}
          <motion.h1
            className={`text-7xl md:text-9xl font-display font-bold mb-4 transition-all duration-100 ${glitch ? 'translate-x-1' : ''}`}
            style={{
              background: 'linear-gradient(135deg, #00ff88 0%, #8888ff 50%, #ff4488 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textShadow: glitch ? '2px 0 #ff4488, -2px 0 #00ff88' : 'none',
            }}
          >
            TernaryCPU
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            className="text-xl md:text-2xl text-gray-400 font-mono mb-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            A Full Ternary Computer Architecture Simulator
          </motion.p>

          {/* Architecture layer badges */}
          <motion.div
            className="flex flex-wrap justify-center gap-3 mb-12"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
          >
            {['5-Stage Pipeline', 'Cache Coherence', 'Branch Prediction', 'DMA Controller', 'GPU Core', 'Tensor Accelerator'].map((tag, i) => (
              <span key={tag} className="px-3 py-1 text-xs font-mono border border-cyber-navy rounded-full text-gray-500">
                {tag}
              </span>
            ))}
          </motion.div>

          {/* Buttons */}
          <motion.div
            className="flex flex-wrap justify-center gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.5 }}
          >
            <button
              onClick={() => navigate('/simulator')}
              className="cyber-button primary text-lg px-8 py-3"
            >
              Launch Simulator
            </button>
            <a
              href="https://github.com/devakchaudhari/Trinary"
              target="_blank"
              rel="noopener noreferrer"
              className="cyber-button text-lg px-8 py-3"
            >
              GitHub
            </a>
          </motion.div>
        </motion.div>

        {/* Bottom architecture preview */}
        <motion.div
          className="absolute bottom-8 left-0 right-0 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2 }}
        >
          <div className="flex justify-center items-end gap-1">
            {['IF', 'ID', 'EX', 'MEM', 'WB'].map((stage, i) => (
              <motion.div
                key={stage}
                className={`stage-box stage-${stage.toLowerCase()} px-3 py-1`}
                animate={{ opacity: [0.3, 0.6, 0.3] }}
                transition={{ duration: 2, delay: i * 0.3, repeat: Infinity }}
              >
                <span className="text-[8px] text-gray-500">{stage}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
