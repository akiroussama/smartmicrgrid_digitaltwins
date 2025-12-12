"""
Dashboard Components for Digital Twin Visualization

This package contains all visualization and UI components for the
Microgrid Digital Twin dashboard.

Components:
- microgrid_schematic: Interactive SVG-style microgrid visualization
- realtime_charts: Rolling window charts for real-time data
- control_panel: Simulation controls and parameter tuning
- comparison_mode: U-CBF vs Baseline comparison
- educational_overlays: Thesis concept explanations

Author: Oussama AKIR
Institution: Sup'Com, University of Carthage, Tunisia
Date: December 2025
Version: 1.0.0
"""

# Microgrid Schematic
try:
    from .microgrid_schematic import (
        create_microgrid_schematic,
        create_battery_gauge,
        create_cbf_status_indicator,
        create_power_flow_arrows,
        DARK_THEME,
        LIGHT_THEME,
        ThemeMode,
        ColorPalette
    )
except ImportError:
    pass

# Realtime Charts
try:
    from .realtime_charts import (
        RealtimeChartManager,
        ChartConfig,
        CBFEventType,
        CBFEvent
    )
except ImportError:
    pass

# Control Panel
try:
    from .control_panel import (
        create_simulation_controls,
        create_scenario_selector,
        create_parameter_panel,
        create_perturbation_injector,
        create_metrics_display,
        create_export_controls,
        create_complete_control_panel,
        apply_control_panel_css,
        SimulationControlState,
        UCBFParameters,
        PerturbationConfig,
        PerturbationType,
        ScenarioType,
        SCENARIO_INFO,
        PERTURBATION_INFO
    )
except ImportError:
    pass

# Comparison Mode
try:
    from .comparison_mode import (
        ComparisonEngine,
        ComparisonState,
        ComparisonStats,
        create_voltage_comparison_chart,
        create_soc_comparison_chart,
        create_barrier_chart,
        create_comparison_summary_chart,
        render_comparison_metrics,
        render_comparison_charts,
        render_comparison_mode
    )
except ImportError:
    pass

# Educational Overlays
try:
    from .educational_overlays import (
        Concept,
        ConceptLevel,
        THESIS_CONCEPTS,
        create_cbf_visualization,
        create_uncertainty_visualization,
        render_concept_card,
        render_education_panel,
        render_quick_reference,
        render_theorem_cards
    )
except ImportError:
    pass

__version__ = '1.0.0'
__author__ = 'Oussama AKIR'
