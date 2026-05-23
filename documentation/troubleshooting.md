# Troubleshooting

## Data Updates

The integration uses Home Assistant data coordinators. Each endpoint has its own
coordinator and polling interval:

- Realtime: defaults to 30 seconds.
- Energy: defaults to 300 seconds.
- Monthly energy: defaults to 300 seconds.
- Advanced: defaults to 120 seconds.
- Advanced complete: defaults to 120 seconds.
- Local Modbus TCP: defaults to 5 seconds.

If MyLeonardo rejects the API key, Home Assistant starts a reauthentication
flow. If the service is temporarily unavailable, affected entities are marked
unavailable until polling succeeds again.

After repeated update failures, the integration creates a Home Assistant repair
issue for the affected endpoint. The repair issue is cleared automatically once
that endpoint updates successfully again.

## API Limits

The MyLeonardo API documentation lists these rate limits:

- Realtime: max one request every 5 seconds.
- Energy: max one request every 20 seconds.
- Advanced: max one request every 20 seconds.

The integration polls within those limits.
When daily/monthly energy or basic/complete advanced data are refreshed close
together, the integration throttles calls to the shared endpoint before sending
the second request.

## Known Limitations

- Cloud API mode depends on the MyLeonardo cloud service.
- Hybrid mode depends on both the local Modbus device and the MyLeonardo cloud
  service; realtime values can be local while history values still come from
  the cloud.
- Local Modbus TCP mode requires Home Assistant to reach the local Modbus TCP
  device on the network.
- Energy semantics depend on the MyLeonardo daily energy endpoint. The cloud
  API mode queries from local midnight to now for today's energy sensors.
- Discovery is not implemented; setup requires manually entering an API key and
  plant key or local Modbus host.

## Common Issues

- If setup fails with an authentication error, verify the API key.
- If setup fails with a plant error, verify the plant key.
- If entities become unavailable, check MyLeonardo service availability and the
  Home Assistant logs.
- If Home Assistant shows a MyLeonardo repair issue, follow the repair text and
  check cloud availability, local network access, or connection details.
- Use Home Assistant diagnostics when opening issues. API key, plant key, and
  device identifiers are redacted.
