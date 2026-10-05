# Huong dan phat trien

## Chuan bi

```bash
git clone https://github.com/ck15/blender-mcp-xaydung
cd blender-mcp-xaydung
pip install -e ".[dev]"
pytest
```

37 test chay duoc ma khong can mo Blender. Chung dung socket gia va file DXF
tu sinh.

Phan hinh hoc co script rieng, chay trong Blender that:

```bash
blender --background --python scripts/tu-kiem-tra.py
```

Script nay goi thang cac ham dung hinh roi do lai ket qua. Ma thoat 0 la dat.

## Them mot cong cu moi

Mot cong cu can sua **ba cho**. Thieu cho nao la no khong chay.

### Cho 1: handler trong addon

Them mot phuong thuc vao lop `Handlers` trong
`src/blender_mcp_xaydung/bundled/addon.py`:

```python
def create_lan_can(self, diem_dau, diem_cuoi, cao=1.1, day=0.02, cao_do=0.0,
                   ten=None):
    """Dung lan can kinh."""
    result = self.create_wall(diem_dau, diem_cuoi, day=day, cao=cao,
                              cao_do=cao_do, ten=ten or "LanCan")
    obj = bpy.data.objects[result["ten"]]
    _tag(obj, "lan_can", cao=cao, day=day, dai=result["dai"])
    return {"ten": obj.name, "dai": result["dai"]}
```

Khong phai dang ky gi them. Lop `MCPServer` tim handler bang `getattr`, nen
moi phuong thuc cong khai trong `Handlers` deu goi duoc ngay. Phuong thuc
bat dau bang dau gach duoi bi chan, dung lam ham noi bo.

### Cho 2: tool trong MCP server

Them vao `src/blender_mcp_xaydung/server.py`:

```python
@mcp.tool()
def dung_lan_can(
    diem_dau: list[float],
    diem_cuoi: list[float],
    cao: float = 1.1,
    day: float = 0.02,
    cao_do: float = 0.0,
    ten: str | None = None,
) -> dict:
    """Dung lan can kinh cho ban cong hoac cau thang.

    cao: chieu cao lan can, quy chuan toi thieu 1.1m cho nha tren 9 tang.
    """
    return _goi("create_lan_can", diem_dau=diem_dau, diem_cuoi=diem_cuoi,
                cao=cao, day=day, cao_do=cao_do, ten=ten)
```

Ba dieu bat buoc:

1. **Phai co chu thich kieu cho moi tham so.** FastMCP doc chu ky ham de
   sinh schema. Thieu chu thich thi tham so do khong xuat hien trong schema.
2. **Docstring la tai lieu ma AI doc.** Viet ro don vi, truong hop dung, cac
   gia tri thong dung. Day la thu duy nhat AI co de biet dung tool the nao.
3. **Khong them `from __future__ import annotations` vao file nay.** FastMCP
   ban cu doc chu thich truc tiep tu chu ky ham; neu bat che do chu thich
   dang chuoi, no se bao `issubclass() arg 1 must be a class` khi dang ky tool.

### Cho 3: tai lieu

Them vao `docs/cong-cu.md`, dung nhom.

### Kiem tra da dang ky duoc chua

```bash
python -c "
import asyncio
from blender_mcp_xaydung.server import mcp
tools = asyncio.run(mcp.list_tools())
print(len(tools), 'tool')
print([t.name for t in tools])
"
```

## Viet code chay tren may nguoi khac

Day la nhung cho hay vo khi addon chay tren mot ban Blender khac:

### Tim node shader theo kieu, khong theo ten

Ten node doi theo ngon ngu giao dien Blender. Nguoi dung dat giao dien tieng
Nhat thi `nodes["Principled BSDF"]` bao loi.

```python
# Sai
node = mat.node_tree.nodes["Principled BSDF"]

# Dung
node = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
```

### Ten input cua node cung doi

`Specular` thanh `Specular IOR Level` tu Blender 4.0. Nen thu lan luot:

```python
def _set_input(node, names, value):
    for name in names:
        if name in node.inputs:
            node.inputs[name].default_value = value
            return True
    return False
```

### Khong viet cung ten enum

Danh sach engine render khac nhau giua cac ban. Doc tu `bl_rna` truoc, hoac
gan trong `try` roi doc thong bao loi:

```python
try:
    scene.render.engine = engine
except TypeError as exc:
    # Thong bao loi liet ke day du cac ten hop le
    raise ValueError(f"Engine '{engine}' khong dung. {exc}") from exc
```

### Mau vat lieu phai dat len node

`material.diffuse_color` chi doi mau trong khung nhin, khong anh huong ket
qua render. Mau that nam o input cua node shader.

### bpy khong an toan tu luong phu

Dung tao thread goi bpy. Addon dung `bpy.app.timers` de moi thu chay tren
luong chinh. Xem [kien-truc.md](kien-truc.md).

## Them vat lieu moi

Sua bang `VAT_LIEU` trong `addon.py`:

```python
VAT_LIEU = {
    "be_tong": ((0.60, 0.60, 0.58, 1.0), 0.90, 0.0, 0.0),
    #            mau RGBA                 nham  kim loai  trong suot
}
```

Nho cap nhat bang trong `docs/cong-cu.md` va `guides/vat-lieu.md`.

## Them huong dan nghiep vu

Tao file `.md` moi trong `src/blender_mcp_xaydung/guides/`. Tool `huong_dan`
tu nhan ra, khong phai dang ky.

Huong dan la cho de viet nhung kien thuc khong dang nhet vao docstring cua
tung tool: thu tu lam viec, cac con so quy chuan, loi hay gap.

## Lop soat code

`safe_mode.py` doc code thanh cay cu phap roi tim mau nguy hiem. Them mau
moi bang cach sua cac tap hop o dau file:

| Tap hop | Chan gi |
|---|---|
| `BLOCKED_MODULES` | Module khong duoc nhap |
| `BLOCKED_BUILTINS` | Ham dung san khong duoc goi |
| `BLOCKED_OS_ATTRS` | Thuoc tinh nguy hiem tren `os` |
| `BLOCKED_BPY_OPS` | Lenh Blender gay mat du lieu |
| `BLOCKED_DUNDERS` | Thuoc tinh noi bo dung de pha rao |

Them mau moi thi them test tuong ung vao `tests/test_safe_mode.py`, ca
truong hop phai chan lan truong hop khong duoc chan nham.

Lop nay chan loi ro rang, khong phai tuong lua. Nguoi quyet tam van vuot
duoc. Muc tieu la chan tai nan, khong phai chan ke tan cong.

## Quy uoc code

- Comment va docstring viet tieng Viet khong dau, de chay duoc tren moi may
  khong phu thuoc bang ma
- Ten ham va tham so trong tool MCP dat tieng Viet khong dau, vi AI doc ten
  do de hieu y nghia
- Ten ham noi bo trong addon dat tieng Anh theo thoi quen cua bpy
- Moi so do trong tool tinh bang met
- Khong them tinh nang chua duoc yeu cau

## Phat hanh

```bash
python -m build
python -m twine upload dist/*
```

Truoc khi phat hanh, chay du ca hai bo kiem tra:

```bash
pytest
blender --background --python scripts/tu-kiem-tra.py
```
