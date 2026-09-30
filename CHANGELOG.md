# Changelog

## [2026-09-30]
### Added
- OpenJev local backend (`"local_backend": "openjev"`): the routine lane can use an already-running OpenJev verdict service instead of loading a model, so Linux hosts like Jax get local advice instead of `local_disabled`.
- `tests/test_openjev.py`: option mapping, renormalization, score and yes/no answers, loopback-only URL, service-down handoff, and no cloud call on the routine lane.
### Changed
- README "What is actually connected" table, config example, and the how-it-works diagram now show both local backends.
