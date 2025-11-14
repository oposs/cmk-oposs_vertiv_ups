#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Manuel Oetiker <manuel@oetiker.ch>
# License: GNU General Public License v2

"""
Vertiv/Liebert UPS Power Monitoring
Monitors input/output power, voltage, current, frequency, and load
"""

from typing import Any, Callable, Dict, List, Mapping, Tuple

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    Metric,
    check_levels,
    render,
)


# ============================================================================
# Helper Functions (DRY improvements)
# ============================================================================

def yield_informational_metric(
    section: Dict[str, Any],
    key: str,
    metric_name: str,
    label: str,
    render_func: Callable[[float], str],
    min_value: float = 0.0,
) -> CheckResult:
    """
    Yield metric and notice for informational values.

    This helper eliminates repetitive code for simple metric reporting.

    Args:
        section: Parsed UPS data
        key: Key to look up in section
        metric_name: Metric name for CheckMK
        label: Human-readable label for the notice
        render_func: Function to format the value for display
        min_value: Minimum value to report (values <= this are skipped)

    Yields:
        Metric and Result objects
    """
    value = section.get(key)
    if value is not None and value > min_value:
        yield Metric(metric_name, value)
        yield Result(
            state=State.OK,
            notice=f"{label}: {render_func(value)}"
        )


def check_alarms(
    section: Dict[str, Any],
    alarm_definitions: List[Tuple[str, State, str]]
) -> CheckResult:
    """
    Check multiple alarms using declarative definitions.

    This helper eliminates repetitive alarm checking code.

    Args:
        section: Parsed UPS data
        alarm_definitions: List of (alarm_key, state, message) tuples

    Yields:
        Result objects for active alarms
    """
    for alarm_key, alarm_state, alarm_message in alarm_definitions:
        if section.get(alarm_key, 0) > 0:
            yield Result(state=alarm_state, summary=alarm_message)


def discover_vertiv_ups_power(section: Dict[str, Any]) -> DiscoveryResult:
    """
    Discover power service if power data is available.

    Args:
        section: Parsed UPS data from vertiv_ups section

    Yields:
        Service if power metrics are present
    """
    if section and ("output_load" in section or "output_voltage" in section):
        yield Service()


def check_vertiv_ups_power(
    params: Mapping[str, Any],
    section: Dict[str, Any],
) -> CheckResult:
    """
    Check power status and metrics.

    Monitors:
    - System status (normal, on battery, bypass, etc.)
    - Output load percentage
    - Input/output voltage and frequency
    - Output power and current
    - Power-related alarms

    Args:
        params: Check parameters with thresholds
        section: Parsed UPS data

    Yields:
        Result and Metric objects
    """
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from UPS")
        return

    # System status - use output_source as fallback for more reliable detection
    system_status = section.get("system_status", "unknown")
    output_source = section.get("output_source", "")

    # Determine actual operational state
    # ECO mode (bypass) is normal operation, not a warning condition
    if system_status == "normal":
        status_state = State.OK
        status_text = "normal"
    elif system_status == "on_bypass" or output_source == "bypass":
        # Bypass/ECO mode is normal operation for efficiency
        status_state = State.OK
        status_text = "bypass (ECO mode)" if output_source == "bypass" else "on bypass"
    elif system_status == "on_battery":
        status_state = State.WARN
        status_text = "on battery"
    elif system_status in ["shutdown"]:
        status_state = State.CRIT
        status_text = system_status
    elif system_status == "startup":
        status_state = State.OK
        status_text = "startup"
    elif system_status == "unknown" and output_source in ["normal", "bypass"]:
        # If system_status is unknown but output_source indicates normal operation
        status_state = State.OK
        status_text = f"operating ({output_source} mode)"
    else:
        # Truly unknown status
        status_state = State.UNKNOWN
        status_text = f"{system_status} (please verify)"

    yield Result(
        state=status_state,
        summary=f"System status: {status_text}"
    )

    # ECO mode information (already shown in status, provide as detail)
    eco_state = section.get("eco_mode_state", 0)
    eco_status = section.get("eco_mode_status", 0)
    if output_source == "bypass" and (eco_state > 0 or eco_status > 0):
        yield Result(
            state=State.OK,
            notice="ECO mode enabled for energy efficiency"
        )

    # Output load percentage (critical metric)
    output_load = section.get("output_load")
    if output_load is not None:
        yield from check_levels(
            output_load,
            levels_upper=params.get("output_load_upper"),
            metric_name="output_load",
            label="Output load",
            render_func=render.percent,
            boundaries=(0, 100),
        )
    else:
        yield Result(state=State.UNKNOWN, notice="Output load data unavailable")

    # Output power (watts)
    yield from yield_informational_metric(
        section, "output_power", "output_power",
        "Output power", lambda w: f"{w:.0f} W"
    )

    # Output voltage
    output_voltage = section.get("output_voltage")
    if output_voltage is not None and output_voltage > 0:
        yield from check_levels(
            output_voltage,
            levels_upper=params.get("output_voltage_upper"),
            levels_lower=params.get("output_voltage_lower"),
            metric_name="output_voltage",
            label="Output voltage",
            render_func=lambda v: f"{v:.1f} V",
        )

    # Output current
    yield from yield_informational_metric(
        section, "output_current", "output_current",
        "Output current", lambda a: f"{a:.1f} A"
    )

    # Output frequency
    output_frequency = section.get("output_frequency")
    if output_frequency is not None and output_frequency > 0:
        yield from check_levels(
            output_frequency,
            levels_upper=params.get("output_frequency_upper"),
            levels_lower=params.get("output_frequency_lower"),
            metric_name="output_frequency",
            label="Output frequency",
            render_func=lambda f: f"{f:.1f} Hz",
        )

    # Input metrics
    yield from yield_informational_metric(
        section, "input_voltage", "input_voltage",
        "Input voltage", lambda v: f"{v:.1f} V"
    )
    yield from yield_informational_metric(
        section, "input_voltage_max", "input_voltage_max",
        "Input voltage max", lambda v: f"{v:.1f} V"
    )
    yield from yield_informational_metric(
        section, "input_voltage_min", "input_voltage_min",
        "Input voltage min", lambda v: f"{v:.1f} V"
    )
    yield from yield_informational_metric(
        section, "input_current", "input_current",
        "Input current", lambda a: f"{a:.1f} A"
    )
    yield from yield_informational_metric(
        section, "input_frequency", "input_frequency",
        "Input frequency", lambda f: f"{f:.1f} Hz"
    )
    yield from yield_informational_metric(
        section, "input_power_factor", "input_power_factor",
        "Input power factor", lambda pf: f"{pf:.2f}"
    )

    # Input blackout count (special handling - allow zero)
    blackout_count = section.get("input_blackout_count")
    if blackout_count is not None:
        yield Metric("input_blackout_count", blackout_count)
        if blackout_count > 0:
            yield Result(
                state=State.OK,
                notice=f"Blackout count: {blackout_count}"
            )

    # Output power metrics
    yield from yield_informational_metric(
        section, "output_apparent_power", "output_apparent_power",
        "Output apparent power", lambda va: f"{va:.0f} VA"
    )
    yield from yield_informational_metric(
        section, "output_power_factor", "output_power_factor",
        "Output power factor", lambda pf: f"{pf:.2f}"
    )
    yield from yield_informational_metric(
        section, "output_apparent_power_rating", "output_apparent_power_rating",
        "Rated power", lambda va: f"{va:.0f} VA"
    )

    # Check power alarms using declarative definitions
    POWER_ALARMS = [
        ("alarm_input_problem", State.WARN, "ALARM: Input power problem detected!"),
        ("alarm_overload", State.CRIT, "ALARM: Output overload!"),
        ("alarm_bypass_not_available", State.WARN, "ALARM: Bypass not available!"),
        ("alarm_output_off", State.CRIT, "ALARM: System output off!"),
        ("alarm_inverter_failure", State.CRIT, "ALARM: Inverter failure!"),
    ]
    yield from check_alarms(section, POWER_ALARMS)


check_plugin_vertiv_ups_power = CheckPlugin(
    name="vertiv_ups_power",
    service_name="Vertiv UPS Power",
    sections=["vertiv_ups"],
    discovery_function=discover_vertiv_ups_power,
    check_function=check_vertiv_ups_power,
    check_ruleset_name="vertiv_ups_power",
    check_default_parameters={
        "output_load_upper": ("fixed", (80.0, 90.0)),  # WARN at 80%, CRIT at 90%
        # Voltage thresholds disabled by default - configure based on your nominal voltage
        # For 230V systems: upper=(253.0, 265.0), lower=(207.0, 195.0)
        # For 120V systems: upper=(132.0, 138.0), lower=(108.0, 102.0)
        "output_frequency_upper": ("fixed", (52.0, 53.0)),  # WARN at 52Hz, CRIT at 53Hz (50Hz nominal)
        "output_frequency_lower": ("fixed", (48.0, 47.0)),  # WARN at 48Hz, CRIT at 47Hz
    },
)
