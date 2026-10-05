"""Kiem tra bo dung ca cong trinh mot luot.

Test thay the tang ket noi bang mot ham gia de ghi lai cac lenh duoc goi,
nho vay kiem tra duoc phan dieu phoi ma khong can mo Blender.
"""

import json
from pathlib import Path

import pytest

from blender_mcp_xaydung import server

VI_DU = Path(__file__).parent.parent / "examples" / "nha-pho-5x20m.json"


class GhiLenh:
    """Thay cho _goi: ghi lai lenh va tra ve ket qua gia."""

    def __init__(self, loi_o=None):
        self.lenh = []
        self.loi_o = loi_o or set()
        self._dem = 0

    def __call__(self, lenh, **params):
        self.lenh.append((lenh, params))
        self._dem += 1
        if self._dem - 1 in self.loi_o:
            raise RuntimeError("loi gia lap")
        return {"ten": f"{lenh}_{self._dem}", "dai": 1.0, "the_tich": 1.0}

    def dem(self, lenh):
        return sum(1 for ten, _ in self.lenh if ten == lenh)


@pytest.fixture
def ghi(monkeypatch):
    g = GhiLenh()
    monkeypatch.setattr(server, "_goi", g)
    return g


MO_TA_NHO = {
    "tang": [{
        "ten": "T1",
        "cao_do": 0.0,
        "cao_tuong": 3.0,
        "san": {"dinh": [[0, 0], [4, 0], [4, 6], [0, 6]], "day": 0.1},
        "tuong": [
            {"diem_dau": [0, 0], "diem_cuoi": [4, 0], "day": 0.22},
            {"diem_dau": [4, 0], "diem_cuoi": [4, 6], "day": 0.22},
        ],
        "cot": [{"vi_tri": [0, 0]}, {"vi_tri": [4, 0]}],
        "cua": [{"tuong": 0, "khoang_cach": 1.0, "rong": 0.9, "cao": 2.2}],
    }]
}


def test_dung_du_so_luong_cau_kien(ghi):
    kq = server.dung_tu_mo_ta(MO_TA_NHO)

    assert kq == {
        "san": 1, "tuong": 2, "cot": 2, "cua": 1, "loi": [],
        "ten_tuong_theo_tang": {"T1": ["create_wall_2", "create_wall_3"]},
    }


def test_cao_do_tang_duoc_truyen_xuong_moi_cau_kien(ghi):
    mo_ta = {"tang": [{"ten": "T2", "cao_do": 3.9, "cao_tuong": 3.25,
                       "tuong": [{"diem_dau": [0, 0], "diem_cuoi": [5, 0]}],
                       "cot": [{"vi_tri": [0, 0]}]}]}
    server.dung_tu_mo_ta(mo_ta)

    for lenh, params in ghi.lenh:
        assert params["cao_do"] == 3.9, f"{lenh} nhan sai cao do"


def test_tuong_lay_chieu_cao_mac_dinh_cua_tang(ghi):
    server.dung_tu_mo_ta(MO_TA_NHO)
    tuong = [p for ten, p in ghi.lenh if ten == "create_wall"]
    assert all(t["cao"] == 3.0 for t in tuong)


def test_tuong_tu_ghi_chieu_cao_rieng_thi_uu_tien(ghi):
    mo_ta = {"tang": [{"ten": "T1", "cao_tuong": 3.0, "tuong": [
        {"diem_dau": [0, 0], "diem_cuoi": [5, 0], "cao": 1.1},
    ]}]}
    server.dung_tu_mo_ta(mo_ta)
    assert ghi.lenh[0][1]["cao"] == 1.1


def test_cua_tro_dung_buc_tuong_theo_so_thu_tu(ghi):
    server.dung_tu_mo_ta(MO_TA_NHO)
    cua = next(p for ten, p in ghi.lenh if ten == "create_opening")
    # Tuong so 0 la buc dau tien duoc dung trong tang do.
    assert cua["ten_tuong"] == "create_wall_2"


def test_cua_tro_sai_tuong_thi_ghi_loi_chu_khong_do_vo(ghi):
    mo_ta = {"tang": [{"ten": "T1", "tuong": [
        {"diem_dau": [0, 0], "diem_cuoi": [5, 0]},
    ], "cua": [{"tuong": 9, "khoang_cach": 1, "rong": 1, "cao": 2}]}]}

    kq = server.dung_tu_mo_ta(mo_ta)
    assert kq["tuong"] == 1
    assert kq["cua"] == 0
    assert len(kq["loi"]) == 1
    assert "khong tim thay tuong so 9" in kq["loi"][0]


def test_mot_cau_kien_loi_khong_lam_hong_ca_me(monkeypatch):
    # Cho lenh thu hai that bai: do la buc tuong dau tien.
    g = GhiLenh(loi_o={1})
    monkeypatch.setattr(server, "_goi", g)

    kq = server.dung_tu_mo_ta(MO_TA_NHO)

    assert kq["san"] == 1, "San van phai dung duoc"
    assert kq["tuong"] == 1, "Buc tuong con lai van phai dung duoc"
    assert kq["cot"] == 2, "Cot van phai dung duoc"
    assert len(kq["loi"]) >= 1


def test_nhieu_tang_dung_doc_lap(ghi):
    mo_ta = {"tang": [
        {"ten": "T1", "cao_do": 0.0, "tuong": [{"diem_dau": [0, 0], "diem_cuoi": [5, 0]}]},
        {"ten": "T2", "cao_do": 3.9, "tuong": [{"diem_dau": [0, 0], "diem_cuoi": [5, 0]}]},
    ]}
    kq = server.dung_tu_mo_ta(mo_ta)

    assert kq["tuong"] == 2
    assert set(kq["ten_tuong_theo_tang"]) == {"T1", "T2"}


def test_mo_ta_rong_khong_loi(ghi):
    kq = server.dung_tu_mo_ta({})
    assert kq["tuong"] == 0
    assert kq["loi"] == []


# ------------------------------------------------- file vi du di kem repo

def test_file_vi_du_doc_duoc():
    assert VI_DU.is_file(), "Thieu file vi du trong examples/"
    json.loads(VI_DU.read_text(encoding="utf-8"))


def test_file_vi_du_dung_duoc_het(ghi):
    mo_ta = json.loads(VI_DU.read_text(encoding="utf-8"))
    kq = server.dung_tu_mo_ta(mo_ta)

    assert kq["loi"] == [], f"File vi du co loi: {kq['loi']}"
    assert kq["san"] == 4, "Phai co 4 san cho 4 tang"
    assert kq["tuong"] == 22
    assert kq["cot"] == 30
    assert kq["cua"] == 15


def test_file_vi_du_co_cao_do_tang_dan():
    """Cac tang phai xep chong len nhau, khong duoc trung hay lon cao do."""
    mo_ta = json.loads(VI_DU.read_text(encoding="utf-8"))
    cao_do = [t["cao_do"] for t in mo_ta["tang"]]
    assert cao_do == sorted(cao_do), "Cao do cac tang phai tang dan"
    assert len(set(cao_do)) == len(cao_do), "Khong duoc hai tang cung cao do"


def test_file_vi_du_tuong_khop_voi_chieu_cao_tang():
    """Chan tuong tang tren phai dat dung bang dinh tuong tang duoi cong dam."""
    mo_ta = json.loads(VI_DU.read_text(encoding="utf-8"))
    tang = mo_ta["tang"]

    for duoi, tren in zip(tang, tang[1:]):
        cao_tang = tren["cao_do"] - duoi["cao_do"]
        chenh = cao_tang - duoi["cao_tuong"]
        # Phan chenh chinh la chieu cao dam, phai nam trong khoang hop ly.
        assert 0.25 <= chenh <= 0.45, (
            f"{duoi['ten']}: cao tang {cao_tang:.2f} tru cao tuong "
            f"{duoi['cao_tuong']:.2f} ra {chenh:.2f}, khong giong chieu cao dam"
        )
