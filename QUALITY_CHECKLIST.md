# Home Assistant Integration Quality Checklist

Reference copy of the Home Assistant Integration Quality Scale checklist for
MyLeonardo.

Source: https://developers.home-assistant.io/docs/core/integration-quality-scale/checklist/

Last reviewed locally: 2026-05-21

Legend:

- `[x]` Completed or not applicable for this integration's current surface area.
- `[ ]` Not completed yet.

## Bronze

- [x] `action-setup` - Service actions are registered in async_setup.
  - Refresh is implemented as a button platform and registered through `PLATFORMS`.
- [x] `appropriate-polling` - If it's a polling integration, set an appropriate polling interval.
- [x] `brands` - Has branding assets available for the integration.
- [x] `common-modules` - Place common patterns in common modules.
- [ ] `config-flow-test-coverage` - Full test coverage for the config flow.
  - Lightweight structure tests now cover Cloud, Modbus, options, and reconfigure paths.
  - Full Home Assistant config-flow tests are still needed to complete this item.
- [x] `config-flow` - Integration needs to be able to be set up via the UI.
  - [x] Uses `data_description` to give context to fields.
  - [x] Uses `ConfigEntry.data` and `ConfigEntry.options` correctly.
- [x] `dependency-transparency` - Dependency transparency.
- [x] `docs-actions` - The documentation describes the provided service actions that can be used.
  - Refresh is exposed as a button entity rather than a service action.
- [x] `docs-high-level-description` - The documentation includes a high-level description of the integration brand, product, or service.
- [x] `docs-installation-instructions` - The documentation provides step-by-step installation instructions for the integration, including, if needed, prerequisites.
- [x] `docs-removal-instructions` - The documentation provides removal instructions.
- [x] `entity-event-setup` - Entity events are subscribed in the correct lifecycle methods.
  - Not applicable: this integration does not currently subscribe to entity events.
- [x] `entity-unique-id` - Entities have a unique ID.
- [x] `has-entity-name` - Entities use `has_entity_name = True`.
- [x] `runtime-data` - Use `ConfigEntry.runtime_data` to store runtime data.
- [x] `test-before-configure` - Test a connection in the config flow.
- [x] `test-before-setup` - Check during integration initialization if we are able to set it up correctly.
- [x] `unique-config-entry` - Don't allow the same device or service to be able to be set up twice.

## Silver

- [x] `action-exceptions` - Service actions raise exceptions when encountering failures.
  - Refresh uses coordinator refresh behavior and coordinator failures are normalized.
- [x] `config-entry-unloading` - Support config entry unloading.
- [x] `docs-configuration-parameters` - The documentation describes all integration configuration options.
- [x] `docs-installation-parameters` - The documentation describes all integration installation parameters.
- [x] `entity-unavailable` - Mark entity unavailable if appropriate.
- [x] `integration-owner` - Has an integration owner.
- [x] `log-when-unavailable` - If internet/device/service is unavailable, log once when unavailable and once when back connected.
- [x] `parallel-updates` - Number of parallel updates is specified.
- [x] `reauthentication-flow` - Reauthentication needs to be available via the UI.
- [ ] `test-coverage` - Above 95% test coverage for all integration modules.
  - Parser, metadata, API, and Modbus unit tests exist, but measured coverage is not yet tracked.

## Gold

- [x] `devices` - The integration creates devices.
- [x] `diagnostics` - Implements diagnostics.
- [ ] `discovery-update-info` - Integration uses discovery info to update network information.
- [ ] `discovery` - Devices can be discovered.
- [x] `docs-data-update` - The documentation describes how data is updated.
- [ ] `docs-examples` - The documentation provides automation examples the user can use.
- [x] `docs-known-limitations` - The documentation describes known limitations of the integration.
- [ ] `docs-supported-devices` - The documentation describes known supported / unsupported devices.
- [x] `docs-supported-functions` - The documentation describes the supported functionality, including entities, and platforms.
  - README covers Cloud API mode, Local Modbus TCP mode, Hybrid mode, sensor groups, binary status sensors, Energy Dashboard recommendations, grid sign convention, and refresh behavior.
- [x] `docs-troubleshooting` - The documentation provides troubleshooting information.
- [x] `docs-use-cases` - The documentation describes use cases to illustrate how this integration can be used.
- [ ] `dynamic-devices` - Devices added after integration setup.
- [x] `entity-category` - Entities are assigned an appropriate `EntityCategory`.
- [x] `entity-device-class` - Entities use device classes where possible.
- [x] `entity-disabled-by-default` - Integration disables less popular or noisy entities.
- [x] `entity-translations` - Entities have translated names.
- [ ] `exception-translations` - Exception messages are translatable.
- [x] `icon-translations` - Entities implement icon translations.
- [x] `reconfiguration-flow` - Integrations should have a reconfigure flow.
- [x] `repair-issues` - Repair issues and repair flows are used when user intervention is needed.
  - Repeated endpoint update failures create a repair issue that clears automatically after recovery.
- [ ] `stale-devices` - Stale devices are removed.

## Platinum

- [x] `async-dependency` - Dependency is async.
- [x] `inject-websession` - The integration dependency supports passing in a websession.
- [ ] `strict-typing` - Strict typing.

## Next Quality Targets

- Add full Home Assistant config flow tests.
- Add coverage measurement for refresh button behavior and manual refresh rate-limit skipping.
- Measure and raise test coverage toward 95%.
- Add automation examples to the README.
- Add an explicit supported / unsupported devices section to the README.
- Use translated exceptions where Home Assistant supports them.
- Decide whether discovery and dynamic device handling are possible for Cloud API or Local Modbus TCP mode.
