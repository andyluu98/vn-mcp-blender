# VN MCP Blender

MCP server giúp AI dựng mô hình nhà 3D trong Blender từ dữ liệu kiến trúc,
đọc được mặt bằng DXF từ AutoCAD và bóc khối lượng từ chính mô hình.

Viết riêng cho hồ sơ nhà ở Việt Nam: tường 220 và 110, cột bê tông, dầm, sàn,
cầu thang, mái bằng. Mọi số đo tính bằng mét.

## Làm được gì

| Nhóm | Nội dung |
|---|---|
| Dựng cấu kiện | Tường, sàn, cột, dầm, cầu thang, mái, khoét lỗ cửa |
| Đọc bản vẽ | Nhập mặt bằng DXF, rút trục tim tường và vị trí cột |
| Vật liệu | 10 vật liệu xây dựng dựng sẵn: bê tông, gạch, kính, gỗ, thép, ngói |
| Nhìn và render | Chụp khung nhìn để kiểm tra, render ảnh phối cảnh |
| Xuất | glb, fbx, obj, stl |
| Bóc khối lượng | Đo thể tích từ hình học thật, đã trừ lỗ cửa |

Tổng cộng 30 công cụ. Danh sách đầy đủ ở [docs/cong-cu.md](docs/cong-cu.md).

## Cài đặt

Cần hai thứ: MCP server và addon trong Blender. Xem hướng dẫn từng bước ở
[docs/cai-dat.md](docs/cai-dat.md), hoặc làm nhanh như dưới.

### Yêu cầu

- Blender 3.0 trở lên
- Python 3.10 trở lên
- Claude Code, Claude Desktop, hoặc bất kỳ ứng dụng nào nối được MCP

### Bước 1: cài gói

```bash
git clone https://github.com/andyluu98/vn-mcp-blender
cd vn-mcp-blender
pip install -e .
```

### Bước 2: cài addon vào Blender

```bash
vn-mcp-blender install-addon
```

Lệnh này tự tìm Blender trên máy và chép addon vào. Sau đó trong Blender:

1. `Edit > Preferences > Add-ons`
2. Tìm **MCP Xây Dựng**, tích vào ô bên trái để bật
3. Trong khung nhìn 3D, bấm phím **N** để mở thanh bên
4. Chọn tab **MCP Xây Dựng**, bấm **Bật kết nối**

### Bước 3: khai báo với Claude

Thêm vào file cấu hình MCP:

```json
{
  "mcpServers": {
    "vn-blender": {
      "command": "vn-mcp-blender"
    }
  }
}
```

File cấu hình nằm ở:

| Ứng dụng | Đường dẫn |
|---|---|
| Claude Code | `~/.claude.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |

Khởi động lại Claude, rồi thử bảo: "kiểm tra kết nối Blender".

### Kiểm tra nhanh không cần Claude

```bash
vn-mcp-blender check
```

## Dùng thử

Mở Blender, bật addon, rồi bảo Claude:

> Dựng cho tôi nhà phố 5m x 14m, 1 tầng, tường bao 220 cao 3.1m, sàn dày 100,
> 4 cột 220x220 ở bốn góc. Xong thì cho tôi xem ảnh.

Hoặc dựng từ bản vẽ có sẵn:

> Đọc file F:/ban-ve/mat-bang.dxf xem có layer gì, rồi dựng tường lên 3D.

Trong thư mục [examples/](examples/) có sẵn mô tả một căn nhà phố 5x20m, 3 tầng
1 tum lấy từ hồ sơ thật. Dựng thử bằng:

```bash
blender --background --python scripts/dung-vi-du.py
```

## Kiến trúc

Blender không nói chuyện MCP trực tiếp được, nên bộ này chia hai nửa:

```
Claude  <--stdio/MCP-->  MCP server  <--socket TCP 9877-->  Addon trong Blender
```

MCP server khai báo công cụ và đọc file DXF. Addon làm mọi việc dựng hình bằng
thư viện bpy. Chi tiết ở [docs/kien-truc.md](docs/kien-truc.md).

Cổng mặc định là **9877**, chọn khác 9876 để không đâm vào addon `blender-mcp`
phổ biến nếu bạn đang dùng cả hai.

## Phát triển

```bash
pip install -e ".[dev]"
pytest
```

50 test chạy được mà không cần mở Blender. Riêng phần hình học có script tự
kiểm tra chạy trong Blender thật:

```bash
blender --background --python scripts/tu-kiem-tra.py
```

Cách thêm công cụ mới: [docs/phat-trien.md](docs/phat-trien.md).

## An toàn

Công cụ `chay_python` cho phép chạy Python bất kỳ trong Blender. Code được soát
trước để chặn xóa file, chạy lệnh hệ thống, và các thao tác làm mất bản vẽ đang
mở. Xem `src/vn_mcp_blender/safe_mode.py`.

Bộ soát này chặn lỗi rõ ràng, không phải tường lửa. Vẫn nên đọc code trước khi
cho chạy trên bản vẽ quan trọng, và lưu file trước khi làm việc lớn.

Bộ công cụ này **không gửi dữ liệu đi đâu**. Không có telemetry.

## Ghi chú về ngôn ngữ

Tài liệu và chữ hiện trên giao diện viết tiếng Việt có dấu. Riêng chú thích
trong mã nguồn viết không dấu, để chạy được trên mọi máy không phụ thuộc bảng
mã, kể cả khi Blender dùng bản Python cũ hoặc hệ điều hành đặt locale lạ.

## Giấy phép

MIT. Xem [LICENSE](LICENSE).

Dự án độc lập, không liên quan đến Blender Foundation.
