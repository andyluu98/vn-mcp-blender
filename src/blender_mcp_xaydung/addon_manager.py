"""Cai file addon vao thu muc script cua Blender.

Nguoi dung van cai tay qua Edit > Preferences > Add-ons duoc. Module nay chi
lam cho nhanh: tim thu muc Blender tren may roi chep file addon vao dung cho.
"""

from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path

ADDON_FILENAME = "mcp_xaydung_addon.py"


def bundled_addon_path() -> Path:
    """Duong dan toi file addon di kem goi nay."""
    return Path(__file__).parent / "bundled" / "addon.py"


def _blender_config_roots() -> list[Path]:
    """Cac thu muc goc Blender luu cau hinh, tuy he dieu hanh."""
    system = platform.system()

    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            return []
        return [Path(appdata) / "Blender Foundation" / "Blender"]

    if system == "Darwin":
        return [Path.home() / "Library" / "Application Support" / "Blender"]

    # Linux va cac he con lai
    return [
        Path.home() / ".config" / "blender",
        Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "blender",
    ]


def find_addon_dirs() -> list[Path]:
    """Tim moi thu muc addons cua cac ban Blender dang co tren may.

    Tra ve danh sach sap theo so phien ban, moi nhat dung dau.
    """
    found: list[tuple[tuple, Path]] = []

    for root in _blender_config_roots():
        if not root.is_dir():
            continue
        for version_dir in root.iterdir():
            if not version_dir.is_dir():
                continue
            try:
                # Ten thu muc la so phien ban, vi du "4.2" hoac "5.2".
                key = tuple(int(p) for p in version_dir.name.split("."))
            except ValueError:
                continue
            found.append((key, version_dir / "scripts" / "addons"))

    found.sort(key=lambda item: item[0], reverse=True)
    return [path for _, path in found]


def install(target: Path | None = None) -> list[Path]:
    """Chep addon vao Blender. Tra ve danh sach duong dan da ghi.

    Khong truyen target thi cai cho moi ban Blender tim thay.
    """
    source = bundled_addon_path()
    if not source.is_file():
        raise FileNotFoundError(f"Khong thay file addon goc: {source}")

    targets = [target] if target else find_addon_dirs()
    if not targets:
        raise RuntimeError(
            "Khong tim thay thu muc addons cua Blender. "
            "Anh cai tay qua Edit > Preferences > Add-ons > Install, "
            f"chon file: {source}"
        )

    written: list[Path] = []
    for addon_dir in targets:
        addon_dir.mkdir(parents=True, exist_ok=True)
        dest = addon_dir / ADDON_FILENAME
        shutil.copyfile(source, dest)
        written.append(dest)

    return written
