# Installation

## HACS Custom Repository

1. In HACS, open **Custom repositories**.
2. Add this repository URL.
3. Select **Integration** as the category.
4. Install **MyLeonardo**.
5. Restart Home Assistant.

This repository stores the integration files at the repository root, so
`hacs.json` uses `content_in_root: true`.

## Manual

Copy the integration files into:

```text
custom_components/myleonardo/
```

Then restart Home Assistant.

## Removal

Remove the integration from **Settings > Devices & services**, then restart
Home Assistant if requested. Manual installations can also remove the
`custom_components/myleonardo/` directory after the integration entry has been
deleted.
