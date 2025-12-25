# Changelog

## 1.1.0.1
- Read-only mode forces directory reader (no USB mount/copy readers).
- Heartbeat file now updates during playback, not just between files.
- Added DEPLOYMENT.md checklist for sealed model builds.


## 1.1.0.0
- Added read-only mode for sealed builds (reduce SD writes; disable resume writes and USB copy behaviour).
- Atomic resume state writes (temp file + replace) so power loss doesn’t corrupt state.
- Media preflight (skip zero-byte/unknown files; don't thrash).
- Hardware model warning (Pi 4/5 not target).
- Optional alive file heartbeat for external supervision.
- Documented panel resolutions and non-goals.


## 1.0.0.3
- Reduced busy-wait behaviour in the main loop (adaptive sleep instead of 2ms spin).
- hello_video helper avoids `sleep(0)` and uses terminate→kill escalation.
- USB mounter loop avoids busy waiting.


## 1.0.0.2
- Player stop now targets the process group we started (less collateral damage than `pkill -9`).
- Playlist resume state stored in a deterministic location (XDG state dir / /var/lib / /tmp), with legacy fallback.
- USB mount folder create/remove uses Python helpers with root-prefix safety checks.

## 1.0.0.1
- Initial TABARC niche-repo framing for model-making projects.
