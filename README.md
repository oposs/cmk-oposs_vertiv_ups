# OPOSS Vertiv/Liebert UPS Monitoring Plugin for CheckMK

[![License](https://img.shields.io/badge/License-GPLv2-blue.svg)](LICENSE)
[![CheckMK](https://img.shields.io/badge/CheckMK-2.3.0+-green.svg)](https://checkmk.com/)

Comprehensive SNMP monitoring plugin for Vertiv/Liebert UPS devices in CheckMK 2.3.x.

## Features

- **52+ SNMP OIDs monitored** across battery, power, and environmental metrics
- **Dual Protocol Support**: RFC1628 standard UPS MIB and Liebert enterprise MIBs
- **Smart Fallback**: Automatically falls back from Liebert OIDs to RFC1628 when needed
- **ECO Mode Detection**: Recognizes and properly reports ECO/bypass mode as normal operation
- **Rich Visualization**: Comprehensive graphs and perfometers
- **Web UI Configuration**: Easy threshold customization via rulesets
- **Out-of-the-Box**: Works immediately with sensible defaults
- **Multi-Voltage Support**: Handles both 120V (US) and 230V (EU) systems

## Installation

1. Download the latest MKP package from [Releases](https://github.com/oposs/cmk-oposs_vertiv_ups/releases)
2. In CheckMK: **Setup → Extension packages**
3. Click **Upload package** and select the `.mkp` file
4. Click **Install**

**Test SNMP connectivity:**
```bash
snmpwalk -v2c -c public your-ups-hostname .1.3.6.1.4.1.476
```

## Supported Devices

**Tested:** Vertiv GXT5-1500IRT2UXL

**Compatible with any Vertiv/Liebert UPS supporting:**
- Liebert-GP MIB (OID: 1.3.6.1.4.1.476.1.42)
- RFC1628 UPS MIB (OID: 1.3.6.1.2.1.33)

Including: GXT5 series, Liebert GXT series, Liebert PSI series, and other Liebert-GP compatible devices.

## Monitored Services

### Battery Service
- Charge percentage, temperature, runtime, voltage, current
- Last battery replacement date
- Alarms: battery low, over-temperature, discharging, replace battery
- **Defaults:** Charge WARN 20%/CRIT 10%, Temp WARN 30°C/CRIT 35°C, Runtime WARN 10min/CRIT 5min

### Power Service
- System status, ECO mode, output load, voltage, current, power, frequency
- Input voltage/current/frequency/power factor, voltage statistics (min/max)
- Alarms: input problem, overload, bypass unavailable, output off, inverter failure
- **Defaults:** Load WARN 80%/CRIT 90%, Frequency WARN ±2Hz/CRIT ±3Hz (50Hz nominal)
- **Voltage:** Disabled by default (configure per region)

### Environment Service
- Ambient/inlet air temperature
- **Defaults:** WARN 35°C, CRIT 40°C

## Configuration

### Voltage Thresholds (Regional)

**230V Systems (Europe/Asia):**
- Upper: 253V (warn), 265V (crit)
- Lower: 207V (warn), 195V (crit)

**120V Systems (North America):**
- Upper: 132V (warn), 138V (crit)
- Lower: 108V (warn), 102V (crit)

### Frequency Thresholds

**50Hz Systems:** Upper 52Hz/53Hz, Lower 48Hz/47Hz
**60Hz Systems:** Upper 62Hz/63Hz, Lower 58Hz/57Hz

**Configure via:** Setup → Services → Service monitoring rules → Search "Vertiv UPS"

## Troubleshooting

**Services not appearing?**
1. Test: `snmpwalk -v2c -c public UPS_IP .1.3.6.1.4.1.476`
2. Check CheckMK SNMP settings
3. Run service discovery: Setup → Hosts → Services → Fix all

**Wrong values (÷10)?** → Update to v0.0.4+

**System status "unknown"?** → Update to v0.0.7+ (supports string status values)

**Voltage alarms (230V)?** → Update to v0.0.8+ (voltage thresholds disabled by default)

## Architecture

**Metadata-Driven OID Management:** All OIDs in structured table with Liebert primary + RFC1628 fallback
**Smart Unit Handling:** Liebert OIDs return decimals, RFC1628 returns deci-units
**DRY Code:** Helper functions eliminate repetition
**Declarative Alarms:** Simple declarative alarm lists

```
local/lib/python3/cmk_addons/plugins/oposs_vertiv_ups/
├── agent_based/      # SNMP section + check plugins
├── graphing/         # Metrics, graphs, perfometers
└── rulesets/         # Web UI configuration
```

## Contributing

Contributions welcome via [GitHub Issues](https://github.com/oposs/cmk-oposs_vertiv_ups/issues):
- Bug reports
- Feature requests
- Pull requests
- Documentation improvements
- Device compatibility reports

## References

- [CheckMK Documentation](https://docs.checkmk.com/)
- [CheckMK Plugin Development](https://docs.checkmk.com/latest/en/devel_intro.html)
- [RFC1628 UPS MIB](https://www.rfc-editor.org/rfc/rfc1628)
- [Vertiv Support](https://www.vertiv.com/en-us/support/)

---

**Made with ❤️ by OETIKER+PARTNER AG**
