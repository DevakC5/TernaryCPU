// ── Pipeline ──────────────────────────────────────────────────────────
export interface PipelineStage {
  instruction: string;
  opcode: string;
  bubble: boolean;
  stalled: boolean;
}

export interface PipelineData {
  if_stage: PipelineStage;
  id_stage: PipelineStage;
  ex_stage: PipelineStage;
  mem_stage: PipelineStage;
  wb_stage: PipelineStage;
  total_instructions: number;
  stall_cycles: number;
  flush_count: number;
}

// ── Cache ─────────────────────────────────────────────────────────────
export interface CacheLine {
  tag: number;
  valid: boolean;
  dirty: boolean;
}

export interface CacheData {
  name: string;
  hits: number;
  misses: number;
  hit_rate: number;
  lines: CacheLine[];
}

// ── Branch Predictor ──────────────────────────────────────────────────
export interface BranchData {
  mode: string;
  predictions: number;
  mispredictions: number;
  accuracy: number;
  counters: Record<string, number>;
}

// ── Bus ───────────────────────────────────────────────────────────────
export interface BusData {
  transfers: number;
  pending: number;
  utilization: number;
  idle_cycles: number;
}

// ── DMA ───────────────────────────────────────────────────────────────
export interface DMAData {
  active: boolean;
  queued: number;
  completed_transfers: number;
  progress: number;
}

// ── Interrupts ────────────────────────────────────────────────────────
export interface InterruptData {
  pending: number;
  in_isr: boolean;
}

// ── Profiler ──────────────────────────────────────────────────────────
export interface ProfilerData {
  cycles: number;
  instructions: number;
  cpi: number;
  ipc: number;
  total_stalls: number;
  cache_hit_rate: number;
  branch_accuracy: number;
}

// ── System Snapshot ───────────────────────────────────────────────────
export interface SystemSnapshot {
  cycle: number;
  clock_cycle: number;
  pc: number;
  sp: number;
  halted: boolean;
  registers: Record<string, string>;
  flags: Record<string, boolean>;
  pipeline: PipelineData | null;
  icache: CacheData | null;
  dcache: CacheData | null;
  branch: BranchData | null;
  bus: BusData | null;
  dma: DMAData | null;
  interrupt: InterruptData | null;
  profiler: ProfilerData | null;
  current_instruction: string;
  instructions_loaded: number;
  timestamp: number;
}

// ── Demo ──────────────────────────────────────────────────────────────
export interface DemoEntry {
  name: string;
  source: string;
}

// ── WebSocket Messages ────────────────────────────────────────────────
export interface WsSnapshotMessage {
  type: 'snapshot';
  data: SystemSnapshot;
}

export interface WsStatusMessage {
  type: 'status';
  data: { connected: boolean; mode: string };
}

export interface WsLoadResultMessage {
  type: 'load_result';
  data: { success: boolean; message: string; labels?: Record<string, number>; instruction_count?: number; instructions?: string[] };
}

export interface WsDemosMessage {
  type: 'demos';
  data: DemoEntry[];
}

export type WsMessage = WsSnapshotMessage | WsStatusMessage | WsLoadResultMessage | WsDemosMessage;

// ── Execution Event (for timeline) ────────────────────────────────────
export interface ExecutionEvent {
  instr: string;
  stage_states: string[];
  cycle: number;
}
