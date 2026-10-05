# Hướng dẫn phát triển

## Chuẩn bị

```bash
git clone https://github.com/andyluu98/vn-mcp-blender
cd vn-mcp-blender
pip install -e ".[dev]"
pytest
```

50 test chạy được mà không cần mở Blender. Chúng dùng socket giả và file DXF
tự sinh.

Phần hình học có script riêng, chạy trong Blender thật:

```bash
blender --background --python scripts/tu-kiem-tra.py
```

Script này gọi thẳng các hàm dựng hình rồi đo lại kết quả. Mã thoát 0 là đạt.

Có thêm script dựng cả ngôi nhà mẫu rồi bóc khối lượng:

```bash
blender --background --python scripts/dung-vi-du.py
blender --background --python scripts/dung-vi-du.py -- --render anh.png
```

## Thêm một công cụ mới

Một công cụ cần sửa **ba chỗ**. Thiếu chỗ nào là nó không chạy.

### Chỗ 1: handler trong addon

Thêm một phương thức vào lớp `Handlers` trong
`src/vn_mcp_blender/bundled/addon.py`:

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

Không phải đăng ký gì thêm. Lớp `MCPServer` tìm handler bằng `getattr`, nên
mọi phương thức công khai trong `Handlers` đều gọi được ngay. Phương thức bắt
đầu bằng dấu gạch dưới bị chặn, dùng làm hàm nội bộ.

### Chỗ 2: công cụ trong MCP server

Thêm vào `src/vn_mcp_blender/server.py`:

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

Ba điều bắt buộc:

1. **Phải có chú thích kiểu cho mọi tham số.** FastMCP đọc chữ ký hàm để sinh
   schema. Thiếu chú thích thì tham số đó không xuất hiện trong schema.
2. **Docstring là tài liệu mà AI đọc.** Viết rõ đơn vị, trường hợp dùng, các
   giá trị thông dụng. Đây là thứ duy nhất AI có để biết dùng công cụ thế nào.
3. **Không thêm `from __future__ import annotations` vào file này.** FastMCP
   bản cũ đọc chú thích trực tiếp từ chữ ký hàm; nếu bật chế độ chú thích dạng
   chuỗi, nó sẽ báo `issubclass() arg 1 must be a class` khi đăng ký công cụ.

### Chỗ 3: tài liệu

Thêm vào `docs/cong-cu.md`, đúng nhóm.

### Kiểm tra đã đăng ký được chưa

```bash
python -c "
import asyncio
from vn_mcp_blender.server import mcp
tools = asyncio.run(mcp.list_tools())
print(len(tools), 'tool')
print([t.name for t in tools])
"
```

## Viết code chạy trên máy người khác

Đây là những chỗ hay vỡ khi addon chạy trên một bản Blender khác:

### Tìm node shader theo kiểu, không theo tên

Tên node đổi theo ngôn ngữ giao diện Blender. Người dùng đặt giao diện tiếng
Nhật thì `nodes["Principled BSDF"]` báo lỗi.

```python
# Sai
node = mat.node_tree.nodes["Principled BSDF"]

# Đúng
node = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
```

### Tên input của node cũng đổi

`Specular` thành `Specular IOR Level` từ Blender 4.0. Nên thử lần lượt:

```python
def _set_input(node, names, value):
    for name in names:
        if name in node.inputs:
            node.inputs[name].default_value = value
            return True
    return False
```

### Không viết cứng tên enum

Danh sách engine render khác nhau giữa các bản. Đọc từ `bl_rna` trước, hoặc
gán trong `try` rồi đọc thông báo lỗi:

```python
try:
    scene.render.engine = engine
except TypeError as exc:
    # Thông báo lỗi liệt kê đầy đủ các tên hợp lệ
    raise ValueError(f"Engine '{engine}' khong dung. {exc}") from exc
```

### Màu vật liệu phải đặt lên node

`material.diffuse_color` chỉ đổi màu trong khung nhìn, không ảnh hưởng kết quả
render. Màu thật nằm ở input của node shader.

### Độ đục phải đặt 1.0 cho vật liệu đặc

Bảng `VAT_LIEU` có cột thứ tư là độ đục. Đặt nhầm 0.0 thì cấu kiện tàng hình
khi render, mà nhìn số đo khối lượng không phát hiện ra. Lỗi này đã từng xảy
ra, nên `scripts/tu-kiem-tra.py` có hẳn một phép kiểm cho cả 10 vật liệu.

### bpy không an toàn từ luồng phụ

Đừng tạo thread gọi bpy. Addon dùng `bpy.app.timers` để mọi thứ chạy trên
luồng chính. Xem [kien-truc.md](kien-truc.md).

## Hình học: đo lại, đừng tin số báo cáo

Khi thêm cấu kiện mới, luôn kiểm tra **cả hai**:

1. Thể tích hàm tự báo cáo
2. Thể tích đo từ mesh bằng `addon._mesh_volume(obj)`

Hai số này phải khớp. Lúc phát triển cầu thang, hai số lệch nhau đúng bằng
phần các bậc, hóa ra tiết diện bậc bị quay ngược chiều so với bản thang nên
tính ra thể tích âm. Nếu chỉ tin số báo cáo thì lỗi đó lọt.

Khi gộp nhiều khối vào một mesh, mọi tiết diện phải cùng chiều quay, và các
khối phải lồi. Khối lõm làm Blender chia tam giác sai, thể tích tính ra lệch.

## Thêm vật liệu mới

Sửa bảng `VAT_LIEU` trong `addon.py`:

```python
VAT_LIEU = {
    "be_tong": ((0.60, 0.60, 0.58, 1.0), 0.90, 0.0, 1.00),
    #            màu RGBA                 nhám  kim loại  độ đục
}
```

Nhớ cập nhật bảng trong `docs/cong-cu.md` và `guides/vat-lieu.md`.

## Thêm hướng dẫn nghiệp vụ

Tạo file `.md` mới trong `src/vn_mcp_blender/guides/`. Công cụ `huong_dan` tự
nhận ra, không phải đăng ký.

Hướng dẫn là chỗ để viết những kiến thức không đáng nhét vào docstring của
từng công cụ: thứ tự làm việc, các con số quy chuẩn, lỗi hay gặp.

## Lớp soát code

`safe_mode.py` đọc code thành cây cú pháp rồi tìm mẫu nguy hiểm. Thêm mẫu mới
bằng cách sửa các tập hợp ở đầu file:

| Tập hợp | Chặn gì |
|---|---|
| `BLOCKED_MODULES` | Module không được nhập |
| `BLOCKED_BUILTINS` | Hàm dựng sẵn không được gọi |
| `BLOCKED_OS_ATTRS` | Thuộc tính nguy hiểm trên `os` |
| `BLOCKED_BPY_OPS` | Lệnh Blender gây mất dữ liệu |
| `BLOCKED_DUNDERS` | Thuộc tính nội bộ dùng để phá rào |

Thêm mẫu mới thì thêm test tương ứng vào `tests/test_safe_mode.py`, cả trường
hợp phải chặn lẫn trường hợp không được chặn nhầm.

Lớp này chặn lỗi rõ ràng, không phải tường lửa. Người quyết tâm vẫn vượt được.
Mục tiêu là chặn tai nạn, không phải chặn kẻ tấn công.

## Quy ước code

- Chú thích và docstring trong mã nguồn viết tiếng Việt **không dấu**, để chạy
  được trên mọi máy không phụ thuộc bảng mã. Tài liệu và chữ hiện trên giao
  diện thì viết có dấu.
- Tên hàm và tham số trong công cụ MCP đặt tiếng Việt không dấu, vì AI đọc tên
  đó để hiểu ý nghĩa
- Tên hàm nội bộ trong addon đặt tiếng Anh theo thói quen của bpy
- Tên collection `MCP_XayDung` để không dấu, vì tên này đi theo file khi xuất
  sang glb hay fbx
- Mọi số đo trong công cụ tính bằng mét
- Không thêm tính năng chưa được yêu cầu

## Phát hành

```bash
python -m build
python -m twine upload dist/*
```

Trước khi phát hành, chạy đủ cả hai bộ kiểm tra:

```bash
pytest
blender --background --python scripts/tu-kiem-tra.py
```
