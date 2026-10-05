"""MCP server cho viec dung mo hinh nha 3D trong Blender.

Server nay khai bao cac tool MCP, nhan lenh tu Claude roi chuyen tiep sang
addon chay ben trong Blender qua socket. Ban than server khong dung duoc hinh
nao, moi thao tac hinh hoc deu do addon lam.

Quy uoc don vi: moi so do trong tool deu tinh bang met. Tuong 220 nhap 0.22.
"""

# Khong dung "from __future__ import annotations" o day: FastMCP doc chu thich
# kieu truc tiep tu chu ky ham de sinh schema cho tool. Neu bat che do chu thich
# dang chuoi, cac ban FastMCP cu se khong hieu va bao loi khi dang ky tool.

import base64
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP, Image

from . import __version__
from .connection import BlenderCommandError, BlenderConnectionError, get_connection
from . import dxf as dxf_reader
from . import safe_mode

mcp = FastMCP(
    "vn-mcp-blender",
    instructions=(
        "Bo cong cu dung mo hinh nha 3D trong Blender tu du lieu kien truc.\n"
        "Moi so do tinh bang met. Truoc khi dung nha, goi kiem_tra_ket_noi de "
        "chac chan addon trong Blender dang bat.\n"
        "Dung ca mot cong trinh thi dung dung_tu_mo_ta, nhanh hon nhieu so voi "
        "goi dung_tuong tung buc.\n"
        "Sau moi buoc dung dang ke, goi nhin de xem ket qua that thay vi tin "
        "rang hinh da dung."
    ),
)

GUIDES_DIR = Path(__file__).parent / "guides"


def _goi(lenh: str, **params: Any) -> Any:
    """Gui mot lenh sang addon, doi ten loi thanh thong bao de hieu."""
    try:
        return get_connection().send(lenh, params)
    except BlenderConnectionError as exc:
        raise RuntimeError(str(exc)) from exc
    except BlenderCommandError as exc:
        raise RuntimeError(f"Blender bao loi khi chay '{lenh}': {exc}") from exc


# ------------------------------------------------------------ ket noi

@mcp.tool()
def kiem_tra_ket_noi() -> dict:
    """Kiem tra MCP server co noi duoc toi Blender khong.

    Goi tool nay dau tien. Neu loi, thong bao se chi ro cach bat addon.
    """
    status = _goi("get_status")
    status["phien_ban_server"] = __version__
    return status


@mcp.tool()
def huong_dan(chu_de: str = "") -> str:
    """Doc huong dan nghiep vu truoc khi lam mot mang viec.

    Bo trong de xem danh sach chu de co san.
    """
    available = sorted(p.stem for p in GUIDES_DIR.glob("*.md"))
    if not chu_de:
        return "Cac chu de co san: " + ", ".join(available)

    path = GUIDES_DIR / f"{chu_de}.md"
    if not path.is_file():
        return f"Khong co chu de '{chu_de}'. Cac chu de co san: {', '.join(available)}"
    return path.read_text(encoding="utf-8")


# ------------------------------------------------------------ xem canh

@mcp.tool()
def xem_canh(chi_cua_addon: bool = False, gioi_han: int = 100) -> dict:
    """Liet ke cac doi tuong dang co trong canh Blender.

    chi_cua_addon: chi liet ke nhung thu bo cong cu nay dung ra.
    """
    return _goi("get_scene_info", chi_cua_addon=chi_cua_addon, gioi_han=gioi_han)


@mcp.tool()
def xem_doi_tuong(ten: str) -> dict:
    """Xem chi tiet mot doi tuong: vi tri, kich thuoc, vat lieu, so do cau kien."""
    return _goi("get_object_info", ten=ten)


# ------------------------------------------------------------ dung cau kien

@mcp.tool()
def dung_tuong(
    diem_dau: list[float],
    diem_cuoi: list[float],
    day: float = 0.22,
    cao: float = 3.0,
    cao_do: float = 0.0,
    ten: str | None = None,
) -> dict:
    """Dung mot buc tuong thang tren mat bang.

    diem_dau, diem_cuoi: [x, y] hai dau truc tim tuong, don vi met.
    day: be day tuong. Tuong bao 0.22, tuong ngan 0.11.
    cao: chieu cao tuong, thuong bang chieu cao tang tru chieu cao dam.
    cao_do: cao do chan tuong.
    """
    return _goi("create_wall", diem_dau=diem_dau, diem_cuoi=diem_cuoi,
                day=day, cao=cao, cao_do=cao_do, ten=ten)


@mcp.tool()
def dung_san(
    dinh: list[list[float]],
    day: float = 0.10,
    cao_do: float = 0.0,
    ten: str | None = None,
) -> dict:
    """Dung tam san betong tu da giac mat bang.

    dinh: danh sach [x, y] theo thu tu vong quanh, it nhat 3 diem.
    cao_do: cao do mat tren cua san. San do xuong duoi cao do nay.
    """
    return _goi("create_slab", dinh=dinh, day=day, cao_do=cao_do, ten=ten)


@mcp.tool()
def dung_cot(
    vi_tri: list[float],
    rong: float = 0.22,
    sau: float = 0.22,
    cao: float = 3.0,
    cao_do: float = 0.0,
    ten: str | None = None,
) -> dict:
    """Dung mot cot chu nhat. vi_tri la [x, y] tam cot."""
    return _goi("create_column", vi_tri=vi_tri, rong=rong, sau=sau,
                cao=cao, cao_do=cao_do, ten=ten)


@mcp.tool()
def dung_dam(
    diem_dau: list[float],
    diem_cuoi: list[float],
    rong: float = 0.22,
    cao: float = 0.35,
    cao_do_day: float = 2.65,
    ten: str | None = None,
) -> dict:
    """Dung mot dam ngang. cao_do_day la cao do day dam, khong phai dinh dam."""
    return _goi("create_beam", diem_dau=diem_dau, diem_cuoi=diem_cuoi,
                rong=rong, cao=cao, cao_do_day=cao_do_day, ten=ten)


@mcp.tool()
def khoet_cua(
    ten_tuong: str,
    khoang_cach: float,
    rong: float,
    cao: float,
    be_cua: float = 0.0,
) -> dict:
    """Khoet lo cua di hoac cua so tren mot buc tuong da dung.

    ten_tuong: ten object tuong, lay tu ket qua dung_tuong.
    khoang_cach: tu diem dau cua tuong den mep trai lo cua.
    be_cua: cao do day lo so voi chan tuong. Cua di dat 0, cua so thuong 0.9.
    """
    return _goi("create_opening", ten_tuong=ten_tuong, khoang_cach=khoang_cach,
                rong=rong, cao=cao, be_cua=be_cua)


@mcp.tool()
def dung_cau_thang(
    diem_dau: list[float],
    huong_do: float = 0.0,
    so_bac: int = 18,
    cao_bac: float = 0.175,
    rong_bac: float = 0.27,
    rong_thang: float = 1.0,
    cao_do: float = 0.0,
    day_ban: float = 0.12,
    ten: str | None = None,
) -> dict:
    """Dung cau thang betong mot ve: ban nghieng cong cac bac nam tren.

    huong_do: huong di len tinh bang do, 0 la theo truc X duong, 90 la truc Y duong.
    cao_bac nhan so_bac phai bang chieu cao tang. Vi du tang cao 3.15m thi
    18 bac moi bac 0.175m.
    day_ban: be day ban thang, do vuong goc voi mat nghieng.

    Thang duoc dung dung cau tao that chu khong dap mot khoi dac, nho vay
    khoi luong betong boc ra dung voi thuc te.
    """
    return _goi("create_stair", diem_dau=diem_dau, huong_do=huong_do,
                so_bac=so_bac, cao_bac=cao_bac, rong_bac=rong_bac,
                rong_thang=rong_thang, cao_do=cao_do, day_ban=day_ban,
                ten=ten)


@mcp.tool()
def dung_mai(
    dinh: list[list[float]],
    kieu: str = "bang",
    day: float = 0.10,
    cao_do: float = 0.0,
    do_doc: float = 0.02,
    vuon: float = 0.0,
    ten: str | None = None,
) -> dict:
    """Dung mai betong.

    kieu: 'bang' cho mai bang co doc thoat nuoc, 'doc' cho mai mot doc.
    do_doc: ty le doc, 0.02 la 2 phan tram.
    vuon: phan mai dua ra ngoai mep tuong.
    """
    return _goi("create_roof", dinh=dinh, kieu=kieu, day=day, cao_do=cao_do,
                do_doc=do_doc, vuon=vuon, ten=ten)


# ------------------------------------------------------------ dung hang loat

@mcp.tool()
def dung_tu_mo_ta(mo_ta: dict) -> dict:
    """Dung ca cong trinh tu mot ban mo ta, nhanh hon goi tung tool.

    Day la cach nen dung khi dung nguyen mot ngoi nha. Cau truc mo_ta:

        {
          "ten": "Nha pho 5x20",
          "tang": [
            {
              "ten": "Tang 1",
              "cao_do": 0.0,
              "cao_tuong": 3.1,
              "san":  {"dinh": [[0,0],[5,0],[5,14],[0,14]], "day": 0.1},
              "tuong": [{"diem_dau": [0,0], "diem_cuoi": [5,0], "day": 0.22}],
              "cot":   [{"vi_tri": [0,0], "rong": 0.22, "sau": 0.22, "cao": 3.1}],
              "cua":   [{"tuong": 0, "khoang_cach": 1.0, "rong": 1.0,
                         "cao": 2.2, "be_cua": 0.0}]
            }
          ]
        }

    Truong "tuong" trong moi muc cua la so thu tu cua buc tuong trong danh sach
    tuong cua chinh tang do, dem tu 0.
    """
    tong = {"san": 0, "tuong": 0, "cot": 0, "cua": 0, "loi": []}
    ten_tuong_theo_tang: dict = {}

    for i, tang in enumerate(mo_ta.get("tang", [])):
        ten_tang = tang.get("ten", f"Tang{i + 1}")
        cao_do = float(tang.get("cao_do", 0.0))
        cao_tuong = float(tang.get("cao_tuong", 3.0))

        san = tang.get("san")
        if san:
            try:
                _goi("create_slab", dinh=san["dinh"],
                     day=float(san.get("day", 0.10)),
                     cao_do=cao_do, ten=f"San_{ten_tang}")
                tong["san"] += 1
            except RuntimeError as exc:
                tong["loi"].append(f"{ten_tang} san: {exc}")

        ten_tuong: list[str] = []
        for j, t in enumerate(tang.get("tuong", [])):
            try:
                kq = _goi("create_wall",
                          diem_dau=t["diem_dau"], diem_cuoi=t["diem_cuoi"],
                          day=float(t.get("day", 0.22)),
                          cao=float(t.get("cao", cao_tuong)),
                          cao_do=cao_do,
                          ten=t.get("ten") or f"Tuong_{ten_tang}_{j}")
                ten_tuong.append(kq["ten"])
                tong["tuong"] += 1
            except RuntimeError as exc:
                ten_tuong.append("")
                tong["loi"].append(f"{ten_tang} tuong {j}: {exc}")

        ten_tuong_theo_tang[ten_tang] = ten_tuong

        for j, c in enumerate(tang.get("cot", [])):
            try:
                _goi("create_column", vi_tri=c["vi_tri"],
                     rong=float(c.get("rong", 0.22)),
                     sau=float(c.get("sau", 0.22)),
                     cao=float(c.get("cao", cao_tuong)),
                     cao_do=cao_do,
                     ten=c.get("ten") or f"Cot_{ten_tang}_{j}")
                tong["cot"] += 1
            except RuntimeError as exc:
                tong["loi"].append(f"{ten_tang} cot {j}: {exc}")

        for j, cua in enumerate(tang.get("cua", [])):
            idx = int(cua.get("tuong", -1))
            if not (0 <= idx < len(ten_tuong)) or not ten_tuong[idx]:
                tong["loi"].append(f"{ten_tang} cua {j}: khong tim thay tuong so {idx}")
                continue
            try:
                _goi("create_opening", ten_tuong=ten_tuong[idx],
                     khoang_cach=float(cua["khoang_cach"]),
                     rong=float(cua["rong"]), cao=float(cua["cao"]),
                     be_cua=float(cua.get("be_cua", 0.0)))
                tong["cua"] += 1
            except RuntimeError as exc:
                tong["loi"].append(f"{ten_tang} cua {j}: {exc}")

    tong["ten_tuong_theo_tang"] = ten_tuong_theo_tang
    return tong


# ------------------------------------------------------------ doc DXF

@mcp.tool()
def doc_layer_dxf(duong_dan: str) -> dict:
    """Liet ke layer trong mot file DXF, de biet layer nao chua tuong va cot.

    Goi tool nay truoc khi dung dung_nha_tu_dxf, vi moi don vi thiet ke dat
    ten layer mot kieu.
    """
    try:
        return dxf_reader.liet_ke_layer(duong_dan)
    except Exception as exc:
        raise RuntimeError(f"Khong doc duoc file DXF: {exc}") from exc


@mcp.tool()
def doc_mat_bang_dxf(
    duong_dan: str,
    layer_tuong: list[str] | None = None,
    layer_cot: list[str] | None = None,
    vung: list[float] | None = None,
    ty_le: float = 0.001,
    goc: list[float] | None = None,
) -> dict:
    """Doc mat bang DXF va tra ve danh sach tuong, cot, chua dung gi trong Blender.

    Dung tool nay de kiem tra du lieu doc ra co dung khong truoc khi dung.
    vung: [x0, y0, x1, y1] theo don vi ban ve, de lay rieng mot mat bang khi
    ho so xep nhieu mat bang canh nhau.
    ty_le: 0.001 cho ban ve milimet, 1.0 cho ban ve met.
    """
    try:
        mb = dxf_reader.doc_mat_bang(
            duong_dan,
            layer_tuong=tuple(layer_tuong) if layer_tuong else dxf_reader.LAYER_TUONG_MAC_DINH,
            layer_cot=tuple(layer_cot) if layer_cot else dxf_reader.LAYER_COT_MAC_DINH,
            vung=tuple(vung) if vung else None,
            ty_le=ty_le,
            goc=tuple(goc) if goc else (0.0, 0.0),
        )
    except Exception as exc:
        raise RuntimeError(f"Khong doc duoc mat bang: {exc}") from exc
    return mb.to_dict()


@mcp.tool()
def dung_nha_tu_dxf(
    duong_dan: str,
    cao_tuong: float = 3.0,
    cao_do: float = 0.0,
    layer_tuong: list[str] | None = None,
    layer_cot: list[str] | None = None,
    vung: list[float] | None = None,
    ty_le: float = 0.001,
    goc: list[float] | None = None,
    dung_cot_luon: bool = True,
) -> dict:
    """Doc mat bang DXF roi dung thang tuong va cot trong Blender.

    Day la buoc noi giua ban ve 2D va mo hinh 3D. Nen goi doc_mat_bang_dxf
    truoc de kiem tra so lieu, roi moi goi tool nay.
    """
    data = doc_mat_bang_dxf(duong_dan, layer_tuong, layer_cot, vung, ty_le, goc)

    ket_qua = {"tuong": 0, "cot": 0, "loi": []}

    for i, t in enumerate(data["tuong"]):
        try:
            _goi("create_wall", diem_dau=t["diem_dau"], diem_cuoi=t["diem_cuoi"],
                 day=t["day"], cao=cao_tuong, cao_do=cao_do,
                 ten=f"Tuong_dxf_{i}")
            ket_qua["tuong"] += 1
        except RuntimeError as exc:
            ket_qua["loi"].append(f"tuong {i}: {exc}")

    if dung_cot_luon:
        for i, c in enumerate(data["cot"]):
            try:
                _goi("create_column", vi_tri=c["tam"], rong=c["rong"],
                     sau=c["sau"], cao=cao_tuong, cao_do=cao_do,
                     ten=f"Cot_dxf_{i}")
                ket_qua["cot"] += 1
            except RuntimeError as exc:
                ket_qua["loi"].append(f"cot {i}: {exc}")

    ket_qua["pham_vi"] = data["pham_vi"]
    return ket_qua


# ------------------------------------------------------------ vat lieu

@mcp.tool()
def tao_vat_lieu(ten: str, loai: str = "be_tong",
                 mau: list[float] | None = None) -> dict:
    """Tao vat lieu xay dung.

    loai co san: be_tong, gach, tuong_son, kinh, go, thep, ngoi, gach_lat,
    da, nhom. Truyen mau [r, g, b] trong khoang 0 den 1 de doi mau rieng.
    """
    return _goi("create_material", ten=ten, loai=loai, mau=mau)


@mcp.tool()
def gan_vat_lieu(ten_doi_tuong: str, ten_vat_lieu: str) -> dict:
    """Gan mot vat lieu da tao len doi tuong."""
    return _goi("assign_material", ten_doi_tuong=ten_doi_tuong,
                ten_vat_lieu=ten_vat_lieu)


# ------------------------------------------------------------ sua, xoa

@mcp.tool()
def sua_doi_tuong(ten: str, vi_tri: list[float] | None = None,
                  xoay_do: list[float] | None = None,
                  ty_le: list[float] | None = None,
                  ten_moi: str | None = None) -> dict:
    """Doi vi tri, goc xoay, ty le hoac ten cua mot doi tuong. Goc tinh bang do."""
    return _goi("modify_object", ten=ten, vi_tri=vi_tri, xoay_do=xoay_do,
                ty_le=ty_le, ten_moi=ten_moi)


@mcp.tool()
def xoa_doi_tuong(ten: str) -> dict:
    """Xoa mot doi tuong khoi canh."""
    return _goi("delete_object", ten=ten)


@mcp.tool()
def nhan_ban(ten: str, lech: list[float], ten_moi: str | None = None) -> dict:
    """Nhan ban mot doi tuong va doi di mot khoang. lech la [dx, dy, dz] bang met."""
    return _goi("duplicate_object", ten=ten, lech=lech, ten_moi=ten_moi)


@mcp.tool()
def xoa_toan_bo(chi_cua_addon: bool = True) -> dict:
    """Xoa cac doi tuong bo cong cu nay da dung.

    Mac dinh chi xoa trong collection rieng, khong dung toi vat nguoi dung tu lam.
    Dat chi_cua_addon=False de xoa sach ca canh, can nhac ky truoc khi dung.
    """
    return _goi("clear_scene", chi_cua_addon=chi_cua_addon)


# ------------------------------------------------------------ camera, den

@mcp.tool()
def tao_den(kieu: str = "SUN", vi_tri: list[float] | None = None,
            cong_suat: float = 5.0, goc_do: list[float] | None = None,
            ten: str | None = None) -> dict:
    """Tao nguon sang. kieu: SUN, POINT, SPOT hoac AREA.

    SUN dung lam anh nang mat troi, goc_do quyet dinh huong nang.
    """
    return _goi("create_light", kieu=kieu,
                vi_tri=vi_tri or [5, -5, 10],
                cong_suat=cong_suat,
                goc_do=goc_do or [45, 0, 45], ten=ten)


@mcp.tool()
def anh_sang_moi_truong(cuong_do: float = 1.0,
                        mau: list[float] | None = None) -> dict:
    """Dat anh sang moi truong, dong vai bau troi hat sang vao cong trinh.

    Chi co mot nguon SUN thi moi mat quay khoi huong nang deu den si, nhin
    khong ra hinh khoi. Goi tool nay cung voi tao_den de anh ro rang.

    cuong_do: 0.5 cho troi chieu nang gat, 1.0 cho troi quang, 2.0 cho troi
    nhieu may hoac muon nhin ro moi chi tiet.
    """
    return _goi("set_world_light", cuong_do=cuong_do,
                mau=mau or [0.55, 0.65, 0.80])


@mcp.tool()
def tao_camera(vi_tri: list[float], nhin_vao: list[float] | None = None,
               tieu_cu: float = 35.0, dat_lam_chinh: bool = True,
               ten: str | None = None) -> dict:
    """Dat camera va huong no vao mot diem.

    tieu_cu 35 cho phoi canh rong, 50 cho goc nhin gan voi mat nguoi.
    """
    return _goi("create_camera", vi_tri=vi_tri, nhin_vao=nhin_vao or [0, 0, 0],
                tieu_cu=tieu_cu, dat_lam_chinh=dat_lam_chinh, ten=ten)


@mcp.tool()
def cai_dat_render(rong: int = 1920, cao: int = 1080,
                   engine: str | None = None,
                   mau_anh: str | None = None) -> dict:
    """Dat do phan giai va engine render.

    engine thuong dung: BLENDER_EEVEE_NEXT cho nhanh, CYCLES cho dep.
    Ten engine khac nhau giua cac ban Blender, neu sai thi thong bao loi se
    liet ke cac ten hop le.
    """
    return _goi("set_render_settings", rong=rong, cao=cao,
                engine=engine, mau_anh=mau_anh)


# ------------------------------------------------------------ xem va render

@mcp.tool()
def nhin(kich_thuoc_toi_da: int = 1200) -> Image:
    """Chup khung nhin Blender de nhin tan mat ket qua vua dung.

    Goi tool nay sau moi buoc dung dang ke. Nhin anh roi tu danh gia: co khoi
    nao bay lo lung, dam xuyen qua nhau, hay sai ty le khong.
    """
    kq = _goi("viewport_screenshot", kich_thuoc_toi_da=kich_thuoc_toi_da)
    return Image(data=base64.b64decode(kq["anh_base64"]), format="png")


@mcp.tool()
def render_anh(duong_dan: str | None = None,
               kich_thuoc_toi_da: int = 1600) -> Image:
    """Render anh chinh thuc bang engine dang chon.

    Cham hon nhin nhung cho ra anh dep. Truyen duong_dan de luu lai file.
    """
    kq = _goi("render_image", duong_dan=duong_dan,
              kich_thuoc_toi_da=kich_thuoc_toi_da)
    return Image(data=base64.b64decode(kq["anh_base64"]), format="png")


# ------------------------------------------------------------ xuat

@mcp.tool()
def xuat_file(duong_dan: str, dinh_dang: str = "glb",
              chi_cua_addon: bool = False) -> dict:
    """Xuat mo hinh ra file. dinh_dang: glb, fbx, obj hoac stl.

    glb hop de xem tren web va dien thoai, fbx hop de dua sang phan mem khac.
    """
    return _goi("export_scene", duong_dan=duong_dan, dinh_dang=dinh_dang,
                chi_cua_addon=chi_cua_addon)


@mcp.tool()
def boc_khoi_luong() -> dict:
    """Boc khoi luong tu chinh mo hinh 3D da dung.

    The tich do truc tiep tu hinh hoc nen da tru san cac lo cua da khoet.
    Ket qua gom tung loai cau kien va tong betong, tong khoi xay.
    """
    return _goi("compute_quantities")


# ------------------------------------------------------------ nang cao

@mcp.tool()
def chay_python(code: str) -> dict:
    """Chay Python bat ky ben trong Blender, dung khi khong co tool san phu hop.

    Code duoc soat truoc de chan cac thao tac nguy hiem nhu xoa file hay chay
    lenh he thong. Gan gia tri vao bien ten 'ket_qua' de nhan lai gia tri do.

    Luu y khi viet code chay tren may nguoi khac:
    - Tim node shader theo thuoc tinh type, khong theo ten, vi ten doi theo
      ngon ngu giao dien.
    - Khong viet cung ten enum, hay doc danh sach hop le tu bl_rna truoc.
    """
    ket_qua = safe_mode.scan(code)
    if not ket_qua.safe:
        raise RuntimeError(ket_qua.message())
    return _goi("execute_code", code=code)


def main() -> None:
    """Diem vao khi chay server."""
    mcp.run()


if __name__ == "__main__":
    main()
