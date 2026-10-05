# Hướng dẫn cài đặt chi tiết

Tài liệu này viết cho người chưa từng cài MCP bao giờ. Làm từng bước, mỗi bước
đều có cách kiểm tra đã đạt chưa trước khi sang bước sau.

## Hiểu trước khi cài

Bạn sẽ cài **hai** thứ, không phải một:

1. **MCP server**: một chương trình Python. Claude tự khởi động nó khi cần.
2. **Addon**: một file Python nạp vào trong Blender.

Hai thứ này nói chuyện với nhau qua cổng 9877 trên chính máy bạn.

Ví như gọi điện cho người trong phòng kín: MCP server là người trực tổng đài,
addon là người cầm máy bên trong. Thiếu một bên là không nói được.

## Bước 0: kiểm tra máy đã sẵn sàng

```bash
python --version
```

Phải từ 3.10 trở lên. Nếu chưa có Python, tải ở python.org, nhớ tích ô
"Add Python to PATH" khi cài trên Windows.

Blender phải từ bản 3.0 trở lên. Mở Blender, vào `Help > About Blender` để xem.

## Bước 1: cài gói Python

```bash
git clone https://github.com/andyluu98/vn-mcp-blender
cd vn-mcp-blender
pip install -e .
```

### Kiểm tra

```bash
vn-mcp-blender --version
```

Ra số phiên bản là đạt. Nếu báo "command not found", thử:

```bash
python -m vn_mcp_blender.cli --version
```

Nếu cách này chạy được thì thư mục script của Python chưa nằm trong PATH.
Không sao, ở bước 3 bạn khai báo bằng `python -m` thay vì tên lệnh.

## Bước 2: cài addon vào Blender

### Cách a: để lệnh tự làm

```bash
vn-mcp-blender install-addon
```

Lệnh này tìm mọi bản Blender trên máy rồi chép addon vào. Nó in ra đường dẫn
đã chép.

### Cách b: cài tay

Lấy đường dẫn file addon:

```bash
vn-mcp-blender addon-path
```

Rồi trong Blender: `Edit > Preferences > Add-ons > Install...`, chọn đúng file đó.

### Bật addon

1. Trong Blender mở `Edit > Preferences > Add-ons`
2. Gõ "MCP" vào ô tìm kiếm
3. Thấy dòng **Interface: MCP Xây Dựng**, tích vào ô vuông bên trái
4. Đóng cửa sổ Preferences

### Bật kết nối

1. Đưa chuột vào khung nhìn 3D, bấm phím **N**. Một thanh dọc hiện ra bên phải.
2. Trong thanh đó có các tab dọc. Chọn tab **MCP Xây Dựng**.
3. Bấm nút **Bật kết nối**.
4. Dòng chữ đổi thành "Đang chạy ở cổng 9877" kèm dấu tích.

### Kiểm tra

Mở một cửa sổ dòng lệnh khác, giữ Blender đang mở:

```bash
vn-mcp-blender check
```

Phải in ra thông tin Blender. Nếu báo không nối được, xem [xu-ly-loi.md](xu-ly-loi.md).

## Bước 3: khai báo với Claude

### Claude Code

Mở file `~/.claude.json` (trên Windows là `C:\Users\<tên>\.claude.json`),
tìm mục `mcpServers`, thêm vào:

```json
{
  "mcpServers": {
    "vn-blender": {
      "type": "stdio",
      "command": "vn-mcp-blender",
      "args": []
    }
  }
}
```

Trên Windows, nếu tên lệnh không chạy được thì dùng:

```json
{
  "mcpServers": {
    "vn-blender": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "vn_mcp_blender.cli"]
    }
  }
}
```

### Claude Desktop

File cấu hình:

| Hệ điều hành | Đường dẫn |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Nội dung giống Claude Code ở trên.

### Kiểm tra

Khởi động lại Claude, rồi gõ:

> kiểm tra kết nối Blender

Claude phải trả về phiên bản Blender và số đối tượng đang có.

## Thứ tự khởi động hàng ngày

Mỗi lần làm việc, làm theo thứ tự này:

1. Mở Blender trước
2. Bấm **Bật kết nối** trong tab MCP Xây Dựng
3. Mở Claude

Nếu mở Claude trước rồi mới mở Blender vẫn được, chỉ cần bấm Bật kết nối là
xong, không phải khởi động lại Claude.

## Dùng chung với addon blender-mcp khác

Bộ này dùng cổng **9877**, còn addon `blender-mcp` phổ biến dùng 9876. Hai cái
chạy song song được, không đâm nhau.

Nếu muốn đổi cổng, sửa ở cả hai nơi:

- Trong Blender: ô "Cổng" ngay trên nút Bật kết nối
- Trong mã nguồn: sửa `DEFAULT_PORT` trong `src/vn_mcp_blender/__init__.py`

## Gỡ cài đặt

```bash
pip uninstall vn-mcp-blender
```

Addon trong Blender gỡ riêng: `Edit > Preferences > Add-ons`, tìm MCP Xây Dựng,
bấm mũi tên mở rộng rồi chọn Remove.
