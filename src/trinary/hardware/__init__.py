"""Hardware simulation package — clock, pipeline, cache, bus, DMA, interrupts."""

from trinary.hardware.clock import Clock
from trinary.hardware.pipeline import Pipeline, PipelineStage
from trinary.hardware.hazards import HazardUnit
from trinary.hardware.cache import Cache, CacheLine
from trinary.hardware.branch_predictor import BranchPredictor
from trinary.hardware.bus import Bus, BusRequest
from trinary.hardware.dma import DMA, DMATransfer
from trinary.hardware.vram_controller import VRAMController
from trinary.hardware.interrupts import InterruptController
from trinary.hardware.profiler import Profiler
from trinary.hardware.timing import (
    INSTRUCTION_LATENCIES,
    get_latency,
    is_branch, is_load, is_store, is_tensor_op,
    reads_registers, writes_registers,
)

__all__ = [
    "Clock",
    "Pipeline",
    "PipelineStage",
    "HazardUnit",
    "Cache",
    "CacheLine",
    "BranchPredictor",
    "Bus",
    "BusRequest",
    "DMA",
    "DMATransfer",
    "VRAMController",
    "InterruptController",
    "Profiler",
    "INSTRUCTION_LATENCIES",
    "get_latency",
    "is_branch", "is_load", "is_store", "is_tensor_op",
    "reads_registers", "writes_registers",
]
