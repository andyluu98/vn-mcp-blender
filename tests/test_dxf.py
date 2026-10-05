"""Kiem tra viec rut tuong va cot tu ban ve DXF.

Test tu sinh file DXF nho roi doc lai, khong phu thuoc ban ve ngoai.
"""

import math

import ezdxf
import pytest

from blender_mcp_xaydung import dxf as dxf_reader


def _them_hcn(msp, layer, x0, y0, x1, y1):
    """Ve mot hinh chu nhat kin tren layer cho truoc."""
    msp.add_lwpolyline(
        [(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
        close=True,
        dxfattribs={"layer": layer},
    )


@pytest.fixture
def ban_ve(tmp_path):
    """Mat bang gia lap: 2 tuong 220, 1 tuong 110, 1 cot. Don vi milimet."""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Tuong doc dai 14m, day 220, nam o x = 0
    _them_hcn(msp, "A-WALL-220", -110, 0, 110, 14000)
    # Tuong ngang dai 5m, day 220, nam o y = 0
    _them_hcn(msp, "A-WALL-220", 0, -110, 5000, 110)
    # Tuong ngan dai 3m, day 110
    _them_hcn(msp, "A-WALL-110", 1000, 5000, 4000, 5110)
    # Cot 220x220 tai goc
    _them_hcn(msp, "A-COL", -110, -110, 110, 110)
    # Mot hinh vuong tren layer tuong, khong du det nen phai bi bo qua
    _them_hcn(msp, "A-WALL-220", 9000, 9000, 9500, 9500)

    path = tmp_path / "mat_bang.dxf"
    doc.saveas(path)
    return str(path)


def test_liet_ke_layer(ban_ve):
    kq = dxf_reader.liet_ke_layer(ban_ve)
    assert kq["so_layer"] == 3
    assert kq["layer"]["A-WALL-220"]["LWPOLYLINE"] == 3
    assert kq["layer"]["A-COL"]["LWPOLYLINE"] == 1


def test_doc_duoc_dung_so_tuong_va_cot(ban_ve):
    mb = dxf_reader.doc_mat_bang(ban_ve)
    # Hinh vuong 500x500 khong du det nen bi loai, con lai 3 tuong.
    assert len(mb.tuong) == 3
    assert len(mb.cot) == 1


def test_doi_don_vi_sang_met(ban_ve):
    mb = dxf_reader.doc_mat_bang(ban_ve)
    dai_nhat = max(t.dai for t in mb.tuong)
    assert dai_nhat == pytest.approx(14.0, abs=0.01)


def test_be_day_tuong_dung(ban_ve):
    mb = dxf_reader.doc_mat_bang(ban_ve)
    days = sorted(round(t.day, 3) for t in mb.tuong)
    assert days == [0.11, 0.22, 0.22]


def test_truc_tim_nam_giua_tuong(ban_ve):
    """Tuong doc ve tu x = -110 den x = 110 thi truc tim phai o x = 0."""
    mb = dxf_reader.doc_mat_bang(ban_ve)
    tuong_doc = next(t for t in mb.tuong if t.dai > 13.0)
    assert tuong_doc.diem_dau[0] == pytest.approx(0.0, abs=1e-6)
    assert tuong_doc.diem_cuoi[0] == pytest.approx(0.0, abs=1e-6)


def test_loc_theo_vung(ban_ve):
    """Chi lay phan ban ve nam trong khung chi dinh."""
    mb = dxf_reader.doc_mat_bang(ban_ve, vung=(-500, -500, 500, 500))
    # Trong khung nay chi co cot va tuong ngang di qua goc toa do.
    assert len(mb.cot) == 1
    assert all(abs(c.tam[0]) < 0.5 for c in mb.cot)


def test_doi_goc_toa_do(ban_ve):
    """Doi goc thi moi diem phai tinh lai theo goc moi."""
    mb = dxf_reader.doc_mat_bang(ban_ve, goc=(5000, 0))
    tuong_doc = next(t for t in mb.tuong if t.dai > 13.0)
    assert tuong_doc.diem_dau[0] == pytest.approx(-5.0, abs=1e-6)


def test_cot_doc_dung_kich_thuoc(ban_ve):
    mb = dxf_reader.doc_mat_bang(ban_ve)
    cot = mb.cot[0]
    assert cot.rong == pytest.approx(0.22, abs=1e-6)
    assert cot.sau == pytest.approx(0.22, abs=1e-6)


def test_tuong_xien_van_doc_duoc(tmp_path):
    """Tuong ve xien 45 do cung phai ra dung chieu dai va be day."""
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    # Hinh chu nhat det, xoay 45 do, dai 10m day 0.2m
    dai, day = 10000.0, 200.0
    c = math.sqrt(0.5)
    ux, uy = c, c
    vx, vy = -c, c
    pts = []
    for t, s in ((0, -day / 2), (dai, -day / 2), (dai, day / 2), (0, day / 2)):
        pts.append((ux * t + vx * s, uy * t + vy * s))
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "A-WALL-220"})

    path = tmp_path / "xien.dxf"
    doc.saveas(path)

    mb = dxf_reader.doc_mat_bang(str(path))
    assert len(mb.tuong) == 1
    assert mb.tuong[0].dai == pytest.approx(10.0, abs=0.01)
    assert mb.tuong[0].day == pytest.approx(0.2, abs=0.01)
