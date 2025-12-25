# Deployment checklist (sealed model builds)

This is the boring part that stops you reopening the model with a screwdriver later.

## Before you install it in the model
- Encode media to a sane bitrate for the panel and board class.
- Test the full playlist end-to-end.
- Cold boot test: 10+ power cycles. If it fails once, it will fail in the model.

## Recommended config for sealed builds
Use `assets/sealed-model.ini` as a starting point.

Key points:
- `read_only = true` (reduces SD writes)
- `alive_file = /tmp/pi_model_looper.alive` (optional heartbeat)
- `preflight_media = true` (skip obvious junk quickly)

## SD card reality
If you can, keep the filesystem as read-only after deployment.
At minimum, keep writes low. This repo tries to help, but physics still wins.

## Power
Brownouts happen.
If you're driving a screen and a Pi Zero from a questionable supply, assume corruption is a matter of time.
Use a decent regulator.
