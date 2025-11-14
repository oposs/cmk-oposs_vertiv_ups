#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Manuel Oetiker <manuel@oetiker.ch>
# License: GNU General Public License v2

"""
Vertiv/Liebert UPS Graphing Definitions
Metrics, graphs, and perfometers for UPS monitoring
"""

from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import (
    Color,
    DecimalNotation,
    TimeNotation,
    Metric,
    Unit,
)
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.perfometers import Perfometer, FocusRange, Closed


# ============================================================================
# Unit Definitions
# ============================================================================

unit_percentage = Unit(DecimalNotation("%"))
unit_celsius = Unit(DecimalNotation("°C"))
unit_volts = Unit(DecimalNotation("V"))
unit_amperes = Unit(DecimalNotation("A"))
unit_watts = Unit(DecimalNotation("W"))
unit_hertz = Unit(DecimalNotation("Hz"))
unit_seconds = Unit(TimeNotation())


# ============================================================================
# Battery Metrics
# ============================================================================

metric_battery_charge = Metric(
    name="battery_charge",
    title=Title("Battery charge"),
    unit=unit_percentage,
    color=Color.GREEN,
)

metric_battery_temperature = Metric(
    name="battery_temperature",
    title=Title("Battery temperature"),
    unit=unit_celsius,
    color=Color.ORANGE,
)

metric_battery_runtime = Metric(
    name="battery_runtime",
    title=Title("Battery runtime"),
    unit=unit_seconds,
    color=Color.BLUE,
)

metric_battery_voltage = Metric(
    name="battery_voltage",
    title=Title("Battery voltage"),
    unit=unit_volts,
    color=Color.PURPLE,
)

metric_battery_current = Metric(
    name="battery_current",
    title=Title("Battery current"),
    unit=unit_amperes,
    color=Color.CYAN,
)


# ============================================================================
# Power Metrics
# ============================================================================

metric_output_load = Metric(
    name="output_load",
    title=Title("Output load"),
    unit=unit_percentage,
    color=Color.BLUE,
)

metric_output_power = Metric(
    name="output_power",
    title=Title("Output power"),
    unit=unit_watts,
    color=Color.PURPLE,
)

metric_output_voltage = Metric(
    name="output_voltage",
    title=Title("Output voltage"),
    unit=unit_volts,
    color=Color.GREEN,
)

metric_output_current = Metric(
    name="output_current",
    title=Title("Output current"),
    unit=unit_amperes,
    color=Color.CYAN,
)

metric_output_frequency = Metric(
    name="output_frequency",
    title=Title("Output frequency"),
    unit=unit_hertz,
    color=Color.ORANGE,
)

metric_output_apparent_power = Metric(
    name="output_apparent_power",
    title=Title("Output apparent power"),
    unit=Unit(DecimalNotation("VA")),
    color=Color.DARK_PURPLE,
)

metric_output_power_factor = Metric(
    name="output_power_factor",
    title=Title("Output power factor"),
    unit=Unit(DecimalNotation("")),
    color=Color.DARK_BLUE,
)

metric_output_apparent_power_rating = Metric(
    name="output_apparent_power_rating",
    title=Title("Output power rating"),
    unit=Unit(DecimalNotation("VA")),
    color=Color.DARK_GRAY,
)

metric_input_voltage = Metric(
    name="input_voltage",
    title=Title("Input voltage"),
    unit=unit_volts,
    color=Color.LIGHT_GREEN,
)

metric_input_voltage_max = Metric(
    name="input_voltage_max",
    title=Title("Input voltage max"),
    unit=unit_volts,
    color=Color.DARK_GREEN,
)

metric_input_voltage_min = Metric(
    name="input_voltage_min",
    title=Title("Input voltage min"),
    unit=unit_volts,
    color=Color.BROWN,
)

metric_input_current = Metric(
    name="input_current",
    title=Title("Input current"),
    unit=unit_amperes,
    color=Color.LIGHT_CYAN,
)

metric_input_frequency = Metric(
    name="input_frequency",
    title=Title("Input frequency"),
    unit=unit_hertz,
    color=Color.LIGHT_ORANGE,
)

metric_input_power_factor = Metric(
    name="input_power_factor",
    title=Title("Input power factor"),
    unit=Unit(DecimalNotation("")),
    color=Color.LIGHT_BLUE,
)

metric_input_blackout_count = Metric(
    name="input_blackout_count",
    title=Title("Input blackout count"),
    unit=Unit(DecimalNotation("")),
    color=Color.DARK_RED,
)


# ============================================================================
# Environmental Metrics
# ============================================================================

metric_ambient_temperature = Metric(
    name="ambient_temperature",
    title=Title("Ambient temperature"),
    unit=unit_celsius,
    color=Color.RED,
)


# ============================================================================
# Graphs
# ============================================================================

graph_battery_charge = Graph(
    name="battery_charge",
    title=Title("Battery Charge"),
    simple_lines=["battery_charge"],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,
    ),
)

graph_battery_runtime = Graph(
    name="battery_runtime",
    title=Title("Battery Runtime"),
    simple_lines=["battery_runtime"],
)

graph_battery_temperature = Graph(
    name="battery_temperature",
    title=Title("Battery Temperature"),
    simple_lines=["battery_temperature"],
)

graph_battery_electrical = Graph(
    name="battery_electrical",
    title=Title("Battery Electrical"),
    simple_lines=["battery_voltage", "battery_current"],
    optional=["battery_current"],
)

graph_output_load = Graph(
    name="output_load",
    title=Title("UPS Output Load"),
    simple_lines=["output_load"],
    minimal_range=MinimalRange(
        lower=0,
        upper=100,
    ),
)

graph_output_power = Graph(
    name="output_power",
    title=Title("UPS Output Power (Watts)"),
    simple_lines=["output_power"],
)

graph_output_apparent_power = Graph(
    name="output_apparent_power",
    title=Title("UPS Output Apparent Power (VA)"),
    simple_lines=["output_apparent_power"],
)

graph_output_power_factor = Graph(
    name="output_power_factor",
    title=Title("UPS Power Factor"),
    simple_lines=["input_power_factor", "output_power_factor"],
    optional=["input_power_factor"],
)

graph_output_voltage = Graph(
    name="output_voltage",
    title=Title("Output Voltage"),
    simple_lines=["output_voltage"],
)

graph_output_current = Graph(
    name="output_current",
    title=Title("Output Current"),
    simple_lines=["output_current"],
)

graph_frequency = Graph(
    name="ups_frequency",
    title=Title("UPS Frequency"),
    simple_lines=["input_frequency", "output_frequency"],
    optional=["input_frequency"],
)

graph_voltage_comparison = Graph(
    name="voltage_comparison",
    title=Title("Input vs Output Voltage"),
    simple_lines=["input_voltage", "output_voltage"],
    optional=["input_voltage"],
)

graph_input_voltage_statistics = Graph(
    name="input_voltage_statistics",
    title=Title("Input Voltage Statistics"),
    simple_lines=["input_voltage", "input_voltage_max", "input_voltage_min"],
    optional=["input_voltage_max", "input_voltage_min"],
)

graph_input_current = Graph(
    name="input_current",
    title=Title("Input Current"),
    simple_lines=["input_current"],
)

graph_ambient_temperature = Graph(
    name="ambient_temperature",
    title=Title("Ambient Temperature"),
    simple_lines=["ambient_temperature"],
)


# ============================================================================
# Perfometers
# ============================================================================

perfometer_battery_charge = Perfometer(
    name="battery_charge",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(100),
    ),
    segments=["battery_charge"],
)

perfometer_output_load = Perfometer(
    name="output_load",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(100),
    ),
    segments=["output_load"],
)

perfometer_battery_temperature = Perfometer(
    name="battery_temperature",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(50),
    ),
    segments=["battery_temperature"],
)

perfometer_ambient_temperature = Perfometer(
    name="ambient_temperature",
    focus_range=FocusRange(
        lower=Closed(0),
        upper=Closed(50),
    ),
    segments=["ambient_temperature"],
)
