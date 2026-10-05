"""Soat code Python truoc khi gui vao Blender chay.

Tool execute_blender_code cho phep chay Python bat ky ben trong Blender. Do la
thu manh nhat cua bo nay, nhung cung la cho nguy hiem nhat: code chay voi day
du quyen cua nguoi dung, doc ghi xoa duoc moi file tren may.

Lop nay doc code thanh cay cu phap (AST) roi tim cac mau nguy hiem. No khong
thay the viec nguoi dung doc code truoc khi chay, chi chan nhung loi ro rang.
Dat VN_MCP_UNSAFE=1 de tat, nhung chi lam vay khi hieu ro rui ro.
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass, field

# Module khong duoc phep nhap: dung duoc de xoa file, chay lenh he thong,
# hoac mo ket noi mang ra ngoai.
BLOCKED_MODULES = frozenset({
    "subprocess", "shutil", "ctypes", "socket", "socketserver",
    "multiprocessing", "http", "urllib", "ftplib", "smtplib",
    "telnetlib", "pty", "pickle", "marshal", "importlib",
})

# Ham dung san khong duoc goi.
BLOCKED_BUILTINS = frozenset({
    "eval", "exec", "compile", "__import__", "breakpoint", "input",
})

# Thuoc tinh nguy hiem tren module os.
BLOCKED_OS_ATTRS = frozenset({
    "remove", "unlink", "rmdir", "removedirs", "system", "popen",
    "execv", "execve", "execl", "execlp", "spawnv", "kill", "killpg",
    "chmod", "chown", "rename", "replace", "truncate",
})

# Lenh Blender gay mat du lieu hoac dong chuong trinh.
BLOCKED_BPY_OPS = frozenset({
    "quit_blender", "read_factory_settings", "read_homefile",
    "open_mainfile", "recover_last_session",
})

# Thuoc tinh noi bo dung de pha rao chan.
BLOCKED_DUNDERS = frozenset({
    "__subclasses__", "__bases__", "__globals__", "__code__",
    "__closure__", "__builtins__", "__loader__", "__spec__",
})


@dataclass
class ScanResult:
    """Ket qua soat mot doan code."""

    safe: bool
    reasons: list[str] = field(default_factory=list)

    def message(self) -> str:
        lines = ["Code bi chan vi cac ly do sau:"]
        lines += [f"  - {r}" for r in self.reasons]
        lines.append(
            "Neu anh chac chan doan code nay an toan, dat bien moi truong "
            "VN_MCP_UNSAFE=1 roi khoi dong lai MCP server."
        )
        return "\n".join(lines)


def unsafe_mode_enabled() -> bool:
    """Nguoi dung da tu tat lop soat nay chua."""
    return os.environ.get("VN_MCP_UNSAFE", "").strip().lower() in {"1", "true", "yes"}


def _attr_chain(node: ast.Attribute) -> list[str]:
    """Bien node cua a.b.c thanh danh sach ['a', 'b', 'c']."""
    parts: list[str] = []
    cur: ast.AST = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
    return list(reversed(parts))


def _literal_mode_arg(node: ast.Call) -> str | None:
    """Lay che do mo file neu no duoc viet thang thanh chuoi hang."""
    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
        value = node.args[1].value
        if isinstance(value, str):
            return value
    for kw in node.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            if isinstance(kw.value.value, str):
                return kw.value.value
    return None


class _Scanner(ast.NodeVisitor):
    """Di khap cay cu phap va ghi lai moi cho dang ngo."""

    def __init__(self) -> None:
        self.reasons: list[str] = []

    def _flag(self, node: ast.AST, text: str) -> None:
        line = getattr(node, "lineno", "?")
        self.reasons.append(f"dong {line}: {text}")

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root in BLOCKED_MODULES:
                self._flag(node, f"nhap module bi chan '{alias.name}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        root = (node.module or "").split(".")[0]
        if root in BLOCKED_MODULES:
            self._flag(node, f"nhap tu module bi chan '{node.module}'")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func

        if isinstance(func, ast.Name):
            if func.id in BLOCKED_BUILTINS:
                self._flag(node, f"goi ham bi chan '{func.id}()'")
            elif func.id == "open":
                mode = _literal_mode_arg(node)
                if mode and any(ch in mode for ch in "wxa+"):
                    self._flag(node, f"mo file de ghi voi che do '{mode}'")

        elif isinstance(func, ast.Attribute):
            chain = _attr_chain(func)
            if len(chain) >= 2 and chain[0] == "os" and chain[-1] in BLOCKED_OS_ATTRS:
                name = ".".join(chain)
                self._flag(node, f"goi '{name}()' co the xoa file hoac chay lenh he thong")
            if len(chain) >= 3 and chain[0] == "bpy" and chain[1] == "ops":
                if chain[-1] in BLOCKED_BPY_OPS:
                    name = ".".join(chain)
                    self._flag(node, f"goi '{name}()' lam mat ban ve dang mo")

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr in BLOCKED_DUNDERS:
            self._flag(node, f"truy cap thuoc tinh noi bo '{node.attr}'")
        self.generic_visit(node)


def scan(code: str) -> ScanResult:
    """Soat doan code, tra ve ket qua kem ly do neu bi chan."""
    if unsafe_mode_enabled():
        return ScanResult(safe=True)

    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return ScanResult(safe=False, reasons=[f"code sai cu phap Python: {exc}"])

    scanner = _Scanner()
    scanner.visit(tree)
    return ScanResult(safe=not scanner.reasons, reasons=scanner.reasons)
