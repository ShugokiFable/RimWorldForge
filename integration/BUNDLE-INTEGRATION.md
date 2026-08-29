# Ultimate AI Starter Bundle integration

This folder is intended to live at:

```text
Ultimate-AI-Starter-Bundle/
  BUNDLED-TOOLS/
    rimworld-forge/
```

The standalone `ShugokiFable/RimWorldForge` repository can later mirror this source, following the same source-of-truth pattern as Skyrim Forge.

## Recommended pack behavior

### Install

Keep RimWorldForge installed as a zero-standing-token local tool/skill. Do **not** connect its MCP globally.

Run its own `Install.ps1 -SkipTests` from the bundle installer or let a game-specific optional step invoke it. The Forge has no third-party Python dependencies.

Set:

```text
RIMWORLD_FORGE_ROOT=<bundle>\BUNDLED-TOOLS\rimworld-forge
```

or the installed copy if the bundle later chooses to deploy it elsewhere.

### Profile

Add the profile in `integration/PROFILES.fragment.json` to `BUNDLED-TOOLS/PROFILES.json` after adapting version metadata.

The detection markers intentionally target a Forge workspace or a normal RimWorld mod source tree, not arbitrary C# projects.

For providers without project-scoped MCP support, use the skill + CLI instead of registering the server globally.

### Skill

Copy `skills/rimworld-forge/SKILL.md` through the bundle's normal provider-skill installer. The skill is the router and costs almost nothing until a RimWorld request matches. The 11-tool MCP is the execution surface and should remain parked outside RimWorld work.

## Why the Forge is vendored instead of fetched

It is tightly coupled to the bundle's agent workflow, evidence vocabulary, token discipline and installer conventions. Developing it under `BUNDLED-TOOLS/rimworld-forge` lets one commit test the Forge and the pack integration together. A public standalone repo can be a release mirror.

## Not patched automatically in this artifact

The pack's GitHub connector was read-only during foundation creation, so the following existing bundle files were deliberately left untouched rather than guessed or partially rewritten:

- `INSTALL-AIO.ps1`
- `BUNDLED-TOOLS/PROFILES.json`
- global skill catalog/manifests
- pack version/changelog

The fragments here are the intended integration inputs once those files can be modified and tested in the real bundle checkout.
