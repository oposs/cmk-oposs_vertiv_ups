# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### New

### Changed

### Fixed

## 1.0.0 - 2025-11-14
## 0.0.8 - 2024-11-13

### Fixed
- **CRITICAL**: Removed incorrect voltage thresholds that caused false alarms on 230V systems
- Default thresholds were set for 120V (US), causing 230V (EU) systems to show CRIT
- Voltage thresholds now disabled by default - must be configured per deployment

### Changed
- Updated ruleset default values to 230V (±10%/±15% tolerance)
- Added comprehensive help text for voltage configuration showing both 120V and 230V values
- Improved documentation in rulesets explaining regional voltage differences

## 0.0.7 - 2024-11-13

### Fixed
- **CRITICAL**: System status now correctly recognizes string values from Vertiv GXT5
- Added support for "Normal Operation", "On Battery", "On Bypass" string values
- Previously only supported numeric codes (0-5) causing "unknown" status
- Maintains backward compatibility with older Liebert models using numeric values

### Changed
- Improved system status detection with smarter fallback logic
- ECO mode (bypass) now properly treated as OK state, not warning
- Enhanced status messages: shows "bypass (ECO mode)" for better clarity

## 0.0.6 - 2024-11-13

### Fixed
- **CRITICAL**: Fallback logic now correctly handles zero values
- Bug: `if not value:` treated string "0" as falsy, incorrectly triggering RFC1628 fallback
- Impact: Battery current=0, input current=0, etc. now report correctly
- **CRITICAL**: Prevented silent data loss when OID has no mapper/converter
- Added else clause to store raw values if no processing defined
- Eliminates risk of configuration errors causing invisible data loss
- **HIGH**: Fixed incorrect converter usage for RFC1628 output current
- Was using `decivolts_to_volts` (semantically wrong)
- Now uses `deciunits_to_units` (correct generic converter)
- **HIGH**: Added missing ruleset registration exports
- Rulesets now properly exported via `__all__` for CheckMK discovery

### Changed
- **MAJOR CODE REFACTOR**: Eliminated ~145 lines of repetitive code
- Created `yield_informational_metric()` helper function (-100 lines)
- Created `check_alarms()` declarative alarm checking (-45 lines)
- Battery check: reduced from ~240 to 201 lines (-16%)
- Power check: reduced from ~350 to 287 lines (-18%)
- Significantly improved code maintainability through DRY principles
- Better code readability with declarative patterns
- Added comprehensive documentation to helper functions

## 0.0.5 - 2024-11-13

### New
- ECO mode monitoring (2 new OIDs)
- OID 5454: ECO Mode Operation State
- OID 6198: ECO Mode Status
- Automatic ECO mode detection when UPS is in bypass
- Output source tracking (2 new OIDs)
- OID 4872: UPS Output Source (Liebert)
- OID 1.3.6.1.2.1.33.1.4.1.0: RFC1628 Output Source
- Input power statistics (3 new OIDs)
- OID 4113: Input Current L1
- OID 4106: Max Input Voltage L1-N
- OID 4107: Min Input Voltage L1-N
- Battery maintenance tracking
- OID 4160: Last Battery Replacement Date
- New metrics: `input_current`, `input_voltage_max`, `input_voltage_min`
- New graph: "Input Voltage Statistics" (current/min/max)
- New graph: "Input Current"

### Changed
- Total monitored OIDs increased from ~45 to 52+
- Enhanced power service with input statistics display

## 0.0.4 - 2024-11-13

### Fixed
- **CRITICAL**: Corrected unit conversion for all Liebert enterprise OIDs
- Bug: Liebert OIDs return decimal values (e.g., "231.3"), not deci-units
- Was incorrectly dividing by 10 again, causing:
  - Input voltage: 22.91V instead of 231.3V
  - Output frequency: 4.99Hz instead of 49.9Hz
  - Battery voltage: 5.4V instead of 54V
  - Battery temperature: 2.76°C instead of 26.4°C
- Fixed 8 converter functions to use `to_float()` instead of deci-unit converters

### Changed
- Updated all Liebert OID converters while maintaining RFC1628 fallback converters
- Added comments explaining Liebert vs RFC1628 unit differences

## 0.0.3 - 2024-11-13

### Fixed
- Fixed `render.temperature` error - CheckMK 2.3.x doesn't have this function
- Replaced with custom lambda: `lambda t: f"{t:.1f} °C"`
- Fixed `render.frequency` error - CheckMK 2.3.x doesn't have this function
- Replaced with custom lambda: `lambda f: f"{f:.1f} Hz"`
- Fixed graph unit mixing error
- Cannot mix VA (volt-amperes) and W (watts) in same graph
- Split into separate graphs: `graph_output_power` (W only) and `graph_output_apparent_power` (VA only)

### Changed
- All Python files validated successfully
- Package size: 9.3K

## 0.0.2 - 2024-11-13

### New
- Initial public release
- Comprehensive SNMP monitoring for Vertiv/Liebert UPS devices
- Support for both RFC1628 standard and Liebert enterprise MIBs
- Three monitoring services:
  - Battery monitoring (charge, temperature, runtime, voltage, current)
  - Power monitoring (input/output voltage, frequency, load, power metrics)
  - Environment monitoring (ambient temperature)
- 40+ SNMP OIDs monitored
- Automatic fallback from Liebert to RFC1628 OIDs
- 9 alarm conditions monitored
- Comprehensive graphing and perfometers
- Web UI rulesets for threshold configuration
- Out-of-the-box functionality with sensible defaults
- Metadata-driven OID management architecture
- CheckMK 2.3.0p1+ compatible
- Tested on Vertiv GXT5-1500IRT2UXL
