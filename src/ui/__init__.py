from .sidebar import render_sidebar
from .price_chart import render_main_chart
from .stats_panels import render_stats_panels
from .state_monitor import render_state_monitor
from .theme import inject_institutional_theme, STRATEGY_LABELS_PT, get_friendly_label
from .radar_tab import render_radar_tab
from .simulator_tab import render_simulator_fragment
from .guide_tab import render_guide_tab

__all__ = [
    "render_sidebar",
    "render_main_chart",
    "render_stats_panels",
    "render_state_monitor",
    "inject_institutional_theme",
    "STRATEGY_LABELS_PT",
    "get_friendly_label",
    "render_radar_tab",
    "render_simulator_fragment",
    "render_guide_tab",
]
