from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Hermetic tests: never probe the real Steam libraries on the dev machine.
os.environ.setdefault("RIMWORLD_FORGE_OFFLINE", "1")

from rwforge.assets import emit_prompts
from rwforge.blueprints import blueprint_from_def
from rwforge.builder import build_project
from rwforge.generator import apply_plan, validate_plan
from rwforge.indexer import build_index, inspect_def, search_index
from rwforge.logs import analyze_log
from rwforge.mods import scan_mods
from rwforge.project import new_project
from rwforge.validator import validate_workspace


class ForgeTests(unittest.TestCase):
    def test_plan_validation_rejects_duplicate_defname(self):
        plan = {
            "schema": 1,
            "mod": {"name": "X", "packageId": "a.b"},
            "defs": [
                {"type": "ThingDef", "fields": {"defName": "A"}},
                {"type": "PawnKindDef", "fields": {"defName": "A"}},
            ],
        }
        result = validate_plan(plan)
        self.assertFalse(result["ok"])
        self.assertTrue(any("duplicate" in e for e in result["errors"]))

    def test_workspace_generate_validate_build(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td) / "Demo"
            new_project("Demo Mod", "tester.demo", workspace=ws)
            plan = {
                "schema": 1,
                "mod": {"name": "Demo Mod", "packageId": "tester.demo", "author": "Tester", "supportedVersions": ["1.6"], "description": "Demo"},
                "defs": [{"type": "ThingDef", "attributes": {"ParentName": "BaseThing"}, "fields": {"defName": "Tester_DemoThing", "label": "demo thing", "statBases": {"MarketValue": 10}}}],
                "assets": [],
            }
            plan_path = ws / "plans" / "demo.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            generated = apply_plan(ws, plan_path)
            self.assertTrue(generated["ok"])
            validation = validate_workspace(ws)
            self.assertTrue(validation["ok"], validation)
            built = build_project(ws)
            self.assertTrue(built["ok"], built)
            archive = Path(built["archive"])
            self.assertTrue(archive.is_file())
            with zipfile.ZipFile(archive) as zf:
                names = zf.namelist()
                self.assertTrue(any(x.endswith("About/About.xml") for x in names))
                self.assertTrue(any(x.endswith("Defs/Generated/ThingDefs.xml") for x in names))

    def test_index_search_and_inspect(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "RimWorld"
            defs = root / "Data" / "Core" / "Defs" / "ThingDefs"
            defs.mkdir(parents=True)
            (defs / "Test.xml").write_text("""<?xml version='1.0'?><Defs><ThingDef><defName>Test_Centipede</defName><label>test centipede</label></ThingDef></Defs>""", encoding="utf-8")
            index = Path(td) / "index.json"
            result = build_index(root, output=index)
            self.assertEqual(result["records"], 1)
            hits = search_index("centipede", index_path=index)
            self.assertEqual(hits[0]["def_name"], "Test_Centipede")
            record = inspect_def("Test_Centipede", index)
            self.assertIn("<defName>Test_Centipede</defName>", record["xml"])

    def test_log_analyzer_groups_errors(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "Player.log"
            log.write_text("hello\nCould not resolve cross-reference: No ThingDef named Nope\nNullReferenceException: x\n", encoding="utf-8")
            result = analyze_log(log)
            self.assertEqual(result["counts"]["cross_reference"], 1)
            self.assertEqual(result["counts"]["exception"], 1)

    def test_missing_texture_is_warning_not_fake_success_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            ws = Path(td) / "Demo"
            new_project("Demo Mod", "tester.demo", workspace=ws)
            defs = ws / "source" / "Defs" / "X.xml"
            defs.write_text("<Defs><ThingDef><defName>Tester_X</defName><graphicData><texPath>Tester/Missing</texPath></graphicData></ThingDef></Defs>", encoding="utf-8")
            result = validate_workspace(ws)
            self.assertTrue(result["ok"])
            self.assertTrue(any(w["code"] == "texture.missing" for w in result["warnings"]))

    def test_blueprint_from_indexed_def_and_art_prompts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "RimWorld"
            defs = root / "Data" / "Core" / "Defs"
            defs.mkdir(parents=True)
            (defs / "Weapon.xml").write_text("<Defs><ThingDef ParentName='BaseThing'><defName>Gun_Test</defName><label>test gun</label><statBases><MarketValue>100</MarketValue></statBases></ThingDef></Defs>", encoding="utf-8")
            index = Path(td) / "index.json"
            build_index(root, output=index)
            plan = Path(td) / "blueprint.json"
            result = blueprint_from_def("Gun_Test", "Tester_NewGun", plan, index, "tester.newgun", "New Gun")
            self.assertTrue(result["ok"])
            data = json.loads(plan.read_text(encoding="utf-8"))
            self.assertEqual(data["defs"][0]["attributes"]["ParentName"], "BaseThing")
            self.assertEqual(data["defs"][0]["fields"]["defName"], "Tester_NewGun")

            ws = Path(td) / "Art"
            new_project("Art", "tester.art", workspace=ws)
            (ws / "plans" / "ASSETS-NEEDED.json").write_text(json.dumps({"schema": 1, "assets": [{"id": "icon", "kind": "ui_icon", "target": "Textures/Test/Icon.png", "transparent": True, "canvas": [128,128], "notes": "sharp silhouette"}]}), encoding="utf-8")
            prompts = emit_prompts(ws)
            self.assertEqual(prompts["count"], 1)
            self.assertIn("production asset brief", Path(prompts["prompts"][0]).read_text(encoding="utf-8"))

    def test_mod_scan_detects_framework(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "RimWorld"
            (root / "Data" / "Core" / "Defs").mkdir(parents=True)
            about = root / "Mods" / "HAR" / "About"
            about.mkdir(parents=True)
            about.joinpath("About.xml").write_text("<ModMetaData><name>Humanoid Alien Races</name><author>x</author><packageId>erdelf.HumanoidAlienRaces</packageId><supportedVersions><li>1.6</li></supportedVersions><description>x</description></ModMetaData>", encoding="utf-8")
            result = scan_mods(root)
            har = next(x for x in result["frameworks"] if x["packageId"] == "erdelf.humanoidalienraces")
            self.assertTrue(har["installed"])

    def test_index_reads_versioned_mod_layouts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "RimWorld"
            (root / "Data" / "Core" / "Defs").mkdir(parents=True)
            # Workshop-style mod: defs under 1.6/, Common/ and LoadFolders.xml
            mod = root / "Mods" / "SomeWorkshopMod"
            for sub in ("Defs", "1.6/Defs", "Common/Defs"):
                d = mod / sub
                d.mkdir(parents=True)
                d.joinpath("D.xml").write_text(
                    f"<Defs><ThingDef><defName>Test_{sub.replace('/', '_')}</defName><label>x</label></ThingDef></Defs>",
                    encoding="utf-8",
                )
            # a 1.5-only defs dir must NOT be indexed
            old = mod / "1.5" / "Defs"
            old.mkdir(parents=True)
            old.joinpath("Old.xml").write_text("<Defs><ThingDef><defName>Test_Legacy</defName></ThingDef></Defs>", encoding="utf-8")
            index = Path(td) / "index.json"
            result = build_index(root, include_mods=root / "Mods", output=index)
            names = {r["def_name"] for r in json.loads(index.read_text(encoding="utf-8"))["records"]}
            self.assertIn("Test_Defs", names)
            self.assertIn("Test_1.6_Defs", names)
            self.assertIn("Test_Common_Defs", names)
            self.assertNotIn("Test_Legacy", names)

    def test_index_default_auto_discovers_workshop_roots(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "RimWorld"
            (root / "Data" / "Core" / "Defs").mkdir(parents=True)
            # game on library A (inside td), workshop content "elsewhere" (second dir in td)
            ws = Path(td) / "OtherLibrary" / "steamapps" / "workshop" / "content" / "294100"
            mod = ws / "555555"
            (mod / "1.6" / "Defs").mkdir(parents=True)
            (mod / "1.6" / "Defs" / "W.xml").write_text("<Defs><ThingDef><defName>Test_WSMod</defName></ThingDef></Defs>", encoding="utf-8")
            # no libraryfolders.vdf inside td; point discovery at the second library via env
            os.environ["RIMWORLD_WORKSHOP_ROOT"] = str(ws)
            try:
                index = Path(td) / "i.json"
                build_index(root, output=index)  # no include_mods -> auto-discovery
                names = {r["def_name"] for r in json.loads(index.read_text(encoding="utf-8"))["records"]}
                self.assertIn("Test_WSMod", names)
            finally:
                os.environ.pop("RIMWORLD_WORKSHOP_ROOT", None)

    def test_scan_mods_detects_framework_by_assembly_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "RimWorld"
            (root / "Data" / "Core" / "Defs").mkdir(parents=True)
            mod = root / "Mods" / "RenamedHarmonyRepack"
            (mod / "About").mkdir(parents=True)
            mod.joinpath("About", "About.xml").write_text("<ModMetaData><name>Some Repack</name><packageId>who.knows</packageId><supportedVersions><li>1.6</li></supportedVersions></ModMetaData>", encoding="utf-8")
            (mod / "1.6" / "Assemblies").mkdir(parents=True)
            (mod / "1.6" / "Assemblies" / "0Harmony.dll").write_bytes(b"MZ")
            result = scan_mods(root)
            harmony = next(f for f in result["frameworks"] if f["name"] == "Harmony")
            self.assertTrue(harmony["installed"])

    def test_log_analyzer_detects_duplicate_ref_storm(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "Player.log"
            storm_line = "InvalidCastException: Specified cast is not valid."
            dup = "[Ref 792923E] Duplicate stacktrace, see ref for original"
            log.write_text("start\n" + "\n".join([storm_line] + [dup] * 3000) + "\n", encoding="utf-8")
            result = analyze_log(log, max_hits=50)
            self.assertGreater(len(result["storms"]), 0)
            storm = max(result["storms"], key=lambda s: s["repeats"])
            self.assertGreaterEqual(storm["repeats"], 1000)
            self.assertEqual(storm["line"], 3)  # the [Ref X] dup line is the repeated one
            self.assertGreater(result["counts"]["duplicate_stack_ref"], 1000)
            self.assertTrue(any("FIRST block" in n for n in result["notes"]))


if __name__ == "__main__":
    unittest.main()
