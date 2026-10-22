"""
Multi-Asset Portfolio Manager, Rebalancing Advisor & Historical Simulator Engine.
Provides deterministic Potential Score (0-100) evaluation per asset based on
its historical Champion Strategy Pair, actionable Today's Rebalancing Plan,
and Zero Look-Ahead Bias bar-by-bar multi-asset portfolio simulation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import math
import numpy as np
import pandas as pd

from ..strategies.base import OHLCVSeries, SignalRecord
from .accumulation_simulator import optimize_strategy_pairs
from .statistical_engine import evaluate_all_strategies
from .timing_classifier import classify_timing_status
