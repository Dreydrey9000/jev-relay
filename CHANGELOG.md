# Changelog

## [2026-10-13]
### Fixed
- The Laya worker's time limit is now the `local_timeout` setting (default 180 seconds, allowed 10 to 600) instead of a fixed 60. On Drey's Mac a cold model load alone ran past 60 seconds, so the local lane always returned nothing.
### Added
- Three tests in `tests/test_router.py`: the default limit, a configured limit, and out-of-range values refusing before any worker starts.

## [2026-09-30]
### Added
- OpenJev local backend (`"local_backend": "openjev"`): the routine lane can use an already-running OpenJev verdict service instead of loading a model, so Linux hosts like Jax get local advice instead of `local_disabled`.
- `tests/test_openjev.py`: option mapping, renormalization, score and yes/no answers, loopback-only URL, service-down handoff, and no cloud call on the routine lane.
### Changed
- README "What is actually connected" table, config example, and the how-it-works diagram now show both local backends.
