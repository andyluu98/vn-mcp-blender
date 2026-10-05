"""Dung ngoi nha mau trong examples/ roi boc khoi luong, chay trong Blender.

Script chay thang ben trong Blender, khong qua socket, nen dung de kiem tra
toan bo duong dung hinh ma khong can bat addon hay mo Claude.

Chay:
    blender --background --python scripts/dung-vi-du.py

Them --save duong/dan.blend de luu lai ket qua:
    blender --background --python scripts/dung-vi-du.py -- --save nha.blend
"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from blender_mcp_xaydung.bundled import addon  # noqa: E402

VI_DU = REPO / "examples" / "nha-pho-5x20m.json"


def dung(h, mo_ta):
    """Dung toan bo cong trinh, lap lai dung logic cua tool dung_tu_mo_ta."""
    dem = {"san": 0, "tuong": 0, "cot": 0, "cua": 0}
    loi = []

    for i, tang in enumerate(mo_ta.get("tang", [])):
        ten_tang = tang.get("ten", f"Tang{i + 1}")
        cao_do = float(tang.get("cao_do", 0.0))
        cao_tuong = float(tang.get("cao_tuong", 3.0))

        san = tang.get("san")
        if san:
            h.create_slab(dinh=san["dinh"], day=float(san.get("day", 0.10)),
                          cao_do=cao_do, ten=f"San_{ten_tang}")
            dem["san"] += 1

        ten_tuong = []
        for j, t in enumerate(tang.get("tuong", [])):
            kq = h.create_wall(
                diem_dau=t["diem_dau"], diem_cuoi=t["diem_cuoi"],
                day=float(t.get("day", 0.22)),
                cao=float(t.get("cao", cao_tuong)),
                cao_do=cao_do, ten=f"Tuong_{ten_tang}_{j}",
            )
            ten_tuong.append(kq["ten"])
            dem["tuong"] += 1

        for j, c in enumerate(tang.get("cot", [])):
            h.create_column(
                vi_tri=c["vi_tri"], rong=float(c.get("rong", 0.22)),
                sau=float(c.get("sau", 0.22)),
                cao=float(c.get("cao", cao_tuong)),
                cao_do=cao_do, ten=f"Cot_{ten_tang}_{j}",
            )
            dem["cot"] += 1

        for j, cua in enumerate(tang.get("cua", [])):
            idx = int(cua.get("tuong", -1))
            if not (0 <= idx < len(ten_tuong)):
                loi.append(f"{ten_tang} cua {j}: khong co tuong so {idx}")
                continue
            h.create_opening(
                ten_tuong=ten_tuong[idx],
                khoang_cach=float(cua["khoang_cach"]),
                rong=float(cua["rong"]), cao=float(cua["cao"]),
                be_cua=float(cua.get("be_cua", 0.0)),
            )
            dem["cua"] += 1

    return dem, loi


def main():
    import bpy

    mo_ta = json.loads(VI_DU.read_text(encoding="utf-8"))
    print(f"\nDung: {mo_ta.get('ten')}")

    h = addon.Handlers()
    h.clear_scene()

    dem, loi = dung(h, mo_ta)
    print(f"\nDa dung: {dem['san']} san, {dem['tuong']} tuong, "
          f"{dem['cot']} cot, {dem['cua']} lo cua")
    if loi:
        print("Loi:")
        for item in loi:
            print(f"  - {item}")

    # Mai phu phan tum
    h.create_roof([[0, 0], [5, 0], [5, 10.5], [0, 10.5]],
                  day=0.10, cao_do=14.3, vuon=0.3)

    # Cau thang noi 4 tang. Tang 1 cao 3.45m, cac tang tren 3.6m.
    for ten, cao_do, cao_tang in [
        ("Thang_1_2", 0.45, 3.45), ("Thang_2_3", 3.90, 3.60),
        ("Thang_3_Tum", 7.50, 3.60),
    ]:
        so_bac = 20
        h.create_stair([1.0, 5.3], huong_do=90, so_bac=so_bac,
                       cao_bac=cao_tang / so_bac, rong_bac=0.27,
                       rong_thang=1.0, cao_do=cao_do, ten=ten)

    # Vat lieu
    h.create_material("BeTong", loai="be_tong")
    h.create_material("TuongSon", loai="tuong_son")
    coll = bpy.data.collections[addon.COLLECTION_NAME]
    for obj in coll.objects:
        loai = obj.get("xd_loai")
        if loai == "tuong":
            h.assign_material(obj.name, "TuongSon")
        elif loai in {"san", "cot", "dam", "mai", "cau_thang"}:
            h.assign_material(obj.name, "BeTong")

    # Den va camera. Camera dung o goc truoc ben trai nen huong nang phai
    # chieu vao dung hai mat do, neu khong anh ra toan bong toi.
    h.create_light(kieu="SUN", goc_do=[55, 0, 25], cong_suat=4.0)
    h.set_world_light(cuong_do=1.2)
    h.create_camera(vi_tri=[18, -16, 12], nhin_vao=[2.5, 6, 6], tieu_cu=35)

    print("\n" + "=" * 62)
    print("BOC KHOI LUONG")
    print("=" * 62)

    kl = h.compute_quantities()
    print(f"{'Loai cau kien':<14}{'So luong':>10}{'The tich m3':>14}{'Dien tich m2':>14}")
    print("-" * 62)
    for loai in sorted(kl["cau_kien"]):
        g = kl["cau_kien"][loai]
        print(f"{loai:<14}{g['so_luong']:>10}{g['the_tich']:>14.3f}"
              f"{g['dien_tich']:>14.2f}")
    print("-" * 62)
    print(f"{'Tong betong':<14}{'':>10}{kl['tong']['be_tong_m3']:>14.3f}")
    print(f"{'Tong khoi xay':<14}{'':>10}{kl['tong']['khoi_xay_m3']:>14.3f}")

    canh = h.get_scene_info(chi_cua_addon=True, gioi_han=1)
    print(f"\nTong doi tuong trong collection: {canh['tong_doi_tuong']}")

    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

    if "--save" in argv:
        path = argv[argv.index("--save") + 1]
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(path).resolve()))
        print(f"Da luu: {path}")

    if "--render" in argv:
        path = str(Path(argv[argv.index("--render") + 1]).resolve())
        h.set_render_settings(rong=1280, cao=960)
        scene = bpy.context.scene
        scene.render.filepath = path
        scene.render.image_settings.file_format = "PNG"

        # Danh sach engine khac nhau giua cac ban Blender, nen thu lan luot
        # thay vi doan truoc ten nao co.
        for engine, samples in (("BLENDER_EEVEE_NEXT", 32), ("BLENDER_EEVEE", 32),
                                ("CYCLES", 16)):
            try:
                scene.render.engine = engine
            except TypeError:
                continue
            if engine == "CYCLES":
                scene.cycles.samples = samples
                scene.cycles.device = "CPU"
            try:
                bpy.ops.render.render(write_still=True)
                print(f"Da render bang {engine}: {path}")
                break
            except RuntimeError as exc:
                print(f"{engine} khong render duoc: {exc}")
        else:
            print("Khong engine nao render duoc trong che do nen.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
