from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, Any

from .discovery import discover_game

KNOWN_FRAMEWORKS = {
    "erdelf.humanoidalienraces": "Humanoid Alien Races",
    "brrainz.harmony": "Harmony",
    "smashphil.vehicleframework": "Vehicle Framework",
    "redmattis.bigsmall.core": "Big & Small Core",
    "oskarpotocki.vanillafactionsexpanded.core": "Vanilla Factions Expanded - Core",
    "vanillaexpanded.vfecore": "Vanilla Expanded Framework",
    "memegoddess.giddyup": "Giddy-Up",
    "rim.job.world": "RimJobWorld",
    "cj.rimtalk": "RimTalk",
    "unlimitedhugs.hugslib": "HugsLib",
    "smashphil.vanillaexpandedframework": "VEF (legacy id)",
}


def _workshop_root(game_root: Path) -> Path | None:
    # <SteamLibrary>/steamapps/common/RimWorld -> <SteamLibrary>/steamapps/workshop/content/294100
    try:
        steamapps = game_root.parents[1]
        p = steamapps / "workshop" / "content" / "294100"
        return p if p.is_dir() else None
    except IndexError:
        return None


def mod_roots(game_root: Path) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    local = game_root / "Mods"
    if local.is_dir():
        roots.append(("local", local))
    workshop = _workshop_root(game_root)
    if workshop:
        roots.append(("workshop", workshop))
    extra = os.environ.get("RIMWORLD_MODS_ROOT")
    if extra:
        p = Path(extra).expanduser()
        if p.is_dir():
            roots.append(("extra", p))
    return roots


def _parse_about(path: Path, origin: str) -> dict[str, Any] | None:
    try:
        root = ET.parse(path).getroot()
        if root.tag != "ModMetaData":
            return None
        pid = (root.findtext("packageId") or "").strip()
        if not pid:
            return None
        return {
            "origin": origin,
            "root": str(path.parent.parent),
            "name": (root.findtext("name") or path.parent.parent.name).strip(),
            "packageId": pid,
            "author": (root.findtext("author") or "").strip() or None,
            "supportedVersions": [(x.text or "").strip() for x in root.findall("./supportedVersions/li") if (x.text or "").strip()],
            "dependencies": [(x.text or "").strip() for x in root.findall("./modDependencies/li/packageId") if (x.text or "").strip()],
        }
    except (ET.ParseError, OSError):
        return None


def scan_mods(game_root: Path) -> dict[str, Any]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for origin, root in mod_roots(game_root):
        for child in sorted(p for p in root.iterdir() if p.is_dir()):
            about = child / "About" / "About.xml"
            if not about.is_file():
                continue
            rec = _parse_about(about, origin)
            if not rec:
                continue
            key = rec["packageId"].lower()
            if key in seen:
                rec["duplicatePackageId"] = True
            seen.add(key)
            found.append(rec)
    frameworks = []
    for pid, title in KNOWN_FRAMEWORKS.items():
        matches = [m for m in found if m["packageId"].lower() == pid]
        frameworks.append({"packageId": pid, "name": title, "installed": bool(matches), "matches": matches})
    return {"ok": True, "mods": found, "count": len(found), "frameworks": frameworks, "roots": [{"origin": o, "path": str(p)} for o, p in mod_roots(game_root)]}
