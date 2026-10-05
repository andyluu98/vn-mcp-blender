"""Doc mat bang DXF va rut ra du lieu dung nha.

Ban ve kien truc Viet Nam thuong ve tuong bang polyline kin, mot hinh chu nhat
rat det: canh dai la chieu dai tuong, canh ngan la be day. Module nay nhan ra
cac hinh do roi tra ve truc tim tuong kem be day, de addon dung khoi 3D.

Don vi trong DXF thuong la milimet, con Blender dung met, nen moi so deu duoc
chia cho 1000 truoc khi tra ve. Doi ty_le neu ban ve cua anh dung don vi khac.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

try:
    import ezdxf
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Thieu thu vien ezdxf. Cai bang: pip install ezdxf"
    ) from exc

# Ty le doi tu don vi ban ve sang met. Ban ve mm thi chia 1000.
TY_LE_MM = 0.001

# Mot hinh chu nhat duoc coi la tuong khi canh dai gap canh ngan it nhat chung nay.
TY_SO_DET_TOI_THIEU = 2.5

# Ten layer hay gap trong ho so Viet Nam, dung lam mac dinh.
LAYER_TUONG_MAC_DINH = ("A-WALL-220", "A-WALL-110", "A-WALL", "TUONG")
LAYER_COT_MAC_DINH = ("A-COL", "COT", "A-COLUMN")


@dataclass
class Tuong:
    """Mot doan tuong rut ra tu ban ve."""

    diem_dau: tuple
    diem_cuoi: tuple
    day: float
    layer: str

    @property
    def dai(self) -> float:
        return math.dist(self.diem_dau, self.diem_cuoi)

    def to_dict(self) -> dict:
        return {
            "diem_dau": [round(v, 4) for v in self.diem_dau],
            "diem_cuoi": [round(v, 4) for v in self.diem_cuoi],
            "day": round(self.day, 4),
            "dai": round(self.dai, 4),
            "layer": self.layer,
        }


@dataclass
class Cot:
    """Mot cot rut ra tu ban ve."""

    tam: tuple
    rong: float
    sau: float
    layer: str

    def to_dict(self) -> dict:
        return {
            "tam": [round(v, 4) for v in self.tam],
            "rong": round(self.rong, 4),
            "sau": round(self.sau, 4),
            "layer": self.layer,
        }


@dataclass
class MatBang:
    """Toan bo du lieu rut ra tu mot mat bang."""

    tuong: list = field(default_factory=list)
    cot: list = field(default_factory=list)
    pham_vi: tuple = (0.0, 0.0, 0.0, 0.0)

    def to_dict(self) -> dict:
        return {
            "tuong": [t.to_dict() for t in self.tuong],
            "cot": [c.to_dict() for c in self.cot],
            "so_tuong": len(self.tuong),
            "so_cot": len(self.cot),
            "pham_vi": [round(v, 4) for v in self.pham_vi],
        }


def _polyline_points(entity) -> list:
    """Lay danh sach dinh (x, y) cua mot LWPOLYLINE."""
    return [(p[0], p[1]) for p in entity.get_points("xy")]


def _dedupe(points: list, eps: float = 1e-6) -> list:
    """Bo cac dinh trung nhau lien tiep, ke ca dinh cuoi trung dinh dau."""
    out: list = []
    for p in points:
        if not out or math.dist(p, out[-1]) > eps:
            out.append(p)
    if len(out) > 1 and math.dist(out[0], out[-1]) <= eps:
        out.pop()
    return out


def _oriented_box(points: list):
    """Tim hop bao xoay theo canh dai nhat.

    Tra ve (diem_dau, diem_cuoi, be_day) voi diem_dau va diem_cuoi nam tren
    truc tim, hoac None neu hinh khong du det de coi la tuong.
    """
    pts = _dedupe(points)
    if len(pts) < 3:
        return None

    # Huong cua hinh lay theo canh dai nhat.
    best_len, ux, uy = 0.0, 1.0, 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        d = math.hypot(x2 - x1, y2 - y1)
        if d > best_len:
            best_len, ux, uy = d, (x2 - x1) / d, (y2 - y1) / d

    if best_len <= 0:
        return None

    # Chieu moi dinh len truc doc u va truc ngang v de lay pham vi.
    vx, vy = -uy, ux
    ts = [p[0] * ux + p[1] * uy for p in pts]
    ss = [p[0] * vx + p[1] * vy for p in pts]

    t_min, t_max = min(ts), max(ts)
    s_min, s_max = min(ss), max(ss)

    dai = t_max - t_min
    day = s_max - s_min
    if day <= 0 or dai / day < TY_SO_DET_TOI_THIEU:
        return None

    # Truc tim nam giua hai canh dai.
    s_mid = (s_min + s_max) / 2.0
    start = (ux * t_min + vx * s_mid, uy * t_min + vy * s_mid)
    end = (ux * t_max + vx * s_mid, uy * t_max + vy * s_mid)
    return start, end, day


def _axis_box(points: list):
    """Hop bao theo truc toa do, dung cho cot vuong. Tra ve (tam, rong, sau)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    rong, sau = max(xs) - min(xs), max(ys) - min(ys)
    tam = ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0)
    return tam, rong, sau


def _in_region(x: float, y: float, vung) -> bool:
    if vung is None:
        return True
    x0, y0, x1, y1 = vung
    return x0 <= x <= x1 and y0 <= y <= y1


def doc_mat_bang(
    duong_dan: str,
    layer_tuong=LAYER_TUONG_MAC_DINH,
    layer_cot=LAYER_COT_MAC_DINH,
    vung=None,
    ty_le: float = TY_LE_MM,
    goc=(0.0, 0.0),
) -> MatBang:
    """Doc mot file DXF va rut ra tuong, cot.

    duong_dan: file .dxf can doc.
    layer_tuong, layer_cot: ten cac layer chua tuong va cot.
    vung: [x0, y0, x1, y1] theo don vi ban ve, de lay rieng mot mat bang khi
          ho so xep nhieu mat bang canh nhau tren cung mot khong gian.
    ty_le: he so doi sang met. Ban ve mm dung 0.001.
    goc: [x, y] theo don vi ban ve, se duoc dua ve goc toa do 0,0.
    """
    doc = ezdxf.readfile(duong_dan)
    msp = doc.modelspace()

    wall_layers = {s.upper() for s in layer_tuong}
    col_layers = {s.upper() for s in layer_cot}

    ket_qua = MatBang()
    xs_all: list = []
    ys_all: list = []

    def to_world(p):
        """Doi mot diem tu don vi ban ve sang met, da tru goc."""
        return ((p[0] - goc[0]) * ty_le, (p[1] - goc[1]) * ty_le)

    for entity in msp:
        if entity.dxftype() != "LWPOLYLINE":
            continue

        layer = entity.dxf.layer
        upper = layer.upper()
        points = _polyline_points(entity)
        if len(points) < 3:
            continue

        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
        if not _in_region(cx, cy, vung):
            continue

        if upper in wall_layers:
            box = _oriented_box(points)
            if box is None:
                continue
            start, end, day = box
            ket_qua.tuong.append(Tuong(
                diem_dau=to_world(start),
                diem_cuoi=to_world(end),
                day=day * ty_le,
                layer=layer,
            ))
            xs_all += [p[0] for p in points]
            ys_all += [p[1] for p in points]

        elif upper in col_layers:
            tam, rong, sau = _axis_box(points)
            ket_qua.cot.append(Cot(
                tam=to_world(tam),
                rong=rong * ty_le,
                sau=sau * ty_le,
                layer=layer,
            ))
            xs_all += [p[0] for p in points]
            ys_all += [p[1] for p in points]

    if xs_all:
        ket_qua.pham_vi = (
            (min(xs_all) - goc[0]) * ty_le, (min(ys_all) - goc[1]) * ty_le,
            (max(xs_all) - goc[0]) * ty_le, (max(ys_all) - goc[1]) * ty_le,
        )

    return ket_qua


def liet_ke_layer(duong_dan: str) -> dict:
    """Liet ke layer trong file DXF kem so luong doi tuong, de biet chon layer nao."""
    doc = ezdxf.readfile(duong_dan)
    msp = doc.modelspace()

    dem: dict = {}
    for entity in msp:
        key = entity.dxf.layer
        info = dem.setdefault(key, {})
        info[entity.dxftype()] = info.get(entity.dxftype(), 0) + 1

    return {
        "so_layer": len(dem),
        "layer": {k: dem[k] for k in sorted(dem)},
        "tong_doi_tuong": sum(sum(v.values()) for v in dem.values()),
    }
