# Foundation verification report

Generated: 2026-08-29
Version: 0.1.0-foundation

## Verified in this artifact

- Python source compiles with `compileall`.
- 7/7 bundled unit tests pass.
- CLI capability smoke test passes.
- MCP initialize + tools/list smoke test passes and exposes exactly 11 tools.
- Warden example plan validates.
- Warden example generates a real workspace tree.
- Warden static validation passes XML/metadata checks while correctly reporting missing art as warnings.
- Generated projects build deterministic ZIPs with SHA-256 receipts in tests.
- Def index/search/inspect works against a synthetic RimWorld Data tree.
- Installed-Def to editable-plan blueprint conversion passes.
- Local mod/framework scanning detects HAR by packageId.
- Asset manifests emit image-generation production prompts.
- Player.log classifier detects cross-reference and exception signatures in tests.

## Not runtime-verified here

The execution environment used to build this artifact does not contain the user's RimWorld installation, so these require a real Windows/RimWorld machine:

- Steam library discovery against the user's install
- indexing the user's actual Core/DLC XML corpus
- C# compilation against the user's managed assemblies
- staging into the user's `RimWorld/Mods`
- RimWorld load test
- pawn/item spawn test
- visual validation

The Forge reports these as separate evidence tiers and does not infer them from the static test suite.

## GitHub integration status

Repository reads succeeded against `ShugokiFable/Ultimate-AI-Starter-Bundle`, SkyrimForge, RobloxForge, SaintsRowForge and FollowerForge. The GitHub connector returned HTTP 403 for both branch creation and file creation, so this artifact was not pushed into the user's repository.

`integration/BUNDLE-INTEGRATION.md` and `integration/PROFILES.fragment.json` contain the intended drop-in integration shape without modifying existing bundle files blindly.
