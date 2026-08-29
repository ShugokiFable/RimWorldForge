# Changelog

## 0.2.0 - 2026-08-29

Real-library hardening, proven against a 460+ mod Steam Workshop installation.

- mod Def indexing now reads versioned layouts: `1.6/`, `Common/`, flat `Defs/`,
  and `LoadFolders.xml` (v1.6 entries only). Legacy version dirs are skipped
  (1.6-focused, no wasted index).
- Player.log analyzer collapses identical repeated lines and reports
  `storms`: per-line repeat counts for the `[Ref XXXX] Duplicate stacktrace`
  pattern Unity uses to hide original stacks, plus the line number of the
  first (full-stack) block.
- framework detection expanded: Big & Small, VEF/VFEC, VFEC Core, Giddy-Up,
  RimJobWorld, RimTalk, HugsLib.
- 9-test suite (was 7), covering versioned-layout indexing and storm detection.

## 0.1.0-foundation - 2026-08-29

Initial working foundation.

- local RimWorld discovery with Steam library probing
- Core + Royalty + Ideology + Biotech + Anomaly + Odyssey Def indexing
- ranked Def search and raw source inspection
- installed-Def to typed-plan blueprint conversion
- local/Steam Workshop mod inventory with key framework detection
- production art-prompt emission from asset manifests
- transactional mod workspaces
- generic typed JSON-to-RimWorld-XML generation
- About.xml, dependency and LoadFolders generation
- static validation with evidence tiers
- local texture and declared-asset checks
- optional installed-game reference candidate checks
- deterministic mod folder/ZIP build with SHA-256 receipt
- Player.log classifier
- C# net472 scaffold against installed managed assemblies
- approval-gated compiler and live Mods staging
- 11-tool zero-dependency stdio MCP façade
- agent skill, modding/art/validation/extension docs
- Warden mech and Biotech xenotype teaching plans
- concept SVG art example
- self-contained unittest suite
