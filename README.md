# Pi Model Looper

A small low power, efficient, practical video looper for small, low-power display builds.

Think Pi Zero, Zero W, older boards, and the kind of setup where you put the device inside a model, close it up, and don’t want to think about it again. I make and build models, gamng tables, hobby projects and such builds. So i needed a build that was efficient and liteweight to just play and forget.

This exists for model making and niche physical projects where you need:
- a small screen or cheap HDMI panel
- a loop of short clips
- low power draw
- predictable boot-to-play behaviour

It avoids “smart” features because smart features tend to become problems once the device is sealed inside something you’d rather not reopen.

## What this is, and what it isn’t

This is:
- a single-purpose playback loop for small Raspberry Pi boards. Its a lite weight small footprint build.
- a set-and-forget appliance mindset: boot, play, recover, repeat

This is absolutely not:
- a media centre..
- a streaming platform.--
- a framework
- a clever idea factory

It’s boring on purpose. Boring in this case is efficient.

## Non-goals (so this doesn’t grow extra limbs)

These are explicitly out of scope:
- streaming of any kind
- network dashboards or web UIs
- touchscreen interfaces
- dynamic playlists based on time, weather, mood, or astrology
- anything that increases SD card writes without a very good reason

If you want those things, build a different project. This one lives inside models.

## Hardware target

This repo is aimed at:
- Raspberry Pi Zero / Zero W
- Pi 1, Pi 2, Pi 3-class boards

-- Pi 4 and 5 are not the focus. They’re more capable, but that’s not the problem being solved here. Bigger hardware doesn’t magically make sealed builds easier to live with.

## Sealed model profile (recommended)

If this is going inside a sealed build, you want appliance behaviour, not flexibility.

Recommended defaults:
- `read_only = true`  
  Reduces SD card writes. Disables resume state writes and USB copy modes.
- modest bitrates  
  You don’t need cinema quality for a 5-inch panel. In fact foor this type of build thats he idea.
- no network services unless you genuinely need them
- test a dozen cold boots before you glue anything shut

If your media never changes, use read-only mode. You’ll thank yourself later.

## OS baseline and why it matters

This project assumes an older, stable Raspberry Pi OS baseline that still supports `omxplayer`.

That’s not me being nostalgic. It’s practicality, it works and its low resource rewuirements:
- lower overhead
- hardware decode that actually works on small boards
- fewer moving parts to break

If you want modern KMS or DRM pipelines, you can build them. And yes you’ll also spend more time debugging them than actually looping video. Grab another repo.

## Known-good panel resolutions

These are the cheap HDMI panels people actually use:
- 480×272 for very small dashboards
- 800×480 for common 5-inch panels
- 1024×600 for common 7-inch panels

If you encode to the panel’s native resolution, you reduce scaling work and avoid a lot of ugly tearing.

## Quick start (the tired version)

There’s a fuller checklist in `DEPLOYMENT.md`, especially for sealed builds.

Short version:
1. Put your videos in the configured media folder.
2. Install dependencies using `install.sh`, or do it manually if you don’t trust scripts. That’s honetly reasonable.
3. Configure `video_looper.ini`, or the `/boot` location the scripts expect.
4. Start the service. Supervisor is the default.

Then power-cycle the device.

If it only works while you’re SSH’d in, it doesn’t work.

## Project notes (maintainer voice)

A few things worth stating out loud:
- This is meant to live inside models. Access is limited. Power is flaky. Patience is thin.
- Features that increase UI surface area usually make things worse, not better.
- The right solution is the one that keeps playing without supervision.

If that means fewer features, so be it.

## Future ideas (not implemented on purpose)

These are ideas, not promises:
- backend abstraction so `omxplayer` stays the default for tiny boards, with room for `mpv` later
- fully deterministic state file locations, no relative paths, no surprises
- PID-based player control to avoid broad `pkill` patterns

All of these come with trade-offs. None of them are required for the core job.

## Hardening and efficiency tweaks (TABARC pass)

A few targeted changes that matter on Pi Zero-class hardware:
- PID or process-group based player stopping, not blanket `pkill`
- playlist resume state stored in a deterministic location, with a legacy fallback
- USB mount directories handled in Python rather than shelling out

Individually small changes. Collectively fewer subprocesses, fewer surprises, and less heat.

## Credit and provenance

This is not a fork in the “track upstream forever” sense.

It’s a specialised repo for a niche physical-build use case, built from known, working patterns and then trimmed down until it behaves.

## Branding

<p align="center">
  <img src=".branding/tabarc-icon.svg" width="180" alt="TABARC-Code Icon">
</p>

## This Version Contributor

TABARC-Code  
Project URI: https://github.com/TABARC-Code/  
Version: 1.1.0.4