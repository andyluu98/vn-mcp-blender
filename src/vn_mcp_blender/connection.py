"""Client socket noi toi addon chay ben trong Blender.

Giao thuc: moi ban tin gom 4 byte do dai (big-endian, khong dau) roi den
phan than la JSON ma hoa UTF-8. Cach dong goi nay tranh phai doan khi nao
mot ban tin ket thuc, khac voi kieu doc den khi JSON parse duoc.

    Yeu cau : {"type": "ten_lenh", "params": {...}}
    Tra loi : {"status": "success", "result": {...}}
              {"status": "error",   "message": "mo ta loi"}
"""

from __future__ import annotations

import json
import socket
import struct
from dataclasses import dataclass
from typing import Any

from . import DEFAULT_HOST, DEFAULT_PORT

# Do dai toi da mot ban tin, chan khong cho addon loi lam treo server
MAX_MESSAGE_BYTES = 64 * 1024 * 1024

# Thoi gian cho mac dinh. Dung nha co the ton vai giay nen de rong rai.
DEFAULT_TIMEOUT = 120.0

# Thoi gian cho rieng cho buoc bat tay. Addon dang chay thi tra loi gan nhu
# tuc thi, nen cho lau hon chi lam nguoi dung doi vo ich.
CONNECT_TIMEOUT = 3.0


class BlenderConnectionError(RuntimeError):
    """Khong noi duoc toi Blender, hoac mat ket noi giua chung."""


class BlenderCommandError(RuntimeError):
    """Addon nhan duoc lenh nhung thuc thi that bai."""


def _recv_exactly(sock: socket.socket, n: int) -> bytes:
    """Doc du dung n byte. Socket co the tra ve tung manh nho."""
    chunks = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(min(remaining, 1 << 20))
        if not chunk:
            raise BlenderConnectionError(
                "Blender đóng kết nối giữa chừng. Kiểm tra addon còn bật không."
            )
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


@dataclass
class BlenderConnection:
    """Moi lenh mo mot ket noi moi roi dong lai.

    Giu ket noi lau de bi treo khi nguoi dung tat mo Blender, nen cach nay
    don gian va ben hon. Chi phi mo socket noi bo khong dang ke.
    """

    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    timeout: float = DEFAULT_TIMEOUT

    def _huong_dan_bat_addon(self) -> str:
        return (
            f"Không nối được tới Blender ở {self.host}:{self.port}. "
            "Mở Blender, vào thanh bên khung nhìn 3D (phím N), "
            "chọn tab 'MCP Xây Dựng', rồi bấm 'Bật kết nối'."
        )

    def _mo_ket_noi(self) -> socket.socket:
        """Mo socket toi addon.

        Tach rieng khoi buoc gui nhan de phan biet hai loai that bai: chua noi
        duoc toi Blender, va noi duoc nhung Blender dang ban. Hai truong hop
        nay can hai cach xu ly khac nhau nen khong duoc gop chung thong bao.
        """
        try:
            # Han thoi gian bat tay ngan, vi addon dang chay thi no tra loi ngay.
            # Mot ket noi lau hon the gan nhu chac chan la khong co ai nghe.
            return socket.create_connection(
                (self.host, self.port),
                timeout=min(self.timeout, CONNECT_TIMEOUT),
            )
        except ConnectionRefusedError as exc:
            raise BlenderConnectionError(self._huong_dan_bat_addon()) from exc
        except socket.timeout as exc:
            # Tuong lua hoac cong bi chan thi goi tin bi bo im lang thay vi
            # bi tu choi, nen phai bat ca truong hop nay.
            raise BlenderConnectionError(self._huong_dan_bat_addon()) from exc
        except OSError as exc:
            raise BlenderConnectionError(
                f"{self._huong_dan_bat_addon()} Chi tiết lỗi: {exc}"
            ) from exc

    def send(self, command_type: str, params: dict[str, Any] | None = None) -> Any:
        """Gui mot lenh va tra ve phan 'result' trong cau tra loi."""
        payload = json.dumps(
            {"type": command_type, "params": params or {}},
            ensure_ascii=False,
        ).encode("utf-8")

        sock = self._mo_ket_noi()
        try:
            with sock:
                sock.settimeout(self.timeout)
                sock.sendall(struct.pack(">I", len(payload)) + payload)

                (length,) = struct.unpack(">I", _recv_exactly(sock, 4))
                if length > MAX_MESSAGE_BYTES:
                    raise BlenderConnectionError(
                        f"Addon trả về bản tin quá lớn ({length} byte)."
                    )
                body = _recv_exactly(sock, length)
        except socket.timeout as exc:
            raise BlenderConnectionError(
                f"Blender không trả lời lệnh '{command_type}' trong "
                f"{self.timeout} giây. Có thể đang bận xử lý một lệnh nặng, "
                "hoặc addon gặp lỗi. Xem cửa sổ Console trong Blender."
            ) from exc
        except OSError as exc:
            raise BlenderConnectionError(
                f"Mất kết nối khi đang chạy lệnh '{command_type}': {exc}"
            ) from exc

        try:
            response = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise BlenderConnectionError(
                f"Addon trả về dữ liệu không đọc được: {exc}"
            ) from exc

        if response.get("status") == "error":
            raise BlenderCommandError(
                response.get("message", "Lỗi không rõ từ addon.")
            )

        return response.get("result")


_shared = BlenderConnection()


def get_connection() -> BlenderConnection:
    """Tra ve ket noi dung chung cho ca server."""
    return _shared
