"""Addon Blender cho MCP Xay Dung.

Addon mo mot socket TCP trong Blender va cho lenh tu MCP server gui sang.
Moi lenh duoc thuc thi ngay tren luong chinh cua Blender thong qua
bpy.app.timers, vi thu vien bpy khong an toan khi goi tu luong phu.

Don vi do trong toan bo addon la met, dung theo mac dinh cua Blender.
Du lieu kien truc Viet Nam thuong ghi bang milimet, phan doi don vi do
MCP server lo truoc khi gui sang.

Cai dat: Edit > Preferences > Add-ons > Install, chon dung file nay.
Dung: View3D > thanh ben (phim N) > tab "MCP Xay Dung" > Bat ket noi.
"""

from __future__ import annotations

import base64
import json
import math
import os
import socket
import struct
import tempfile
import traceback

import bpy
import mathutils

bl_info = {
    "name": "MCP Xây Dựng",
    "author": "Ck15",
    "version": (0, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > MCP Xây Dựng",
    "description": "Dựng mô hình nhà 3D từ dữ liệu kiến trúc qua MCP",
    "category": "Interface",
}

DEFAULT_PORT = 9877
MAX_MESSAGE_BYTES = 64 * 1024 * 1024
TICK_SECONDS = 0.05

# Ten collection chua moi thu addon tao ra, de nguoi dung xoa gon mot lan.
COLLECTION_NAME = "MCP_XayDung"


# ---------------------------------------------------------------- tien ich

def _collection() -> bpy.types.Collection:
    """Lay hoac tao collection rieng cho cac doi tuong do addon dung."""
    coll = bpy.data.collections.get(COLLECTION_NAME)
    if coll is None:
        coll = bpy.data.collections.new(COLLECTION_NAME)
        bpy.context.scene.collection.children.link(coll)
    return coll


def _add_mesh(name: str, verts: list, faces: list) -> bpy.types.Object:
    """Tao mot object tu danh sach dinh va mat, dua vao collection cua addon."""
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.validate()

    obj = bpy.data.objects.new(name, mesh)
    _collection().objects.link(obj)
    return obj


def _box_verts(cx: float, cy: float, z0: float, dx: float, dy: float, dz: float) -> list:
    """Tam dinh cua mot hop chu nhat, tinh tu tam day va kich thuoc."""
    hx, hy = dx / 2.0, dy / 2.0
    z1 = z0 + dz
    return [
        (cx - hx, cy - hy, z0), (cx + hx, cy - hy, z0),
        (cx + hx, cy + hy, z0), (cx - hx, cy + hy, z0),
        (cx - hx, cy - hy, z1), (cx + hx, cy - hy, z1),
        (cx + hx, cy + hy, z1), (cx - hx, cy + hy, z1),
    ]


# Mat cua mot hop theo thu tu dinh o tren: day, nap, va bon mat ben.
_BOX_FACES = [
    (0, 3, 2, 1), (4, 5, 6, 7),
    (0, 1, 5, 4), (1, 2, 6, 5),
    (2, 3, 7, 6), (3, 0, 4, 7),
]


def _prism_from_polygon(points: list, z0: float, dz: float) -> tuple:
    """Dung khoi lang tru tu mot da giac phang, tra ve (verts, faces)."""
    n = len(points)
    verts = [(p[0], p[1], z0) for p in points]
    verts += [(p[0], p[1], z0 + dz) for p in points]

    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    return verts, faces


def _extrude_profile(profile: list, x0: float, y0: float, ux: float, uy: float,
                     rong: float, base_z: float) -> tuple:
    """Keo mot tiet dien phang thanh khoi, theo phuong vuong goc voi huong di.

    profile: danh sach (t, z) mo ta tiet dien, t do doc theo huong (ux, uy),
    z do theo chieu cao. Tiet dien phai loi, neu khong hai mat bit dau se
    bi veo khi Blender chia tam giac.

    Tra ve (verts, faces) voi chi so bat dau tu 0.
    """
    vx, vy = -uy * rong / 2.0, ux * rong / 2.0
    n = len(profile)

    verts = []
    for sign in (-1.0, 1.0):
        for t, z in profile:
            verts.append((
                x0 + ux * t + vx * sign,
                y0 + uy * t + vy * sign,
                base_z + z,
            ))

    # Hai mat bit hai dau, roi cac mat ben noi chung lai.
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    return verts, faces


def _tag(obj: bpy.types.Object, loai: str, **extra) -> None:
    """Gan nhan loai cau kien va cac so do len object, phuc vu boc khoi luong."""
    obj["xd_loai"] = loai
    for key, value in extra.items():
        obj[f"xd_{key}"] = value


def _mesh_volume(obj: bpy.types.Object) -> float:
    """The tich khoi kin, tinh bang met khoi, da ke bien doi ty le.

    Do tren hinh hoc DA AP modifier (boolean khoet lo cua). Doc obj.data se
    ra khoi goc chua khoet, lam the tich tuong khong tru lo cua.
    """
    import bmesh

    depsgraph = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    try:
        bm.from_object(obj, depsgraph)
        bm.transform(obj.matrix_world)
        return abs(bm.calc_volume(signed=True))
    finally:
        bm.free()


def _principled(mat: bpy.types.Material):
    """Tim node Principled BSDF theo kieu, khong theo ten.

    Ten node doi theo ngon ngu giao dien Blender nen khong tra cuu bang ten duoc.
    """
    return next(
        (n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"),
        None,
    )


def _set_input(node, names: tuple, value) -> bool:
    """Gan gia tri vao input dau tien tim thay theo danh sach ten uu tien.

    Ten input cung doi giua cac ban Blender, vi du 'Specular' thanh
    'Specular IOR Level' tu ban 4.0, nen phai thu lan luot.
    """
    for name in names:
        if name in node.inputs:
            node.inputs[name].default_value = value
            return True
    return False


# Bang vat lieu xay dung thuong gap.
# Moi dong: (mau RGBA, do nham, do kim loai, do duc)
# Do duc 1.0 la khong nhin xuyen qua duoc, cang nho cang trong. Chi kinh moi
# dat duoi 1.0; dat nham cho vat lieu dac se lam no tang hinh khi render.
VAT_LIEU = {
    "be_tong":   ((0.60, 0.60, 0.58, 1.0), 0.90, 0.0, 1.00),
    "gach":      ((0.55, 0.27, 0.20, 1.0), 0.85, 0.0, 1.00),
    "tuong_son": ((0.92, 0.91, 0.88, 1.0), 0.70, 0.0, 1.00),
    "kinh":      ((0.60, 0.75, 0.80, 1.0), 0.05, 0.0, 0.25),
    "go":        ((0.45, 0.28, 0.14, 1.0), 0.55, 0.0, 1.00),
    "thep":      ((0.70, 0.70, 0.72, 1.0), 0.30, 1.0, 1.00),
    "ngoi":      ((0.45, 0.15, 0.10, 1.0), 0.80, 0.0, 1.00),
    "gach_lat":  ((0.85, 0.83, 0.78, 1.0), 0.25, 0.0, 1.00),
    "da":        ((0.50, 0.50, 0.52, 1.0), 0.60, 0.0, 1.00),
    "nhom":      ((0.75, 0.76, 0.78, 1.0), 0.25, 1.0, 1.00),
}


# ---------------------------------------------------------------- handlers

class Handlers:
    """Moi phuong thuc cong khai o day la mot lenh MCP server goi duoc."""

    # ----- thong tin

    def ping(self):
        return {"pong": True, "blender": bpy.app.version_string}

    def get_status(self):
        return {
            "blender_version": bpy.app.version_string,
            "addon_version": ".".join(str(x) for x in bl_info["version"]),
            "file": bpy.data.filepath or "(chua luu)",
            "don_vi": str(bpy.context.scene.unit_settings.length_unit),
            "so_doi_tuong": len(bpy.context.scene.objects),
            "collection": COLLECTION_NAME,
        }

    def get_scene_info(self, chi_cua_addon: bool = False, gioi_han: int = 100):
        scene = bpy.context.scene
        if chi_cua_addon:
            coll = bpy.data.collections.get(COLLECTION_NAME)
            objects = list(coll.objects) if coll else []
        else:
            objects = list(scene.objects)

        items = []
        for obj in objects[:gioi_han]:
            dim = obj.dimensions
            items.append({
                "ten": obj.name,
                "kieu": obj.type,
                "vi_tri": [round(v, 4) for v in obj.location],
                "kich_thuoc": [round(v, 4) for v in dim],
                "loai_cau_kien": obj.get("xd_loai"),
                "vat_lieu": [s.material.name for s in obj.material_slots if s.material],
            })

        return {
            "ten_scene": scene.name,
            "khung_hinh": [scene.frame_start, scene.frame_current, scene.frame_end],
            "tong_doi_tuong": len(objects),
            "hien_thi": len(items),
            "doi_tuong": items,
        }

    def get_object_info(self, ten: str):
        obj = bpy.data.objects.get(ten)
        if obj is None:
            raise KeyError(f"Khong co doi tuong ten '{ten}'")

        info = {
            "ten": obj.name,
            "kieu": obj.type,
            "vi_tri": [round(v, 4) for v in obj.location],
            "xoay_do": [round(math.degrees(v), 2) for v in obj.rotation_euler],
            "ty_le": [round(v, 4) for v in obj.scale],
            "kich_thuoc": [round(v, 4) for v in obj.dimensions],
            "vat_lieu": [s.material.name for s in obj.material_slots if s.material],
            "modifier": [m.name for m in obj.modifiers],
            "thuoc_tinh_xd": {k: obj[k] for k in obj.keys() if k.startswith("xd_")},
        }
        if obj.type == "MESH":
            info["so_mat"] = len(obj.data.polygons)
            info["so_dinh"] = len(obj.data.vertices)
        return info

    # ----- dung cau kien

    def create_wall(self, diem_dau, diem_cuoi, day=0.22, cao=3.0, cao_do=0.0, ten=None):
        """Dung mot buc tuong thang tu diem dau den diem cuoi.

        diem_dau, diem_cuoi: [x, y] tren mat bang, don vi met.
        day: be day tuong, vi du 0.22 cho tuong 220.
        """
        x0, y0 = float(diem_dau[0]), float(diem_dau[1])
        x1, y1 = float(diem_cuoi[0]), float(diem_cuoi[1])

        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        if length < 1e-6:
            raise ValueError("Diem dau va diem cuoi trung nhau, khong dung duoc tuong.")

        # Vector phap tuyen trong mat phang, dung de day be day sang hai ben.
        nx, ny = -dy / length * day / 2.0, dx / length * day / 2.0

        base = [
            (x0 - nx, y0 - ny), (x1 - nx, y1 - ny),
            (x1 + nx, y1 + ny), (x0 + nx, y0 + ny),
        ]
        verts, faces = _prism_from_polygon(base, cao_do, cao)

        name = ten or f"Tuong_{int(day * 1000)}"
        obj = _add_mesh(name, verts, faces)
        _tag(
            obj, "tuong",
            dai=round(length, 4), day=day, cao=cao, cao_do=cao_do,
            diem_dau=[x0, y0], diem_cuoi=[x1, y1],
            dien_tich=round(length * cao, 4),
            the_tich=round(length * cao * day, 4),
        )
        return {"ten": obj.name, "dai": round(length, 4),
                "dien_tich": round(length * cao, 4),
                "the_tich": round(length * cao * day, 4)}

    def create_slab(self, dinh, day=0.10, cao_do=0.0, ten=None):
        """Dung tam san tu da giac mat bang. dinh: [[x, y], ...] it nhat 3 diem."""
        if len(dinh) < 3:
            raise ValueError("San can it nhat 3 dinh.")

        points = [(float(p[0]), float(p[1])) for p in dinh]
        # San do xuong duoi cao do hoan thien, giong cach thi cong that.
        verts, faces = _prism_from_polygon(points, cao_do - day, day)

        obj = _add_mesh(ten or "San", verts, faces)
        area = _polygon_area(points)
        _tag(obj, "san", day=day, cao_do=cao_do,
             dien_tich=round(area, 4), the_tich=round(area * day, 4))
        return {"ten": obj.name, "dien_tich": round(area, 4),
                "the_tich": round(area * day, 4)}

    def create_column(self, vi_tri, rong=0.22, sau=0.22, cao=3.0, cao_do=0.0, ten=None):
        """Dung mot cot chu nhat. vi_tri: [x, y] la tam cot."""
        x, y = float(vi_tri[0]), float(vi_tri[1])
        verts = _box_verts(x, y, cao_do, rong, sau, cao)
        obj = _add_mesh(ten or f"Cot_{int(rong*1000)}x{int(sau*1000)}", verts, _BOX_FACES)
        _tag(obj, "cot", rong=rong, sau=sau, cao=cao, cao_do=cao_do,
             the_tich=round(rong * sau * cao, 4))
        return {"ten": obj.name, "the_tich": round(rong * sau * cao, 4)}

    def create_beam(self, diem_dau, diem_cuoi, rong=0.22, cao=0.35, cao_do_day=2.65, ten=None):
        """Dung dam ngang. cao_do_day la cao do day dam."""
        result = self.create_wall(diem_dau, diem_cuoi, day=rong, cao=cao,
                                  cao_do=cao_do_day, ten=ten or "Dam")
        obj = bpy.data.objects[result["ten"]]
        _tag(obj, "dam", rong=rong, cao=cao, cao_do=cao_do_day,
             dai=result["dai"], the_tich=result["the_tich"])
        return {"ten": obj.name, "dai": result["dai"], "the_tich": result["the_tich"]}

    def create_opening(self, ten_tuong, khoang_cach, rong, cao, be_cua=0.0):
        """Khoet lo cua tren mot buc tuong da dung.

        khoang_cach: tu diem dau cua tuong den mep trai lo cua, don vi met.
        be_cua: cao do day lo so voi chan tuong. Cua di dat 0, cua so dat 0.9.
        """
        wall = bpy.data.objects.get(ten_tuong)
        if wall is None:
            raise KeyError(f"Khong co tuong ten '{ten_tuong}'")
        if wall.get("xd_loai") != "tuong":
            raise ValueError(f"'{ten_tuong}' khong phai tuong do addon dung.")

        x0, y0 = wall["xd_diem_dau"]
        x1, y1 = wall["xd_diem_cuoi"]
        day = float(wall["xd_day"])
        chan = float(wall["xd_cao_do"])

        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length

        # Tam lo cua nam tren truc tim tuong, cach diem dau mot doan.
        mid = khoang_cach + rong / 2.0
        cx, cy = x0 + ux * mid, y0 + uy * mid

        # Khoi cat day hon tuong mot chut de phep tru khong de lai mang mong.
        cutter_verts, cutter_faces = _prism_from_polygon(
            _rect_along(cx, cy, ux, uy, rong, day + 0.02),
            chan + be_cua, cao,
        )
        cutter = _add_mesh(f"_cat_{ten_tuong}", cutter_verts, cutter_faces)

        mod = wall.modifiers.new(name=f"LoCua_{len(wall.modifiers)}", type="BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter
        cutter.hide_viewport = True
        cutter.hide_render = True

        dt_lo = rong * cao
        wall["xd_dien_tich_lo"] = round(float(wall.get("xd_dien_tich_lo", 0.0)) + dt_lo, 4)
        return {"tuong": wall.name, "khoi_cat": cutter.name,
                "dien_tich_lo": round(dt_lo, 4)}

    def create_stair(self, diem_dau, huong_do=0.0, so_bac=18, cao_bac=0.175,
                     rong_bac=0.27, rong_thang=1.0, cao_do=0.0,
                     day_ban=0.12, ten=None):
        """Dung cau thang betong mot ve: ban nghieng cong cac bac nam tren.

        Dung dung cach cau tao that chu khong dap mot khoi dac, vi khoi dac
        cho khoi luong betong lon gap nhieu lan thuc te.

        huong_do: huong di len tinh bang do, 0 la theo truc X duong.
        day_ban: be day ban thang, do vuong goc voi mat nghieng.
        """
        n = int(so_bac)
        if n < 1:
            raise ValueError("Cau thang phai co it nhat mot bac.")

        rad = math.radians(huong_do)
        ux, uy = math.cos(rad), math.sin(rad)
        x0, y0 = float(diem_dau[0]), float(diem_dau[1])

        tong_dai = n * rong_bac
        tong_cao = n * cao_bac

        # Be day do vuong goc voi mat nghieng, quy ve be day do theo phuong
        # thang dung de dung duoc tiet dien trong mat phang (t, z).
        canh_nghieng = math.hypot(rong_bac, cao_bac)
        day_dung = day_ban * canh_nghieng / rong_bac

        verts: list = []
        faces: list = []

        def them(profile):
            base = len(verts)
            v, f = _extrude_profile(profile, x0, y0, ux, uy, rong_thang, cao_do)
            verts.extend(v)
            faces.extend(tuple(i + base for i in face) for face in f)

        # Ban thang: hinh binh hanh chay suot tu chan len dinh.
        them([
            (0.0, 0.0),
            (tong_dai, tong_cao),
            (tong_dai, tong_cao - day_dung),
            (0.0, -day_dung),
        ])

        # Moi bac la mot lang tru tam giac nam tren mat nghieng.
        # Thu tu dinh phai cung chieu voi tiet dien ban thang o tren, neu
        # nguoc chieu thi mat quay vao trong va the tich tinh ra bi am.
        for i in range(n):
            t0, t1 = i * rong_bac, (i + 1) * rong_bac
            z0, z1 = i * cao_bac, (i + 1) * cao_bac
            them([(t0, z0), (t0, z1), (t1, z1)])

        obj = _add_mesh(ten or "CauThang", verts, faces)

        the_tich = (tong_dai * day_dung + n * rong_bac * cao_bac / 2.0) * rong_thang
        _tag(obj, "cau_thang", so_bac=n, cao_bac=cao_bac, rong_bac=rong_bac,
             rong_thang=rong_thang, cao_do=cao_do, day_ban=day_ban,
             tong_cao=round(tong_cao, 4), the_tich=round(the_tich, 4))

        return {"ten": obj.name, "so_bac": n,
                "tong_cao": round(tong_cao, 4),
                "tong_dai": round(tong_dai, 4),
                "the_tich": round(the_tich, 4)}

    def create_roof(self, dinh, kieu="bang", day=0.10, cao_do=0.0,
                    do_doc=0.02, vuon=0.0, ten=None):
        """Dung mai. kieu: 'bang' (mai bang co doc thoat nuoc) hoac 'doc' (mai mot doc)."""
        if len(dinh) < 3:
            raise ValueError("Mai can it nhat 3 dinh.")

        points = [(float(p[0]), float(p[1])) for p in dinh]
        if vuon > 0:
            points = _offset_polygon(points, vuon)

        n = len(points)
        xs = [p[0] for p in points]
        x_min, x_max = min(xs), max(xs)
        span = max(x_max - x_min, 1e-6)

        def z_at(x: float) -> float:
            if kieu == "bang":
                # Mai bang van phai doc nhe de thoat nuoc, doc theo truc X.
                return cao_do + (x - x_min) * do_doc
            return cao_do + (x - x_min) / span * do_doc * span

        verts = [(p[0], p[1], z_at(p[0]) - day) for p in points]
        verts += [(p[0], p[1], z_at(p[0])) for p in points]

        faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, j, j + n, i + n))

        obj = _add_mesh(ten or "Mai", verts, faces)
        area = _polygon_area(points)
        _tag(obj, "mai", kieu=kieu, day=day, cao_do=cao_do, do_doc=do_doc,
             dien_tich=round(area, 4), the_tich=round(area * day, 4))
        return {"ten": obj.name, "dien_tich": round(area, 4),
                "the_tich": round(area * day, 4)}

    # ----- vat lieu

    def create_material(self, ten, loai="be_tong", mau=None):
        """Tao vat lieu theo bang dung san, hoac theo mau tu chon."""
        mat = bpy.data.materials.get(ten) or bpy.data.materials.new(ten)
        mat.use_nodes = True

        node = _principled(mat)
        if node is None:
            raise RuntimeError("Vat lieu khong co node Principled BSDF.")

        preset = VAT_LIEU.get(loai)
        if preset is None and mau is None:
            raise ValueError(
                f"Khong biet loai '{loai}'. Cac loai co san: {sorted(VAT_LIEU)}"
            )

        if preset:
            color, rough, metal, alpha = preset
        else:
            color, rough, metal, alpha = (1, 1, 1, 1), 0.5, 0.0, 1.0

        if mau is not None:
            color = tuple(mau) if len(mau) == 4 else tuple(mau) + (1.0,)

        _set_input(node, ("Base Color",), color)
        _set_input(node, ("Roughness",), rough)
        _set_input(node, ("Metallic",), metal)
        if alpha < 1.0:
            _set_input(node, ("Alpha",), alpha)
            mat.blend_method = "BLEND"

        return {"ten": mat.name, "loai": loai}

    def assign_material(self, ten_doi_tuong, ten_vat_lieu):
        obj = bpy.data.objects.get(ten_doi_tuong)
        if obj is None:
            raise KeyError(f"Khong co doi tuong '{ten_doi_tuong}'")
        mat = bpy.data.materials.get(ten_vat_lieu)
        if mat is None:
            raise KeyError(f"Khong co vat lieu '{ten_vat_lieu}'")

        obj.data.materials.clear()
        obj.data.materials.append(mat)
        return {"doi_tuong": obj.name, "vat_lieu": mat.name}

    # ----- sua, xoa

    def modify_object(self, ten, vi_tri=None, xoay_do=None, ty_le=None, ten_moi=None):
        obj = bpy.data.objects.get(ten)
        if obj is None:
            raise KeyError(f"Khong co doi tuong '{ten}'")

        if vi_tri is not None:
            obj.location = tuple(float(v) for v in vi_tri)
        if xoay_do is not None:
            obj.rotation_euler = tuple(math.radians(float(v)) for v in xoay_do)
        if ty_le is not None:
            obj.scale = tuple(float(v) for v in ty_le)
        if ten_moi:
            obj.name = ten_moi

        return {"ten": obj.name, "vi_tri": [round(v, 4) for v in obj.location]}

    def delete_object(self, ten):
        obj = bpy.data.objects.get(ten)
        if obj is None:
            raise KeyError(f"Khong co doi tuong '{ten}'")
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"da_xoa": ten}

    def duplicate_object(self, ten, lech=(0.0, 0.0, 0.0), ten_moi=None):
        src = bpy.data.objects.get(ten)
        if src is None:
            raise KeyError(f"Khong co doi tuong '{ten}'")

        copy = src.copy()
        copy.data = src.data.copy()
        if ten_moi:
            copy.name = ten_moi
        copy.location = mathutils.Vector(src.location) + mathutils.Vector(lech)
        _collection().objects.link(copy)
        return {"ten": copy.name}

    def clear_scene(self, chi_cua_addon=True):
        """Xoa cac doi tuong do addon tao. Mac dinh khong dung toi vat cua nguoi dung."""
        coll = bpy.data.collections.get(COLLECTION_NAME)
        if coll is None:
            return {"da_xoa": 0}

        targets = list(coll.objects) if chi_cua_addon else list(bpy.context.scene.objects)
        for obj in targets:
            bpy.data.objects.remove(obj, do_unlink=True)
        return {"da_xoa": len(targets)}

    # ----- camera, den, render

    def create_light(self, kieu="SUN", vi_tri=(5, -5, 10), cong_suat=5.0,
                     goc_do=(45, 0, 45), ten=None):
        data = bpy.data.lights.new(name=ten or f"Den_{kieu}", type=kieu)
        data.energy = cong_suat
        obj = bpy.data.objects.new(data.name, data)
        obj.location = tuple(float(v) for v in vi_tri)
        obj.rotation_euler = tuple(math.radians(float(v)) for v in goc_do)
        _collection().objects.link(obj)
        return {"ten": obj.name, "kieu": kieu}

    def set_world_light(self, cuong_do=1.0, mau=(0.55, 0.65, 0.80)):
        """Dat anh sang moi truong, dong vai bau troi hat sang vao cong trinh.

        Chi co mot nguon SUN thi moi mat quay khoi huong nang deu den si, nhin
        khong ra hinh khoi. Anh sang moi truong lap vao cho toi do.
        """
        world = bpy.context.scene.world
        if world is None:
            world = bpy.data.worlds.new("World")
            bpy.context.scene.world = world
        world.use_nodes = True

        bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
        if bg is None:
            raise RuntimeError("World khong co node Background.")

        color = tuple(mau) if len(mau) == 4 else tuple(mau) + (1.0,)
        bg.inputs["Color"].default_value = color
        bg.inputs["Strength"].default_value = float(cuong_do)
        return {"cuong_do": float(cuong_do), "mau": list(color)}

    def create_camera(self, vi_tri, nhin_vao=(0, 0, 0), tieu_cu=35.0,
                      dat_lam_chinh=True, ten=None):
        data = bpy.data.cameras.new(ten or "Camera_MCP")
        data.lens = float(tieu_cu)
        obj = bpy.data.objects.new(data.name, data)
        obj.location = tuple(float(v) for v in vi_tri)
        _collection().objects.link(obj)

        direction = mathutils.Vector(nhin_vao) - mathutils.Vector(obj.location)
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

        if dat_lam_chinh:
            bpy.context.scene.camera = obj
        return {"ten": obj.name, "tieu_cu": float(tieu_cu)}

    def set_render_settings(self, rong=1920, cao=1080, engine=None, mau_anh=None):
        scene = bpy.context.scene
        scene.render.resolution_x = int(rong)
        scene.render.resolution_y = int(cao)
        scene.render.resolution_percentage = 100

        if engine:
            # Danh sach engine hop le khac nhau giua cac ban Blender, nen phai
            # thu gan roi doc thong bao loi thay vi doan truoc.
            try:
                scene.render.engine = engine
            except TypeError as exc:
                raise ValueError(f"Engine '{engine}' khong dung. {exc}") from exc

        if mau_anh:
            scene.render.image_settings.file_format = mau_anh

        return {"rong": scene.render.resolution_x, "cao": scene.render.resolution_y,
                "engine": scene.render.engine}

    def viewport_screenshot(self, kich_thuoc_toi_da=1200):
        """Chup khung nhin bang render OpenGL, tra ve anh PNG ma hoa base64."""
        return self._render_to_base64(opengl=True, max_size=kich_thuoc_toi_da)

    def render_image(self, duong_dan=None, kich_thuoc_toi_da=1600):
        """Render chinh thuc bang engine dang chon."""
        result = self._render_to_base64(opengl=False, max_size=kich_thuoc_toi_da,
                                        save_to=duong_dan)
        return result

    def _render_to_base64(self, opengl: bool, max_size: int, save_to=None):
        scene = bpy.context.scene
        old_path = scene.render.filepath
        old_format = scene.render.image_settings.file_format
        old_x = scene.render.resolution_x
        old_y = scene.render.resolution_y

        # Thu nho anh de khong gui ban tin qua lon qua socket.
        scale = min(1.0, max_size / max(old_x, old_y))
        tmp = os.path.join(tempfile.gettempdir(), "mcp_xaydung_render.png")

        try:
            scene.render.image_settings.file_format = "PNG"
            scene.render.resolution_x = max(1, int(old_x * scale))
            scene.render.resolution_y = max(1, int(old_y * scale))
            scene.render.filepath = save_to or tmp

            if opengl:
                bpy.ops.render.opengl(write_still=True)
            else:
                bpy.ops.render.render(write_still=True)

            final = bpy.path.abspath(scene.render.filepath)
            if not final.lower().endswith(".png"):
                final += ".png"
            with open(final, "rb") as fh:
                data = fh.read()
        finally:
            scene.render.filepath = old_path
            scene.render.image_settings.file_format = old_format
            scene.render.resolution_x = old_x
            scene.render.resolution_y = old_y

        return {
            "anh_base64": base64.b64encode(data).decode("ascii"),
            "duong_dan": save_to or None,
            "rong": scene.render.resolution_x,
            "cao": scene.render.resolution_y,
        }

    # ----- xuat, boc khoi luong

    def export_scene(self, duong_dan, dinh_dang="glb", chi_cua_addon=False):
        """Xuat canh ra file. dinh_dang: glb, fbx, obj, stl."""
        path = bpy.path.abspath(duong_dan)
        folder = os.path.dirname(path)
        if folder and not os.path.isdir(folder):
            raise ValueError(f"Thu muc khong ton tai: {folder}")

        if chi_cua_addon:
            bpy.ops.object.select_all(action="DESELECT")
            coll = bpy.data.collections.get(COLLECTION_NAME)
            for obj in (coll.objects if coll else []):
                obj.select_set(True)

        fmt = dinh_dang.lower()
        if fmt == "glb":
            bpy.ops.export_scene.gltf(filepath=path, export_format="GLB",
                                      use_selection=chi_cua_addon)
        elif fmt == "fbx":
            bpy.ops.export_scene.fbx(filepath=path, use_selection=chi_cua_addon)
        elif fmt == "obj":
            bpy.ops.wm.obj_export(filepath=path, export_selected_objects=chi_cua_addon)
        elif fmt == "stl":
            bpy.ops.wm.stl_export(filepath=path, export_selected_objects=chi_cua_addon)
        else:
            raise ValueError(f"Dinh dang '{dinh_dang}' khong ho tro. Dung glb, fbx, obj hoac stl.")

        return {"duong_dan": path, "dinh_dang": fmt,
                "dung_luong_kb": round(os.path.getsize(path) / 1024, 1)}

    def compute_quantities(self):
        """Boc khoi luong tu chinh mo hinh, gom theo loai cau kien.

        The tich lay tu hinh hoc thuc te nen da tru san cac lo cua da khoet.
        """
        coll = bpy.data.collections.get(COLLECTION_NAME)
        if coll is None:
            return {"cau_kien": [], "tong": {}}

        groups: dict = {}
        for obj in coll.objects:
            loai = obj.get("xd_loai")
            if not loai or obj.type != "MESH":
                continue

            g = groups.setdefault(loai, {"so_luong": 0, "the_tich": 0.0,
                                         "dien_tich": 0.0, "doi_tuong": []})
            volume = _mesh_volume(obj)
            g["so_luong"] += 1
            g["the_tich"] += volume
            # Dien tich tuong tru phan lo cua da khoet (xd_dien_tich_lo).
            g["dien_tich"] += (float(obj.get("xd_dien_tich", 0.0))
                               - float(obj.get("xd_dien_tich_lo", 0.0)))
            g["doi_tuong"].append({"ten": obj.name, "the_tich_m3": round(volume, 4)})

        for g in groups.values():
            g["the_tich"] = round(g["the_tich"], 4)
            g["dien_tich"] = round(g["dien_tich"], 4)

        tong_bt = round(sum(g["the_tich"] for k, g in groups.items()
                            if k in {"cot", "dam", "san", "cau_thang", "mai"}), 4)
        tong_tuong = round(sum(g["the_tich"] for k, g in groups.items()
                               if k == "tuong"), 4)

        return {
            "cau_kien": groups,
            "tong": {
                "be_tong_m3": tong_bt,
                "khoi_xay_m3": tong_tuong,
                "ghi_chu": "The tich do truc tiep tu hinh hoc, da tru lo cua.",
            },
        }

    # ----- nang cao

    def execute_code(self, code):
        """Chay Python trong Blender. MCP server da soat code truoc khi gui sang."""
        scope = {"bpy": bpy, "math": math, "mathutils": mathutils, "ket_qua": None}
        exec(compile(code, "<mcp_xaydung>", "exec"), scope)  # noqa: S102
        value = scope.get("ket_qua")
        return {"ket_qua": repr(value) if value is not None else "(khong tra ve gi)"}


# ------------------------------------------------------- tien ich hinh hoc

def _polygon_area(points: list) -> float:
    """Dien tich da giac theo cong thuc day giay."""
    total = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def _rect_along(cx: float, cy: float, ux: float, uy: float,
                doc: float, ngang: float) -> list:
    """Hinh chu nhat co tam (cx, cy), canh doc theo huong (ux, uy)."""
    hx, hy = ux * doc / 2.0, uy * doc / 2.0
    px, py = -uy * ngang / 2.0, ux * ngang / 2.0
    return [
        (cx - hx - px, cy - hy - py), (cx + hx - px, cy + hy - py),
        (cx + hx + px, cy + hy + py), (cx - hx + px, cy - hy + py),
    ]


def _offset_polygon(points: list, amount: float) -> list:
    """Noi rong da giac ra ngoai mot khoang, tinh tu tam.

    Cach nay du cho phan vuon mai cua nha hinh chu nhat. Voi da giac lom
    phuc tap thi nen tu tinh dinh mai roi truyen vao.
    """
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)

    out = []
    for x, y in points:
        dx, dy = x - cx, y - cy
        dist = math.hypot(dx, dy)
        if dist < 1e-9:
            out.append((x, y))
        else:
            out.append((x + dx / dist * amount, y + dy / dist * amount))
    return out


# ---------------------------------------------------------------- server

class MCPServer:
    """Socket TCP chay tren luong chinh cua Blender."""

    def __init__(self) -> None:
        self.sock: socket.socket | None = None
        self.running = False
        self.port = DEFAULT_PORT
        self.handlers = Handlers()

    def start(self, port: int = DEFAULT_PORT) -> None:
        if self.running:
            return

        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("localhost", port))
        self.sock.listen(5)
        self.sock.setblocking(False)
        self.running = True

        bpy.app.timers.register(self._tick, persistent=True)
        print(f"[MCP Xây Dựng] Đang nghe ở localhost:{port}")

    def stop(self) -> None:
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None
        print("[MCP Xây Dựng] Đã dừng")

    def _tick(self):
        """Ham chay dinh ky tren luong chinh, nhan va xu ly tung lenh mot."""
        if not self.running or self.sock is None:
            return None

        try:
            client, _ = self.sock.accept()
        except BlockingIOError:
            return TICK_SECONDS
        except OSError:
            return TICK_SECONDS

        try:
            client.settimeout(30.0)
            self._serve(client)
        except Exception:
            traceback.print_exc()
        finally:
            try:
                client.close()
            except OSError:
                pass

        return TICK_SECONDS

    def _serve(self, client: socket.socket) -> None:
        header = _recv_exactly(client, 4)
        if header is None:
            return
        (length,) = struct.unpack(">I", header)
        if length > MAX_MESSAGE_BYTES:
            self._reply(client, {"status": "error", "message": "Ban tin qua lon."})
            return

        body = _recv_exactly(client, length)
        if body is None:
            return

        try:
            request = json.loads(body.decode("utf-8"))
            command = request.get("type", "")
            params = request.get("params", {}) or {}
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._reply(client, {"status": "error", "message": f"JSON hong: {exc}"})
            return

        handler = getattr(self.handlers, command, None)
        if command.startswith("_") or not callable(handler):
            self._reply(client, {
                "status": "error",
                "message": f"Khong co lenh '{command}'.",
            })
            return

        try:
            result = handler(**params)
            self._reply(client, {"status": "success", "result": result})
        except Exception as exc:
            traceback.print_exc()
            self._reply(client, {
                "status": "error",
                "message": f"{type(exc).__name__}: {exc}",
            })

    @staticmethod
    def _reply(client: socket.socket, payload: dict) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        client.sendall(struct.pack(">I", len(data)) + data)


def _recv_exactly(sock: socket.socket, n: int) -> bytes | None:
    chunks = []
    remaining = n
    while remaining > 0:
        chunk = sock.recv(min(remaining, 1 << 20))
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


_server = MCPServer()


# ------------------------------------------------------------- giao dien

class MCPXD_OT_start(bpy.types.Operator):
    bl_idname = "mcp_xaydung.start"
    bl_label = "Bật kết nối"
    bl_description = "Mở socket cho MCP server nối vào"

    def execute(self, context):
        try:
            _server.start(context.scene.mcp_xaydung_port)
        except OSError as exc:
            self.report({"ERROR"}, f"Không mở được cổng: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, f"Đang nghe ở cổng {_server.port}")
        return {"FINISHED"}


class MCPXD_OT_stop(bpy.types.Operator):
    bl_idname = "mcp_xaydung.stop"
    bl_label = "Tắt kết nối"
    bl_description = "Đóng socket"

    def execute(self, context):
        _server.stop()
        self.report({"INFO"}, "Đã dừng")
        return {"FINISHED"}


class MCPXD_PT_panel(bpy.types.Panel):
    bl_label = "MCP Xây Dựng"
    bl_idname = "MCPXD_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MCP Xây Dựng"

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "mcp_xaydung_port")

        if _server.running:
            layout.label(text=f"Đang chạy ở cổng {_server.port}", icon="CHECKMARK")
            layout.operator("mcp_xaydung.stop", icon="PAUSE")
        else:
            layout.label(text="Chưa kết nối", icon="ERROR")
            layout.operator("mcp_xaydung.start", icon="PLAY")


_classes = (MCPXD_OT_start, MCPXD_OT_stop, MCPXD_PT_panel)


def register():
    bpy.types.Scene.mcp_xaydung_port = bpy.props.IntProperty(
        name="Cổng",
        default=DEFAULT_PORT,
        min=1024,
        max=65535,
        description="Cổng TCP mà addon lắng nghe",
    )
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    _server.stop()
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.mcp_xaydung_port


if __name__ == "__main__":
    register()
