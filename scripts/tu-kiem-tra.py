"""Tu kiem tra phan hinh hoc cua addon, chay ben trong Blender.

Script nay goi thang cac ham dung hinh roi do lai ket qua, khong qua socket.
Muc dich la bat loi tinh toan hinh hoc truoc khi dung that.

Chay:
    blender --background --python scripts/tu-kiem-tra.py

Ma thoat 0 la dat, 1 la co phep do sai.
"""

import math
import sys
from pathlib import Path

# Nap module addon tu ma nguon, khong can cai vao Blender truoc.
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from vn_mcp_blender.bundled import addon  # noqa: E402

loi = []


def kiem(ten, thuc_te, mong_doi, sai_so=1e-4):
    """So mot so do voi gia tri mong doi."""
    dat = abs(thuc_te - mong_doi) <= sai_so
    dau = "dat " if dat else "SAI "
    print(f"  [{dau}] {ten}: {thuc_te:.4f} (mong doi {mong_doi:.4f})")
    if not dat:
        loi.append(f"{ten}: duoc {thuc_te:.4f}, dang le {mong_doi:.4f}")


def main():
    h = addon.Handlers()
    h.clear_scene()

    print("\n1. Tuong thang theo truc X")
    # Tuong dai 5m, day 0.22, cao 3.0
    kq = h.create_wall([0, 0], [5, 0], day=0.22, cao=3.0)
    kiem("chieu dai", kq["dai"], 5.0)
    kiem("dien tich mat", kq["dien_tich"], 15.0)
    kiem("the tich", kq["the_tich"], 5.0 * 3.0 * 0.22)
    ten_tuong = kq["ten"]

    import bpy
    obj = bpy.data.objects[ten_tuong]
    kiem("the tich do tu mesh", addon._mesh_volume(obj), 5.0 * 3.0 * 0.22)
    kiem("be rong thuc (truc Y)", obj.dimensions.y, 0.22)
    kiem("chieu cao thuc (truc Z)", obj.dimensions.z, 3.0)

    print("\n2. Tuong xien 45 do")
    kq = h.create_wall([0, 10], [3, 13], day=0.22, cao=3.0)
    kiem("chieu dai", kq["dai"], math.hypot(3, 3))

    print("\n3. Khoet cua tren tuong")
    # Cua di 1.0 x 2.2 dat cach dau tuong 1.5m
    h.create_opening(ten_tuong, khoang_cach=1.5, rong=1.0, cao=2.2, be_cua=0.0)
    obj = bpy.data.objects[ten_tuong]
    # Phai danh gia sau khi modifier boolean da chay.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(eval_obj.to_mesh())
    bm.transform(obj.matrix_world)
    the_tich_sau_khoet = abs(bm.calc_volume(signed=True))
    bm.free()

    mong_doi = 5.0 * 3.0 * 0.22 - 1.0 * 2.2 * 0.22
    kiem("the tich sau khi khoet cua", the_tich_sau_khoet, mong_doi, sai_so=1e-3)

    print("\n4. San betong")
    kq = h.create_slab([[0, 0], [5, 0], [5, 14], [0, 14]], day=0.10, cao_do=3.9)
    kiem("dien tich", kq["dien_tich"], 70.0)
    kiem("the tich", kq["the_tich"], 7.0)
    san = bpy.data.objects[kq["ten"]]
    # San do xuong duoi cao do hoan thien, nen dinh san phai dung bang cao do.
    kiem("cao do dinh san", max(v.co.z for v in san.data.vertices), 3.9)

    print("\n5. Cot")
    kq = h.create_column([2.5, 7], rong=0.22, sau=0.22, cao=3.15)
    kiem("the tich", kq["the_tich"], 0.22 * 0.22 * 3.15)

    print("\n6. Dam")
    kq = h.create_beam([0, 0], [5, 0], rong=0.22, cao=0.35, cao_do_day=2.65)
    kiem("chieu dai", kq["dai"], 5.0)
    kiem("the tich", kq["the_tich"], 5.0 * 0.35 * 0.22)

    print("\n7. Cau thang")
    kq = h.create_stair([0, 0], huong_do=0, so_bac=18, cao_bac=0.175,
                        rong_bac=0.27, rong_thang=1.0, day_ban=0.12)
    kiem("tong chieu cao", kq["tong_cao"], 3.15)
    kiem("tong chieu dai", kq["tong_dai"], 4.86)
    thang = bpy.data.objects[kq["ten"]]
    # Cao tong the gom ca phan ban thang thong xuong duoi chan bac dau.
    kiem("cao thuc te cua thang", thang.dimensions.z, 3.15 + 0.143, sai_so=1e-3)

    # Thang betong la ban nghieng cong cac bac, khong phai khoi dac.
    # Khoi dac cung kich thuoc se cho khoang 10 m3, gap gan 9 lan.
    canh_nghieng = math.hypot(0.27, 0.175)
    day_dung = 0.12 * canh_nghieng / 0.27
    mong_doi_tt = (4.86 * day_dung + 18 * 0.27 * 0.175 / 2) * 1.0
    kiem("the tich bao cao", kq["the_tich"], mong_doi_tt, sai_so=1e-3)
    kiem("the tich do tu mesh", addon._mesh_volume(thang), mong_doi_tt, sai_so=1e-3)
    if kq["the_tich"] > 3.0:
        loi.append("the tich thang qua lon, co ve dang dap khoi dac")

    print("\n8. Mai")
    kq = h.create_roof([[0, 0], [5, 0], [5, 10.5], [0, 10.5]], day=0.10, cao_do=14.3)
    kiem("dien tich", kq["dien_tich"], 52.5)

    print("\n9. Vat lieu")
    h.create_material("BeTong_Test", loai="be_tong")
    h.assign_material(ten_tuong, "BeTong_Test")
    obj = bpy.data.objects[ten_tuong]
    assert obj.material_slots and obj.material_slots[0].material.name == "BeTong_Test", \
        "Gan vat lieu that bai"
    print("  [dat ] gan vat lieu len tuong")

    # Vat lieu dac ma dat alpha thap se lam cau kien tang hinh khi render,
    # ma nhin so do khoi luong thi khong phat hien ra. Kiem tung loai mot.
    for loai in sorted(addon.VAT_LIEU):
        h.create_material(f"Kiem_{loai}", loai=loai)
        mat = bpy.data.materials[f"Kiem_{loai}"]
        node = addon._principled(mat)
        alpha = node.inputs["Alpha"].default_value if "Alpha" in node.inputs else 1.0
        nguong = 0.1 if loai == "kinh" else 0.9
        if alpha < nguong:
            loi.append(f"vat lieu '{loai}' co alpha {alpha:.2f}, se bi tang hinh")
        else:
            print(f"  [dat ] {loai}: alpha {alpha:.2f}")

    print("\n10. Boc khoi luong")
    kl = h.compute_quantities()
    print(f"  Cac loai cau kien: {sorted(kl['cau_kien'])}")
    print(f"  Tong betong: {kl['tong']['be_tong_m3']} m3")
    print(f"  Tong khoi xay: {kl['tong']['khoi_xay_m3']} m3")
    # Cot + dam + san + thang + mai deu tinh vao betong.
    assert kl["tong"]["be_tong_m3"] > 0, "Khong boc duoc khoi luong betong"
    assert "tuong" in kl["cau_kien"], "Thieu nhom tuong"
    print("  [dat ] boc khoi luong tra ve so duong")

    print("\n11. Xem canh")
    canh = h.get_scene_info(chi_cua_addon=True)
    print(f"  So doi tuong addon dung: {canh['tong_doi_tuong']}")
    assert canh["tong_doi_tuong"] >= 7, "Thieu doi tuong trong collection"
    print("  [dat ] liet ke duoc doi tuong")

    print("\n" + "=" * 60)
    if loi:
        print(f"CO {len(loi)} PHEP DO SAI:")
        for item in loi:
            print(f"  - {item}")
        return 1

    print("TAT CA PHEP DO DEU DAT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
