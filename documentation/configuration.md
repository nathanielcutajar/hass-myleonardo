# Configuration

Add the integration from **Settings > Devices & services > Add integration** and
search for **MyLeonardo**.

Choose one connection type during setup.

## Cloud API

Cloud API mode needs:

- MyLeonardo API key
- MyLeonardo plant key

The API key is stored in the Home Assistant config entry. It is redacted from
diagnostics.

## Local Modbus TCP

Local Modbus TCP mode needs:

- Local Modbus TCP device IP address / hostname
- Modbus TCP port, usually `502`

Local Modbus TCP is experimental. It reads the inverter directly and does not
use the MyLeonardo cloud service.

## Hybrid

Hybrid mode needs both sets of details. It uses Local Modbus TCP for fast
realtime plant values and the MyLeonardo cloud API for daily energy and
advanced diagnostic values.

## Options

The integration options allow you to:

- Enable or disable realtime sensors.
- Enable or disable daily energy sensors.
- Enable or disable optional monthly energy sensors.
- Enable or disable advanced diagnostic sensors.
- Enable or disable optional advanced-complete diagnostic sensors.
- Set the realtime polling interval in seconds.
- Set the energy polling interval in seconds.
- Set the advanced polling interval in seconds.

Polling intervals are clamped by the setup form to the API rate limits:

- Realtime: minimum 5 seconds.
- Energy: minimum 20 seconds.
- Advanced: minimum 20 seconds.
- Local Modbus TCP: minimum 1 second, defaults to 5 seconds.

Hybrid mode uses the Local Modbus TCP interval for realtime sensors and the
cloud API intervals for energy and advanced sensors.

Monthly energy and advanced-complete diagnostic sensors are disabled by default
because they require additional cloud API requests. Enable them only if those
values are useful in your installation.
