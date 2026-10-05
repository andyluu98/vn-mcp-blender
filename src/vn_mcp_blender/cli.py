"""Dong lenh cua vn-mcp-blender.

Khong co lenh con thi chay MCP server, day la cach Claude goi toi.
Lenh con 'install-addon' chep addon vao Blender, 'check' thu ket noi.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__, addon_manager
from .connection import BlenderConnectionError, get_connection


def _cmd_install_addon(args: argparse.Namespace) -> int:
    from pathlib import Path

    try:
        written = addon_manager.install(Path(args.thu_muc) if args.thu_muc else None)
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1

    print("Đã chép addon vào:")
    for path in written:
        print(f"  {path}")
    print()
    print("Tiếp theo, trong Blender:")
    print("  1. Edit > Preferences > Add-ons")
    print("  2. Tìm 'MCP Xây Dựng' rồi tích vào ô bên trái để bật")
    print("  3. Trong khung nhìn 3D, bấm phím N để mở thanh bên")
    print("  4. Chọn tab 'MCP Xây Dựng' rồi bấm 'Bật kết nối'")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    conn = get_connection()
    conn.port = args.cong
    try:
        result = conn.send("get_status")
    except BlenderConnectionError as exc:
        print(f"Chưa nối được: {exc}", file=sys.stderr)
        return 1

    print("Nối được tới Blender.")
    for key, value in result.items():
        print(f"  {key}: {value}")
    return 0


def _cmd_addon_path(args: argparse.Namespace) -> int:
    print(addon_manager.bundled_addon_path())
    dirs = addon_manager.find_addon_dirs()
    if dirs:
        print("\nThư mục addons tìm thấy trên máy:")
        for d in dirs:
            print(f"  {d}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vn-mcp-blender",
        description="MCP server dựng mô hình nhà 3D trong Blender.",
    )
    parser.add_argument("--version", action="version", version=__version__)

    sub = parser.add_subparsers(dest="lenh")

    p_install = sub.add_parser("install-addon", help="Chép addon vào Blender")
    p_install.add_argument("--thu-muc", help="Chỉ định thư mục addons cụ thể")
    p_install.set_defaults(func=_cmd_install_addon)

    p_check = sub.add_parser("check", help="Thử kết nối tới Blender")
    p_check.add_argument("--cong", type=int, default=9877, help="Cổng TCP")
    p_check.set_defaults(func=_cmd_check)

    p_path = sub.add_parser("addon-path", help="In đường dẫn file addon")
    p_path.set_defaults(func=_cmd_addon_path)

    args = parser.parse_args(argv)

    if args.lenh is None:
        # Khong co lenh con thi chay MCP server tren stdio.
        from .server import main as run_server
        run_server()
        return 0

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
