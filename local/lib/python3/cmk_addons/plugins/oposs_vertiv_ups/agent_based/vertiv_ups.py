#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2024 Manuel Oetiker <manuel@oetiker.ch>
# License: GNU General Public License v2

"""
Vertiv/Liebert UPS Monitoring Plugin
SNMP section with metadata-driven OID management
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from cmk.agent_based.v2 import (
    SimpleSNMPSection,
    SNMPTree,
    any_of,
    exists,
    contains,
)


# ============================================================================
# Unit Conversion Functions
# ============================================================================

def to_float(value: str) -> float:
    """Convert string to float, return 0.0 on error"""
    try:
        return float(value) if value else 0.0
    except (ValueError, TypeError):
        return 0.0


def decivolts_to_volts(value: str) -> float:
    """Convert decivolts to volts (e.g., 1200 -> 120.0)"""
    return to_float(value) / 10.0


def centihertz_to_hertz(value: str) -> float:
    """Convert centihertz to hertz (e.g., 5000 -> 50.0)"""
    return to_float(value) / 100.0


def minutes_to_seconds(value: str) -> float:
    """Convert minutes to seconds"""
    return to_float(value) * 60.0


def decicelsius_to_celsius(value: str) -> float:
    """Convert decicelsius to celsius"""
    return to_float(value) / 10.0


def deciunits_to_units(value: str) -> float:
    """Convert deci-units to base units (divide by 10)"""
    return to_float(value) / 10.0


def to_string(value: str) -> str:
    """Return string as-is, empty string on None"""
    return value if value else ""


def to_int(value: str) -> int:
    """Convert string to int, return 0 on error"""
    try:
        return int(float(value)) if value else 0
    except (ValueError, TypeError):
        return 0


# ============================================================================
# Value Mapping Dictionaries
# ============================================================================

SYSTEM_STATUS_MAP = {
    # Numeric values (some Liebert models)
    "0": "unknown",
    "1": "startup",
    "2": "normal",
    "3": "on_battery",
    "4": "on_bypass",
    "5": "shutdown",
    # String values (Vertiv GXT5 and similar models)
    "Normal Operation": "normal",
    "Startup": "startup",
    "On Battery": "on_battery",
    "On Bypass": "on_bypass",
    "Shutdown": "shutdown",
    "Unknown": "unknown",
}

BATTERY_STATUS_MAP = {
    "1": "unknown",
    "2": "normal",
    "3": "low",
    "4": "depleted",
}

OUTPUT_SOURCE_MAP = {
    "0": "unknown",
    "1": "normal",
    "2": "bypass",
    "3": "battery",
    "4": "booster",
    "5": "reducer",
}

RFC1628_OUTPUT_SOURCE_MAP = {
    "1": "other",
    "2": "none",
    "3": "normal",
    "4": "bypass",
    "5": "battery",
    "6": "booster",
    "7": "reducer",
}


# ============================================================================
# OID Metadata Definition
# ============================================================================

@dataclass
class OIDDefinition:
    """
    Complete OID metadata for structured data fetching and parsing.

    Attributes:
        key: Internal identifier for this OID
        oid: OID suffix (relative to base)
        description: Human-readable description
        output_key: Key name in parsed output dictionary
        converter: Optional function to convert/scale the value
        mapper: Optional dict to map value to string representation
        fallback_for: If set, this OID is a fallback for the named key
    """
    key: str
    oid: str
    description: str
    output_key: str
    converter: Optional[Callable[[str], Any]] = None
    mapper: Optional[Dict[str, str]] = None
    fallback_for: Optional[str] = None


# Define all OIDs with metadata - ORDER MATTERS!
# OIDs are fetched in this exact order
OID_DEFINITIONS: List[OIDDefinition] = [
    # System Information
    OIDDefinition(
        "model", "2.1.33.1.1.2.0",
        "UPS Model (RFC1628)",
        "model",
        converter=to_string
    ),
    OIDDefinition(
        "system_status", "4.1.476.1.42.3.9.20.1.20.1.2.1.4123",
        "System Status (Liebert)",
        "system_status",
        mapper=SYSTEM_STATUS_MAP
    ),
    OIDDefinition(
        "output_source", "4.1.476.1.42.3.9.20.1.20.1.2.1.4872",
        "UPS Output Source (Liebert)",
        "output_source",
        mapper=OUTPUT_SOURCE_MAP
    ),
    OIDDefinition(
        "output_source_std", "2.1.33.1.4.1.0",
        "Output Source (RFC1628)",
        "output_source_std",
        mapper=RFC1628_OUTPUT_SOURCE_MAP
    ),
    OIDDefinition(
        "eco_mode_state", "4.1.476.1.42.3.9.20.1.20.1.2.1.5454",
        "ECO Mode Operation State (Liebert)",
        "eco_mode_state",
        converter=to_int
    ),
    OIDDefinition(
        "eco_mode_status", "4.1.476.1.42.3.9.20.1.20.1.2.1.6198",
        "ECO Mode Status (Liebert)",
        "eco_mode_status",
        converter=to_int
    ),

    # Battery Metrics - Liebert Enterprise OIDs
    # Note: Liebert OIDs return decimal values in final units (not deci-units)
    OIDDefinition(
        "battery_charge", "4.1.476.1.42.3.9.20.1.20.1.2.1.4153",
        "Battery Charge % (Liebert)",
        "battery_charge",
        converter=to_float
    ),
    OIDDefinition(
        "battery_charge_std", "2.1.33.1.2.4.0",
        "Battery Charge % (RFC1628)",
        "battery_charge",
        converter=to_float,
        fallback_for="battery_charge"
    ),
    OIDDefinition(
        "battery_voltage", "4.1.476.1.42.3.9.20.1.20.1.2.1.4148",
        "Battery Voltage (Liebert)",
        "battery_voltage",
        converter=to_float  # Liebert returns decimal volts directly
    ),
    OIDDefinition(
        "battery_voltage_std", "2.1.33.1.2.5.0",
        "Battery Voltage (RFC1628)",
        "battery_voltage",
        converter=decivolts_to_volts,  # RFC1628 uses decivolts
        fallback_for="battery_voltage"
    ),
    OIDDefinition(
        "battery_current", "4.1.476.1.42.3.9.20.1.20.1.2.1.4149",
        "Battery Current (Liebert)",
        "battery_current",
        converter=to_float  # Liebert returns decimal amperes directly
    ),
    OIDDefinition(
        "battery_temperature", "4.1.476.1.42.3.9.20.1.20.1.2.1.4156",
        "Battery Temperature (Liebert)",
        "battery_temperature",
        converter=to_float  # Liebert returns decimal celsius directly
    ),
    OIDDefinition(
        "battery_temperature_std", "2.1.33.1.2.7.0",
        "Battery Temperature (RFC1628)",
        "battery_temperature",
        converter=to_float,  # RFC1628 battery temp is in degrees C
        fallback_for="battery_temperature"
    ),
    OIDDefinition(
        "battery_runtime", "4.1.476.1.42.3.9.20.1.20.1.2.1.4150",
        "Battery Runtime Minutes (Liebert)",
        "battery_runtime_seconds",
        converter=minutes_to_seconds  # Liebert returns decimal minutes
    ),
    OIDDefinition(
        "battery_runtime_std", "2.1.33.1.2.3.0",
        "Battery Runtime Minutes (RFC1628)",
        "battery_runtime_seconds",
        converter=minutes_to_seconds,  # RFC1628 returns integer minutes
        fallback_for="battery_runtime"
    ),
    OIDDefinition(
        "battery_replacement_date", "4.1.476.1.42.3.9.20.1.20.1.2.1.4160",
        "Last Battery Replacement Date (Liebert)",
        "battery_replacement_date",
        converter=to_string
    ),

    # Input Power Metrics
    OIDDefinition(
        "input_voltage", "4.1.476.1.42.3.9.20.1.20.1.2.1.4096",
        "Input Voltage (Liebert)",
        "input_voltage",
        converter=to_float  # Liebert returns decimal volts directly
    ),
    OIDDefinition(
        "input_voltage_std", "2.1.33.1.3.3.1.3.1",
        "Input Voltage (RFC1628)",
        "input_voltage",
        converter=to_float,  # RFC1628 input voltage is in RMS volts
        fallback_for="input_voltage"
    ),
    OIDDefinition(
        "input_frequency", "4.1.476.1.42.3.9.20.1.20.1.2.1.4105",
        "Input Frequency (Liebert)",
        "input_frequency",
        converter=to_float  # Liebert returns decimal Hz directly
    ),
    OIDDefinition(
        "input_frequency_std", "2.1.33.1.3.3.1.2.1",
        "Input Frequency (RFC1628)",
        "input_frequency",
        converter=deciunits_to_units,  # RFC1628 uses 0.1 Hz units
        fallback_for="input_frequency"
    ),
    OIDDefinition(
        "input_current", "4.1.476.1.42.3.9.20.1.20.1.2.1.4113",
        "Input Current L1 (Liebert)",
        "input_current",
        converter=to_float
    ),
    OIDDefinition(
        "input_power_factor", "4.1.476.1.42.3.9.20.1.20.1.2.1.4116",
        "Input Power Factor L1 (Liebert)",
        "input_power_factor",
        converter=to_float
    ),
    OIDDefinition(
        "input_voltage_max", "4.1.476.1.42.3.9.20.1.20.1.2.1.4106",
        "Max Input Voltage L1-N (Liebert)",
        "input_voltage_max",
        converter=to_float
    ),
    OIDDefinition(
        "input_voltage_min", "4.1.476.1.42.3.9.20.1.20.1.2.1.4107",
        "Min Input Voltage L1-N (Liebert)",
        "input_voltage_min",
        converter=to_float
    ),
    OIDDefinition(
        "input_blackout_count", "4.1.476.1.42.3.9.20.1.20.1.2.1.4120",
        "Input Black Out Count (Liebert)",
        "input_blackout_count",
        converter=to_int
    ),

    # Output Power Metrics
    OIDDefinition(
        "output_voltage", "2.1.33.1.4.4.1.2.1",
        "Output Voltage (RFC1628)",
        "output_voltage",
        converter=to_float
    ),
    OIDDefinition(
        "output_current", "4.1.476.1.42.3.9.20.1.20.1.2.1.4204",
        "Output Current (Liebert)",
        "output_current",
        converter=to_float  # Liebert returns decimal amperes directly
    ),
    OIDDefinition(
        "output_current_std", "2.1.33.1.4.4.1.3.1",
        "Output Current (RFC1628)",
        "output_current",
        converter=deciunits_to_units,  # RFC1628 uses 0.1 amp units
        fallback_for="output_current"
    ),
    OIDDefinition(
        "output_power", "4.1.476.1.42.3.9.20.1.20.1.2.1.4208",
        "Output Power Watts (Liebert)",
        "output_power",
        converter=to_float
    ),
    OIDDefinition(
        "output_power_std", "2.1.33.1.4.4.1.4.1",
        "Output Power Watts (RFC1628)",
        "output_power",
        converter=to_float,
        fallback_for="output_power"
    ),
    OIDDefinition(
        "output_load", "4.1.476.1.42.3.9.20.1.20.1.2.1.4223",
        "Output Load % (Liebert)",
        "output_load",
        converter=to_float
    ),
    OIDDefinition(
        "output_load_std", "2.1.33.1.4.4.1.5.1",
        "Output Load % (RFC1628)",
        "output_load",
        converter=to_float,
        fallback_for="output_load"
    ),
    OIDDefinition(
        "output_frequency", "4.1.476.1.42.3.9.20.1.20.1.2.1.4207",
        "Output Frequency (Liebert)",
        "output_frequency",
        converter=to_float  # Liebert returns decimal Hz directly
    ),
    OIDDefinition(
        "output_frequency_std", "2.1.33.1.4.2.0",
        "Output Frequency (RFC1628)",
        "output_frequency",
        converter=deciunits_to_units,  # RFC1628 uses 0.1 Hz units
        fallback_for="output_frequency"
    ),
    OIDDefinition(
        "output_apparent_power", "4.1.476.1.42.3.9.20.1.20.1.2.1.4209",
        "Output Apparent Power (Liebert)",
        "output_apparent_power",
        converter=to_float
    ),
    OIDDefinition(
        "output_power_factor", "4.1.476.1.42.3.9.20.1.20.1.2.1.4210",
        "Output Power Factor L1 (Liebert)",
        "output_power_factor",
        converter=to_float
    ),
    OIDDefinition(
        "output_apparent_power_rating", "4.1.476.1.42.3.9.20.1.20.1.2.1.4264",
        "Output Apparent Power Rating (Liebert)",
        "output_apparent_power_rating",
        converter=to_float
    ),

    # Environmental
    OIDDefinition(
        "ambient_temperature", "4.1.476.1.42.3.9.20.1.20.1.2.1.4291",
        "Inlet Air Temperature (Liebert)",
        "ambient_temperature",
        converter=to_float  # Liebert returns decimal celsius directly
    ),

    # Alarm Status OIDs
    OIDDefinition(
        "alarm_battery_low", "4.1.476.1.42.3.9.20.1.10.1.2.100.4162",
        "Battery Low Alarm",
        "alarm_battery_low",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_input_problem", "4.1.476.1.42.3.9.20.1.10.1.2.100.4122",
        "Input Problem Alarm",
        "alarm_input_problem",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_overload", "4.1.476.1.42.3.9.20.1.10.1.2.100.5806",
        "Overload Alarm",
        "alarm_overload",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_battery_temp", "4.1.476.1.42.3.9.20.1.10.1.2.100.4219",
        "Battery Temperature Alarm",
        "alarm_battery_temp",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_bypass_not_available", "4.1.476.1.42.3.9.20.1.10.1.2.100.4135",
        "Bypass Not Available Alarm",
        "alarm_bypass_not_available",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_battery_discharging", "4.1.476.1.42.3.9.20.1.10.1.2.100.4168",
        "Battery Discharging Alarm",
        "alarm_battery_discharging",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_output_off", "4.1.476.1.42.3.9.20.1.10.1.2.100.4215",
        "System Output Off Alarm",
        "alarm_output_off",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_inverter_failure", "4.1.476.1.42.3.9.20.1.10.1.2.100.4233",
        "Inverter Failure Alarm",
        "alarm_inverter_failure",
        converter=to_int
    ),
    OIDDefinition(
        "alarm_replace_battery", "4.1.476.1.42.3.9.20.1.10.1.2.100.6182",
        "Replace Battery Alarm",
        "alarm_replace_battery",
        converter=to_int
    ),
]


# ============================================================================
# Parse Function
# ============================================================================

def parse_vertiv_ups(string_table: List[List[str]]) -> Dict[str, Any]:
    """
    Parse SNMP data using OID metadata table.

    Implements automatic fallback: if primary (Liebert) OID is empty/zero,
    tries the fallback (RFC1628) OID.

    Args:
        string_table: SNMP data in order matching OID_DEFINITIONS

    Returns:
        Dictionary with parsed UPS data
    """
    if not string_table or not string_table[0]:
        return {}

    # Map raw SNMP values to OID keys
    raw_data: Dict[str, str] = {}
    for idx, value in enumerate(string_table[0]):
        if idx < len(OID_DEFINITIONS):
            raw_data[OID_DEFINITIONS[idx].key] = value

    # Process with metadata and handle fallbacks
    parsed: Dict[str, Any] = {}

    for oid_def in OID_DEFINITIONS:
        value = raw_data.get(oid_def.key, "")

        # Skip fallback OIDs - they'll be used if primary fails
        if oid_def.fallback_for:
            continue

        # If primary value is missing (empty string), check for fallback
        # Note: Zero is a valid value and should not trigger fallback
        # CRITICAL FIX: Use explicit empty string check, not "not value"
        # because "0" is falsy in Python but is a valid SNMP value
        if value == "":
            # Look for a fallback OID
            fallback_oid = next(
                (d for d in OID_DEFINITIONS if d.fallback_for == oid_def.key),
                None
            )
            if fallback_oid:
                value = raw_data.get(fallback_oid.key, "")

        # Apply conversion or mapping if value exists
        if value:
            if oid_def.mapper:
                parsed[oid_def.output_key] = oid_def.mapper.get(value, "unknown")
            elif oid_def.converter:
                try:
                    parsed[oid_def.output_key] = oid_def.converter(value)
                except (ValueError, TypeError):
                    # Use appropriate default based on converter type
                    if oid_def.converter in [to_float, decivolts_to_volts,
                                            centihertz_to_hertz, minutes_to_seconds,
                                            decicelsius_to_celsius, deciunits_to_units]:
                        parsed[oid_def.output_key] = 0.0
                    elif oid_def.converter == to_int:
                        parsed[oid_def.output_key] = 0
                    else:
                        parsed[oid_def.output_key] = ""
            else:
                # CRITICAL FIX: Store raw value if no mapper or converter specified
                # This prevents silent data loss
                parsed[oid_def.output_key] = value

    return parsed


# ============================================================================
# SNMP Section Registration
# ============================================================================

snmp_section_vertiv_ups = SimpleSNMPSection(
    name="vertiv_ups",
    parse_function=parse_vertiv_ups,
    fetch=SNMPTree(
        base=".1.3.6.1",  # Base OID for all SNMP queries
        oids=[oid_def.oid for oid_def in OID_DEFINITIONS],
    ),
    detect=any_of(
        # Liebert-GP Agent present
        exists(".1.3.6.1.4.1.476.1.42.2.1.1.0"),
        # Standard UPS MIB with Vertiv manufacturer
        contains(".1.3.6.1.2.1.33.1.1.1.0", "Vertiv"),
    ),
)
