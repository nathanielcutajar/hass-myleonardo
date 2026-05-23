# MyLeonardo

[![HACS custom repository](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant custom integration](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5.svg)](https://www.home-assistant.io/)
[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](manifest.json)
[![License](https://img.shields.io/github/license/nathanielcutajar/hass-myleonardo.svg)](LICENSE)

Home Assistant custom integration for MyLeonardo solar and battery systems.

MyLeonardo is the cloud portal used by supported Western Co. Leonardo solar and
battery systems. This integration can read the external MyLeonardo API, a local
Modbus TCP device, or both in hybrid mode.

## AI Assistance Notice

Most of this integration was generated with assistance from OpenAI Codex. The
code has been reviewed and tested during development, but users should treat it
as a community-maintained custom integration and report issues through GitHub.

## Features

- Cloud polling through the MyLeonardo external API.
- Experimental local polling through a local Modbus TCP device.
- Hybrid mode with local realtime values and cloud energy/history values.
- Config flow setup with either API credentials or local Modbus host details.
- Realtime, energy, advanced diagnostic, binary status, and refresh entities.
- Redacted diagnostics support.
- Reauthentication flow when the API key is rejected.

## Documentation

- [Installation](documentation/installation.md)
- [Configuration](documentation/configuration.md)
- [Sensors](documentation/sensors.md)
- [Energy dashboard](documentation/energy-dashboard.md)
- [Automation examples](documentation/automation-examples.md)
- [Supported devices](documentation/supported-devices.md)
- [Troubleshooting](documentation/troubleshooting.md)
- [Development](documentation/development.md)
- [Home Assistant quality checklist](QUALITY_CHECKLIST.md)

## Support

Open an issue on GitHub with diagnostics from Home Assistant when possible.
API keys, plant keys, and device identifiers are redacted from diagnostics.
