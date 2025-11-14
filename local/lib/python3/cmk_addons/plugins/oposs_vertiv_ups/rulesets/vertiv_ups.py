#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Manuel Oetiker <manuel@oetiker.ch>
# License: GNU General Public License v2

"""
Vertiv/Liebert UPS Rulesets
Web UI configuration for threshold parameters
"""

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    SimpleLevels,
    LevelDirection,
    DefaultValue,
    Float,
    TimeSpan,
    TimeMagnitude,
    validators,
)
from cmk.rulesets.v1.rule_specs import (
    CheckParameters,
    Topic,
    HostCondition,
)


# ============================================================================
# Battery Monitoring Ruleset
# ============================================================================

def _form_spec_vertiv_ups_battery():
    return Dictionary(
        title=Title("Vertiv UPS Battery Monitoring"),
        help_text=Help(
            "Configure monitoring thresholds for Vertiv/Liebert UPS battery metrics. "
            "Lower levels trigger alerts when values drop below thresholds. "
            "Upper levels trigger alerts when values exceed thresholds."
        ),
        elements={
            "battery_charge_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Battery charge percentage"),
                    help_text=Help(
                        "Warning and critical levels for battery charge percentage. "
                        "Alerts trigger when charge drops below these levels."
                    ),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(
                        unit_symbol="%",
                        custom_validate=[validators.NumberInRange(min_value=0, max_value=100)],
                    ),
                    prefill_fixed_levels=DefaultValue((20.0, 10.0)),
                ),
                required=True,
            ),
            "battery_temperature_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Battery temperature"),
                    help_text=Help(
                        "Warning and critical levels for battery temperature. "
                        "High battery temperature can indicate overcharging or environmental issues."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="°C",
                        custom_validate=[validators.NumberInRange(min_value=0, max_value=100)],
                    ),
                    prefill_fixed_levels=DefaultValue((30.0, 35.0)),
                ),
                required=True,
            ),
            "battery_runtime_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Estimated battery runtime"),
                    help_text=Help(
                        "Warning and critical levels for estimated battery runtime. "
                        "Alerts trigger when remaining runtime drops below these levels."
                    ),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[
                            TimeMagnitude.HOUR,
                            TimeMagnitude.MINUTE,
                        ],
                    ),
                    prefill_fixed_levels=DefaultValue((600.0, 300.0)),  # 10 min, 5 min in seconds
                ),
                required=True,
            ),
        },
    )


rule_spec_vertiv_ups_battery = CheckParameters(
    title=Title("Vertiv UPS Battery"),
    topic=Topic.POWER,
    name="vertiv_ups_battery",
    parameter_form=_form_spec_vertiv_ups_battery,
    condition=HostCondition(),
)


# ============================================================================
# Power Monitoring Ruleset
# ============================================================================

def _form_spec_vertiv_ups_power():
    return Dictionary(
        title=Title("Vertiv UPS Power Monitoring"),
        help_text=Help(
            "Configure monitoring thresholds for Vertiv/Liebert UPS power metrics including "
            "output load, voltage, and frequency parameters."
        ),
        elements={
            "output_load_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output load percentage"),
                    help_text=Help(
                        "Warning and critical levels for UPS output load. "
                        "High load may indicate capacity issues or oversubscription."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="%",
                        custom_validate=[validators.NumberInRange(min_value=0, max_value=100)],
                    ),
                    prefill_fixed_levels=DefaultValue((80.0, 90.0)),
                ),
                required=True,
            ),
            "output_voltage_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output voltage upper levels"),
                    help_text=Help(
                        "Upper warning and critical levels for output voltage. "
                        "Configure based on your nominal voltage:\n"
                        "• 230V systems: typically 253V warn, 265V crit (+10%/+15%)\n"
                        "• 120V systems: typically 132V warn, 138V crit (+10%/+15%)"
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="V"),
                    prefill_fixed_levels=DefaultValue((253.0, 265.0)),  # 230V nominal
                ),
                required=False,
            ),
            "output_voltage_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output voltage lower levels"),
                    help_text=Help(
                        "Lower warning and critical levels for output voltage. "
                        "Configure based on your nominal voltage:\n"
                        "• 230V systems: typically 207V warn, 195V crit (-10%/-15%)\n"
                        "• 120V systems: typically 108V warn, 102V crit (-10%/-15%)"
                    ),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(unit_symbol="V"),
                    prefill_fixed_levels=DefaultValue((207.0, 195.0)),  # 230V nominal
                ),
                required=False,
            ),
            "output_frequency_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output frequency upper levels"),
                    help_text=Help(
                        "Upper warning and critical levels for output frequency. "
                        "Adjust based on your nominal frequency (50Hz or 60Hz)."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(unit_symbol="Hz"),
                    prefill_fixed_levels=DefaultValue((52.0, 53.0)),  # 50Hz nominal
                ),
                required=False,
            ),
            "output_frequency_lower": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Output frequency lower levels"),
                    help_text=Help(
                        "Lower warning and critical levels for output frequency."
                    ),
                    level_direction=LevelDirection.LOWER,
                    form_spec_template=Float(unit_symbol="Hz"),
                    prefill_fixed_levels=DefaultValue((48.0, 47.0)),  # 50Hz nominal
                ),
                required=False,
            ),
        },
    )


rule_spec_vertiv_ups_power = CheckParameters(
    title=Title("Vertiv UPS Power"),
    topic=Topic.POWER,
    name="vertiv_ups_power",
    parameter_form=_form_spec_vertiv_ups_power,
    condition=HostCondition(),
)


# ============================================================================
# Environment Monitoring Ruleset
# ============================================================================

def _form_spec_vertiv_ups_environment():
    return Dictionary(
        title=Title("Vertiv UPS Environment Monitoring"),
        help_text=Help(
            "Configure monitoring thresholds for environmental conditions around the UPS."
        ),
        elements={
            "ambient_temperature_upper": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Ambient temperature"),
                    help_text=Help(
                        "Warning and critical levels for ambient (inlet air) temperature. "
                        "High ambient temperature can affect UPS performance and battery life."
                    ),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=Float(
                        unit_symbol="°C",
                        custom_validate=[validators.NumberInRange(min_value=-20, max_value=100)],
                    ),
                    prefill_fixed_levels=DefaultValue((35.0, 40.0)),
                ),
                required=True,
            ),
        },
    )


rule_spec_vertiv_ups_environment = CheckParameters(
    title=Title("Vertiv UPS Environment"),
    topic=Topic.ENVIRONMENTAL,
    name="vertiv_ups_environment",
    parameter_form=_form_spec_vertiv_ups_environment,
    condition=HostCondition(),
)


# ============================================================================
# Register all rule specifications for CheckMK discovery
# ============================================================================

__all__ = [
    "rule_spec_vertiv_ups_battery",
    "rule_spec_vertiv_ups_power",
    "rule_spec_vertiv_ups_environment",
]
