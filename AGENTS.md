# AGENTS.md

This repository is an agent skill. Its operating instructions live in `SKILL.md`.

When a user asks you to recommend websites, apps or online tools, asks whether a site is free or worth signing up for, or pastes a signup link, read `SKILL.md` and follow its workflow. Run the probe with `python3 scripts/probe.py <url>` (standard library only, read-only). Never sign up or enter the user's personal data on a site you are screening.

A Chinese edition of the same skill lives in `paywall-radar-zh/` (its own `SKILL.md`, references and a copy of the probe). Use it when the user writes in Chinese and only that folder is installed.
