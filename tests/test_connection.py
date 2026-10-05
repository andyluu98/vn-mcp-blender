"""Kiem tra giao thuc socket giua MCP server va addon.

Test dung mot socket gia dong vai addon, khong can mo Blender.
"""

import json
import socket
import struct
import threading

import pytest

from blender_mcp_xaydung.connection import (
    BlenderCommandError,
    BlenderConnection,
    BlenderConnectionError,
)


class AddonGia:
    """Socket nghe mot ket noi roi tra ve cau tra loi dinh san."""

    def __init__(self, tra_loi, chia_nho=False):
        self.tra_loi = tra_loi
        self.chia_nho = chia_nho
        self.nhan_duoc = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("localhost", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]
        self.thread = threading.Thread(target=self._chay, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        try:
            self.sock.close()
        except OSError:
            pass

    def _chay(self):
        try:
            client, _ = self.sock.accept()
        except OSError:
            return

        with client:
            header = client.recv(4)
            if len(header) < 4:
                return
            (length,) = struct.unpack(">I", header)

            body = b""
            while len(body) < length:
                chunk = client.recv(length - len(body))
                if not chunk:
                    return
                body += chunk
            self.nhan_duoc = json.loads(body.decode("utf-8"))

            data = json.dumps(self.tra_loi, ensure_ascii=False).encode("utf-8")
            payload = struct.pack(">I", len(data)) + data

            if self.chia_nho:
                # Gui tung byte mot de chac chan ben nhan ghep lai dung.
                for i in range(len(payload)):
                    client.sendall(payload[i:i + 1])
            else:
                client.sendall(payload)


def test_gui_va_nhan_duoc():
    with AddonGia({"status": "success", "result": {"ok": True}}) as addon:
        conn = BlenderConnection(port=addon.port, timeout=5)
        ket_qua = conn.send("get_status", {"a": 1})

    assert ket_qua == {"ok": True}
    assert addon.nhan_duoc == {"type": "get_status", "params": {"a": 1}}


def test_ghep_dung_khi_du_lieu_ve_tung_manh():
    """Socket co the tra ve tung manh nho, ben nhan phai ghep lai du."""
    lon = {"status": "success", "result": {"text": "x" * 500}}
    with AddonGia(lon, chia_nho=True) as addon:
        conn = BlenderConnection(port=addon.port, timeout=10)
        ket_qua = conn.send("test")

    assert len(ket_qua["text"]) == 500


def test_giu_duoc_tieng_viet_co_dau():
    tra_loi = {"status": "success", "result": {"ten": "Tuong gạch 220 phòng ngủ"}}
    with AddonGia(tra_loi) as addon:
        conn = BlenderConnection(port=addon.port, timeout=5)
        ket_qua = conn.send("test")

    assert ket_qua["ten"] == "Tuong gạch 220 phòng ngủ"


def test_loi_tu_addon_thanh_ngoai_le():
    with AddonGia({"status": "error", "message": "Khong co tuong ten 'X'"}) as addon:
        conn = BlenderConnection(port=addon.port, timeout=5)
        with pytest.raises(BlenderCommandError, match="Khong co tuong"):
            conn.send("get_object_info")


def test_bao_loi_ro_rang_khi_blender_chua_bat():
    # Cong nay gan nhu chac chan khong co ai nghe.
    conn = BlenderConnection(port=59999, timeout=2)
    with pytest.raises(BlenderConnectionError) as exc:
        conn.send("ping")

    text = str(exc.value)
    assert "MCP Xay Dung" in text, "Thong bao phai chi ro cach bat addon"


def test_bao_loi_khi_mat_ket_noi_giua_chung():
    """Addon dong may giua chung thi phai bao loi, khong treo."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", 0))
    sock.listen(1)
    port = sock.getsockname()[1]

    def cat_ngang():
        client, _ = sock.accept()
        client.recv(4096)
        # Hua tra ve 1000 byte roi dong luon sau 4 byte.
        client.sendall(struct.pack(">I", 1000) + b"abcd")
        client.close()

    thread = threading.Thread(target=cat_ngang, daemon=True)
    thread.start()

    try:
        conn = BlenderConnection(port=port, timeout=5)
        with pytest.raises(BlenderConnectionError, match="dong ket noi"):
            conn.send("ping")
    finally:
        sock.close()
