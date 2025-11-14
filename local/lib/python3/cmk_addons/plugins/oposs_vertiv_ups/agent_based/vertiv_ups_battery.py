#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Manuel Oetiker <manuel@oetiker.ch>
# License: GNU General Public License v2

"""
Vertiv/Liebert UPS Battery Monitoring
Monitors battery charge, temperature, runtime, voltage, and alarms
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


def discover_vertiv_ups_battery(section: Dict[str, Any]) -> DiscoveryResult:
    """
    Discover battery service if battery data is available.

    Args:
        section: Parsed UPS data from vertiv_ups section

    Yields:
        Service if battery metrics are present
    """
    if section and "battery_charge" in section:
        yield Service()


def check_vertiv_ups_battery(
    params: Mapping[str, Any],
    section: Dict[str, Any],
) -> CheckResult:
    """
    Check battery status and metrics.

    Monitors:
    - Battery charge percentage
    - Battery temperature
    - Estimated runtime
    - Battery voltage and current
    - Battery-related alarms

    Args:
        params: Check parameters with thresholds
        section: Parsed UPS data

    Yields:
        Result and Metric objects
    """
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from UPS")
        return

    # Check battery charge percentage
    battery_charge = section.get("battery_charge")
    if battery_charge is not None:
        yield from check_levels(
            battery_charge,
            levels_lower=params.get("battery_charge_lower"),
            metric_name="battery_charge",
            label="Battery charge",
            render_func=render.percent,
            boundaries=(0, 100),
        )
    else:
        yield Result(state=State.UNKNOWN, summary="Battery charge data unavailable")

    # Check battery temperature
    battery_temp = section.get("battery_temperature")
    if battery_temp is not None and battery_temp > 0:
        yield from check_levels(
            battery_temp,
            levels_upper=params.get("battery_temperature_upper"),
            metric_name="battery_temperature",
            label="Battery temperature",
            render_func=lambda t: f"{t:.1f} °C",
        )

    # Check battery runtime
    battery_runtime = section.get("battery_runtime_seconds")
    if battery_runtime is not None and battery_runtime > 0:
        yield from check_levels(
            battery_runtime,
            levels_lower=params.get("battery_runtime_lower"),
            metric_name="battery_runtime",
            label="Estimated runtime",
            render_func=render.timespan,
        )

    # Battery voltage (informational)
    yield from yield_informational_metric(
        section, "battery_voltage", "battery_voltage",
        "Battery voltage", lambda v: f"{v:.1f} V"
    )

    # Battery current (informational)
    yield from yield_informational_metric(
        section, "battery_current", "battery_current",
        "Battery current", lambda a: f"{a:.1f} A"
    )

    # Battery replacement date (informational)
    battery_replacement_date = section.get("battery_replacement_date")
    if battery_replacement_date:
        yield Result(
            state=State.OK,
            notice=f"Last battery replacement: {battery_replacement_date}"
        )

    # Check battery alarms using declarative definitions
    BATTERY_ALARMS = [
        ("alarm_battery_low", State.CRIT, "ALARM: Battery low!"),
        ("alarm_battery_temp", State.CRIT, "ALARM: Battery temperature critical!"),
        ("alarm_battery_discharging", State.WARN, "ALARM: Battery discharging!"),
        ("alarm_replace_battery", State.WARN, "ALARM: Replace battery!"),
    ]
    yield from check_alarms(section, BATTERY_ALARMS)


check_plugin_vertiv_ups_battery = CheckPlugin(
    name="vertiv_ups_battery",
    service_name="Vertiv UPS Battery",
    sections=["vertiv_ups"],
    discovery_function=discover_vertiv_ups_battery,
    check_function=check_vertiv_ups_battery,
    check_ruleset_name="vertiv_ups_battery",
    check_default_parameters={
        "battery_charge_lower": ("fixed", (20.0, 10.0)),  # WARN at 20%, CRIT at 10%
        "battery_temperature_upper": ("fixed", (30.0, 35.0)),  # WARN at 30°C, CRIT at 35°C
        "battery_runtime_lower": ("fixed", (600.0, 300.0)),  # WARN at 10min, CRIT at 5min
    },
)
