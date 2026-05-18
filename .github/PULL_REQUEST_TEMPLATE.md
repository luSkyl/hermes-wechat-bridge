## Summary

<!-- What changed and why? -->

## Type

- [ ] Bug fix
- [ ] Feature
- [ ] Documentation
- [ ] Security hardening
- [ ] Compatibility / migration

## Checks

- [ ] `python -m pytest`
- [ ] `python -m bridge.cli doctor --config examples/minimal/config.yaml`
- [ ] `python -m bridge.cli simulate --config examples/minimal/config.yaml --event simulator/sample_events/text.json`
- [ ] Docs updated for user-visible behavior
- [ ] No real tokens, logs, private chat IDs, or runtime state included

## Compatibility

- Hermes contract affected: yes / no
- Web UI service API affected: yes / no
- WeChat callback/delivery affected: yes / no

## Notes for Reviewers

<!-- Risks, migration notes, screenshots, or sanitized logs. -->
