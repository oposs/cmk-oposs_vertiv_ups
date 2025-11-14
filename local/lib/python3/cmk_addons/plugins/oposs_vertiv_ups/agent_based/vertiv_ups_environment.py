#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Manuel Oetiker <manuel@oetiker.ch>
# License: GNU General Public License v2

"""
Vertiv/Liebert UPS Environment Monitoring
Monitors ambient temperature and environmental conditions
"""

from typing import Any, Dict, Mapping

from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    check_levels,
    render,
)


def discover_vertiv_ups_environment(section: Dict[str, Any]) -> DiscoveryResult:
    """
    Discover environment service if environmental data is available.

    Args:
        section: Parsed UPS data from vertiv_ups section

    Yields:
        Service if environmental metrics are present
    """
    if section and "ambient_temperature" in section:
        ambient_temp = section.get("ambient_temperature", 0)
        if ambient_temp > 0:  # Only discover if we have valid temperature data
            yield Service()


def check_vertiv_ups_environment(
    params: Mapping[str, Any],
    section: Dict[str, Any],
) -> CheckResult:
    """
    Check environmental conditions.

    Monitors:
    - Ambient/inlet air temperature

    Args:
        params: Check parameters with thresholds
        section: Parsed UPS data

    Yields:
        Result and Metric objects
    """
    if not section:
        yield Result(state=State.UNKNOWN, summary="No data from UPS")
        return

    # Check ambient temperature
    ambient_temp = section.get("ambient_temperature")
    if ambient_temp is not None and ambient_temp > 0:
        yield from check_levels(
            ambient_temp,
            levels_upper=params.get("ambient_temperature_upper"),
            metric_name="ambient_temperature",
            label="Inlet air temperature",
            render_func=lambda t: f"{t:.1f} °C",
        )
    else:
        yield Result(
            state=State.UNKNOWN,
            summary="Ambient temperature data unavailable"
        )


check_plugin_vertiv_ups_environment = CheckPlugin(
    name="vertiv_ups_environment",
    service_name="Vertiv UPS Environment",
    sections=["vertiv_ups"],
    discovery_function=discover_vertiv_ups_environment,
    check_function=check_vertiv_ups_environment,
    check_ruleset_name="vertiv_ups_environment",
    check_default_parameters={
        "ambient_temperature_upper": ("fixed", (35.0, 40.0)),  # WARN at 35°C, CRIT at 40°C
    },
)
