"""Kiem tra lop soat code nguy hiem."""

import pytest

from blender_mcp_xaydung import safe_mode


@pytest.fixture(autouse=True)
def _tat_che_do_bo_qua(monkeypatch):
    """Dam bao test khong bi anh huong boi bien moi truong cua may that."""
    monkeypatch.delenv("BLENDER_MCP_UNSAFE", raising=False)


CODE_AN_TOAN = [
    "import bpy\nbpy.ops.mesh.primitive_cube_add(size=2)",
    "import bpy, math\nket_qua = len(bpy.data.objects)",
    "import bpy\nfor o in bpy.data.objects:\n    o.location.z += 1",
    "import json\nket_qua = json.dumps({'a': 1})",
    "with open('/tmp/x.txt') as f:\n    data = f.read()",
]

CODE_NGUY_HIEM = [
    ("import subprocess", "nhap module bi chan"),
    ("from shutil import rmtree", "nhap tu module bi chan"),
    ("import os\nos.remove('/tmp/x')", "xoa file"),
    ("import os\nos.system('dir')", "xoa file hoac chay lenh"),
    ("eval('1+1')", "goi ham bi chan"),
    ("exec('x = 1')", "goi ham bi chan"),
    ("__import__('os')", "goi ham bi chan"),
    ("import bpy\nbpy.ops.wm.quit_blender()", "mat ban ve"),
    ("import bpy\nbpy.ops.wm.read_factory_settings()", "mat ban ve"),
    ("open('/tmp/x.txt', 'w').write('hi')", "mo file de ghi"),
    ("open('/tmp/x.txt', mode='a')", "mo file de ghi"),
    ("().__class__.__bases__", "thuoc tinh noi bo"),
    ("print.__globals__", "thuoc tinh noi bo"),
]


@pytest.mark.parametrize("code", CODE_AN_TOAN)
def test_code_an_toan_duoc_cho_qua(code):
    ket_qua = safe_mode.scan(code)
    assert ket_qua.safe, f"Bi chan nham: {ket_qua.reasons}"


@pytest.mark.parametrize("code,manh_ly_do", CODE_NGUY_HIEM)
def test_code_nguy_hiem_bi_chan(code, manh_ly_do):
    ket_qua = safe_mode.scan(code)
    assert not ket_qua.safe, f"Dang le phai chan: {code}"
    assert any(manh_ly_do in r for r in ket_qua.reasons), (
        f"Ly do khong khop. Nhan duoc: {ket_qua.reasons}"
    )


def test_code_sai_cu_phap_bi_chan():
    ket_qua = safe_mode.scan("def (:")
    assert not ket_qua.safe
    assert "sai cu phap" in ket_qua.reasons[0]


def test_thong_bao_liet_ke_moi_ly_do():
    ket_qua = safe_mode.scan("import subprocess\neval('1')")
    assert not ket_qua.safe
    assert len(ket_qua.reasons) == 2
    text = ket_qua.message()
    assert "subprocess" in text
    assert "eval" in text
    assert "BLENDER_MCP_UNSAFE" in text


def test_che_do_bo_qua_cho_moi_thu_di_qua(monkeypatch):
    monkeypatch.setenv("BLENDER_MCP_UNSAFE", "1")
    assert safe_mode.scan("import subprocess").safe


def test_so_dong_duoc_ghi_dung():
    ket_qua = safe_mode.scan("x = 1\ny = 2\nimport subprocess")
    assert "dong 3" in ket_qua.reasons[0]
