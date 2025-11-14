# OPOSS Vertiv/Liebert UPS Monitoring Plugin for CheckMK

[![License](https://img.shields.io/badge/License-GPLv2-blue.svg)](LICENSE)
[![CheckMK](https://img.shields.io/badge/CheckMK-2.3.0+-green.svg)](https://checkmk.com/)

Comprehensive SNMP monitoring plugin for Vertiv/Liebert UPS devices in CheckMK 2.3.x.

## 🎯 Features

- **📊 Complete Monitoring Coverage**: 52+ SNMP OIDs monitored across battery, power, and environmental metrics
- **🔌 Dual Protocol Support**: Works with both RFC1628 standard UPS MIB and Liebert enterprise MIBs
- **⚡ Smart Fallback**: Automatically falls back from Liebert OIDs to RFC1628 standard OIDs when needed
- **🌿 ECO Mode Detection**: Recognizes and properly reports ECO/bypass mode as normal operation
- **📈 Rich Visualization**: Comprehensive graphs and perfometers for all metrics
- **🎛️ User-Friendly Configuration**: Web UI rulesets for easy threshold customization
- **🚀 Out-of-the-Box**: Works immediately with sensible defaults, no configuration required
- **🌍 Multi-Voltage Support**: Handles both 120V (US) and 230V (EU) systems

## 📦 Installation

### Prerequisites

- CheckMK 2.3.0p1 or higher
- SNMP access to your Vertiv/Liebert UPS
- Network connectivity from CheckMK server to UPS

### Quick Install

1. Download the latest MKP package from [Releases](https://github.com/oposs/cmk-oposs_vertiv_ups/releases)
2. In CheckMK, go to **Setup → Extension packages**
3. Click **Upload package** and select the downloaded `.mkp` file
4. Click **Install** to activate the plugin

### SNMP Configuration

Ensure your UPS has SNMP enabled and accessible:

```bash
# Test SNMP connectivity
snmpwalk -v2c -c public your-ups-hostname .1.3.6.1.4.1.476
```

## 🔧 Supported Devices

### Tested Devices

- ✅ Vertiv GXT5-1500IRT2UXL

### Compatible Models

This plugin should work with any Vertiv/Liebert UPS that supports:
- Liebert-GP MIB (enterprise OID: 1.3.6.1.4.1.476.1.42)
- RFC1628 UPS MIB (standard OID: 1.3.6.1.2.1.33)

Including:
- Vertiv GXT5 series
- Vertiv Liebert GXT series
- Vertiv Liebert PSI series
- Other Liebert-GP protocol compatible devices

## 📊 Monitored Metrics

The plugin creates three separate services for logical organization:

### 🔋 Vertiv UPS Battery

**Metrics:**
- Battery charge percentage (with thresholds)
- Battery temperature (with thresholds)
- Estimated runtime (with thresholds)
- Battery voltage
- Battery current
- Last battery replacement date

**Alarms:**
- Battery low
- Battery over-temperature
- Battery discharging
- Replace battery

**Default Thresholds:**
- Charge: WARN at 20%, CRIT at 10%
- Temperature: WARN at 30°C, CRIT at 35°C
- Runtime: WARN at 10min, CRIT at 5min

### ⚡ Vertiv UPS Power

**Metrics:**
- System status (normal, on_battery, on_bypass, etc.)
- ECO mode status
- Output load percentage (with thresholds)
- Output voltage, current, power, frequency
- Input voltage, current, frequency, power factor
- Input voltage statistics (min/max)
- Power factor (input/output)
- Apparent power and ratings
- Blackout count

**Alarms:**
- Input power problem
- Output overload
- Bypass not available
- System output off
- Inverter failure

**Default Thresholds:**
- Load: WARN at 80%, CRIT at 90%
- Voltage: Disabled by default (configure per your voltage)
- Frequency: WARN at ±2Hz, CRIT at ±3Hz (50Hz nominal)

### 🌡️ Vertiv UPS Environment

**Metrics:**
- Ambient/inlet air temperature (with thresholds)

**Default Thresholds:**
- Temperature: WARN at 35°C, CRIT at 40°C

## 📈 Graphs and Visualizations

The plugin provides comprehensive graphing:

### Battery Graphs
- Battery charge percentage (0-100%)
- Battery runtime (estimated)
- Battery temperature
- Battery electrical (voltage/current)

### Power Graphs
- UPS output load (0-100%)
- Output power (Watts)
- Output apparent power (VA)
- Power factor (input/output)
- Frequency (input vs output)
- Voltage comparison (input vs output)
- Input voltage statistics (current/min/max)
- Input/output current

### Environmental Graphs
- Ambient temperature

### Perfometers
- Battery charge (visual bar)
- Output load (visual bar)
- Battery temperature (visual bar)
- Ambient temperature (visual bar)

## ⚙️ Configuration

### Default Operation

The plugin works immediately with **no configuration required**. Sensible defaults are applied based on typical UPS usage patterns.

### Customizing Thresholds

To customize monitoring thresholds:

1. Go to **Setup → Services → Service monitoring rules**
2. Search for "Vertiv UPS"
3. Create rules for:
   - **Vertiv UPS Battery** - Battery thresholds
   - **Vertiv UPS Power** - Power and load thresholds
   - **Vertiv UPS Environment** - Temperature thresholds

### Voltage Configuration by Region

**For 230V Systems (Europe, Asia, most of world):**
```
Output voltage upper: 253V (warn), 265V (crit)
Output voltage lower: 207V (warn), 195V (crit)
```

**For 120V Systems (North America, parts of Asia):**
```
Output voltage upper: 132V (warn), 138V (crit)
Output voltage lower: 108V (warn), 102V (crit)
```

### Frequency Configuration

**For 50Hz Systems (Europe, Asia, most of world):**
```
Output frequency upper: 52Hz (warn), 53Hz (crit)
Output frequency lower: 48Hz (warn), 47Hz (crit)
```

**For 60Hz Systems (North America, parts of Asia):**
```
Output frequency upper: 62Hz (warn), 63Hz (crit)
Output frequency lower: 58Hz (warn), 57Hz (crit)
```

## 🏗️ Architecture

### Design Highlights

- **Metadata-Driven OID Management**: All OIDs defined in a structured, maintainable table
- **Automatic Fallback**: Primary Liebert OIDs with RFC1628 fallbacks
- **Proper Unit Handling**: Liebert OIDs return decimal values; RFC1628 returns deci-units
- **DRY Code**: Helper functions eliminate repetitive patterns
- **Declarative Alarms**: Alarm checking via simple declarative lists

### File Structure

```
local/
└── lib/python3/
    └── cmk_addons/plugins/oposs_vertiv_ups/
        ├── agent_based/
        │   ├── vertiv_ups.py          # SNMP section + OID definitions
        │   ├── vertiv_ups_battery.py  # Battery monitoring check
        │   ├── vertiv_ups_power.py    # Power monitoring check
        │   └── vertiv_ups_environment.py # Environment monitoring check
        ├── graphing/
        │   └── vertiv_ups.py          # Metrics, graphs, perfometers
        └── rulesets/
            └── vertiv_ups.py          # Web UI configuration rulesets
```

## 🔍 Troubleshooting

### Service Discovery Issues

**Problem**: Services not appearing after SNMP setup

**Solution**:
1. Test SNMP connectivity: `snmpwalk -v2c -c public UPS_IP .1.3.6.1.4.1.476`
2. Check CheckMK SNMP settings for the host
3. Verify UPS supports Liebert-GP MIB or RFC1628
4. Run service discovery: **Setup → Hosts → Services → Fix all**

### Incorrect Values

**Problem**: Metrics showing wrong values (e.g., voltage ÷10)

**Solution**: This was fixed in v0.0.4. Ensure you're using version 0.0.4 or later.

### System Status "Unknown"

**Problem**: System status showing as CRIT with "unknown"

**Solution**: Fixed in v0.0.7. The plugin now handles both numeric and string status values from different Vertiv models.

### Voltage Alarms (230V Systems)

**Problem**: False voltage alarms on 230V systems

**Solution**: Fixed in v0.0.8. Voltage thresholds are now disabled by default. Configure appropriate 230V thresholds via CheckMK rules if needed.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit:

- Bug reports via [Issues](https://github.com/oposs/cmk-oposs_vertiv_ups/issues)
- Feature requests
- Pull requests with improvements
- Documentation enhancements
- Additional device compatibility reports

## 📄 License

This project is licensed under the GNU General Public License v2 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the CheckMK community
- Developed using Vertiv/Liebert MIB documentation and RFC1628 standard
- Tested on Vertiv GXT5-1500IRT2UXL hardware

## 📚 References

- [CheckMK Official Documentation](https://docs.checkmk.com/)
- [CheckMK Plugin Development Guide](https://docs.checkmk.com/latest/en/devel_intro.html)
- [RFC1628 UPS MIB Specification](https://www.rfc-editor.org/rfc/rfc1628)
- [Vertiv Support](https://www.vertiv.com/en-us/support/)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/oposs/cmk-oposs_vertiv_ups/issues)
- **Discussions**: [GitHub Discussions](https://github.com/oposs/cmk-oposs_vertiv_ups/discussions)
- **Email**: manuel@oetiker.ch

---

**Made with ❤️ by OETIKER+PARTNER AG**
