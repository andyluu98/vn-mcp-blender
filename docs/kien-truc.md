# Kiến trúc

## Vì sao phải chia hai phần

Blender không nói chuyện MCP được. Nó là phần mềm đồ họa, chỉ chạy Python bên
trong chính nó. MCP thì cần một chương trình đọc ghi qua stdio theo chuẩn riêng.

Nên bộ này chia làm hai:

```
          stdio (MCP)              socket TCP 9877
Claude <----------------> MCP server <-------------> Addon trong Blender
                          (tiến trình      JSON        (thư viện bpy)
                           riêng)
```

| Phần | Chạy ở đâu | Làm gì |
|---|---|---|
| MCP server | Tiến trình riêng, Claude tự khởi động | Khai báo 30 công cụ, đọc file DXF, soát code |
| Addon | Bên trong Blender | Dựng hình, đo khối lượng, chụp ảnh |

Phân chia này có một hệ quả cần nhớ: **MCP server không dựng được hình nào nếu
Blender chưa bật kết nối**. Mọi thao tác hình học đều phải qua addon.

## Giao thức

Mỗi bản tin gồm hai phần:

```
[4 byte độ dài, big-endian] [thân bản tin, JSON UTF-8]
```

Yêu cầu từ server sang addon:

```json
{"type": "create_wall", "params": {"diem_dau": [0, 0], "diem_cuoi": [5, 0]}}
```

Trả lời từ addon, một trong hai dạng:

```json
{"status": "success", "result": {"ten": "Tuong_220", "dai": 5.0}}
```

```json
{"status": "error", "message": "Không có tường tên X"}
```

### Vì sao ghi độ dài lên đầu

Socket TCP không giữ ranh giới bản tin. Gửi một cục 10KB thì bên nhận có thể
nhận thành ba lần, hoặc hai bản tin liên tiếp dính làm một.

Một số bộ MCP Blender khác giải quyết bằng cách đọc thêm cho đến khi JSON parse
được. Cách đó chạy được nhưng mỏng manh: nếu bản tin bị cắt ở đúng chỗ mà phần
đầu tình cờ vẫn là JSON hợp lệ, nó sẽ cắt nhầm.

Ghi độ dài lên đầu thì không phải đoán. Bên nhận biết chính xác cần đọc bao
nhiêu byte. Test `test_ghep_dung_khi_du_lieu_ve_tung_manh` kiểm chứng điều này
bằng cách gửi từng byte một.

## Addon chạy trên luồng chính

Thư viện bpy không an toàn khi gọi từ luồng phụ. Gọi bpy từ thread khác có thể
làm Blender sập mà không báo gì.

Nên addon không tạo thread. Nó đăng ký một hàm chạy định kỳ qua
`bpy.app.timers`, cứ 0.05 giây một lần:

```python
def _tick(self):
    try:
        client, _ = self.sock.accept()   # socket đặt chế độ không chặn
    except BlockingIOError:
        return TICK_SECONDS              # chưa ai gọi, chờ lượt sau
    self._serve(client)                  # xử lý ngay trên luồng chính
    return TICK_SECONDS
```

Socket đặt chế độ không chặn nên `accept()` trả về ngay nếu chưa ai gọi. Khi có
kết nối thì xử lý luôn trên luồng chính, dùng bpy thoải mái.

Đổi lại, một lệnh nặng sẽ làm Blender đứng hình trong lúc chạy. Đây là đánh đổi
có chủ ý: thà để Blender đứng vài giây còn hơn làm nó sập.

## Mỗi kết nối một lệnh

MCP server không giữ kết nối lâu. Mỗi lệnh mở một socket mới rồi đóng lại.

Giữ kết nối lâu sẽ chết khi người dùng tắt mở Blender, và phải viết thêm logic
nối lại. Chi phí mở socket nội bộ chỉ vài phần nghìn giây, không đáng để đánh
đổi lấy sự phức tạp đó.

## Collection riêng

Mọi thứ addon dựng ra đều nằm trong collection tên `MCP_XayDung`. Nhờ vậy:

- Người dùng xóa sạch kết quả bằng một thao tác, không đụng tới vật tự làm
- Công cụ `xoa_toan_bo` mặc định chỉ xóa trong collection này
- Công cụ `boc_khoi_luong` chỉ đếm cấu kiện trong đây

Tên collection cố tình để không dấu, vì tên này đi theo file khi xuất sang glb
hay fbx, mà một số phần mềm nhận mô hình vẫn còn vấp ký tự Unicode.

## Nhãn cấu kiện

Mọi object addon tạo ra đều được gắn thêm thuộc tính tùy biến bắt đầu bằng `xd_`:

| Thuộc tính | Ý nghĩa |
|---|---|
| `xd_loai` | tuong, san, cot, dam, cau_thang, mai |
| `xd_day`, `xd_cao`, `xd_dai` | Số đo danh nghĩa lúc dựng |
| `xd_diem_dau`, `xd_diem_cuoi` | Trục tim tường, dùng để khoét cửa sau này |
| `xd_the_tich`, `xd_dien_tich` | Số đo tính sẵn |

Nhờ các nhãn này mà `boc_khoi_luong` gom được theo loại cấu kiện, và `khoet_cua`
biết tường nằm ở đâu để đặt khối cắt cho đúng.

## Bóc khối lượng đo từ hình thật

`boc_khoi_luong` không cộng lại các số đo danh nghĩa. Nó đo thể tích thực của
từng khối bằng bmesh:

```python
bm.from_mesh(obj.data)
bm.transform(obj.matrix_world)
volume = abs(bm.calc_volume(signed=True))
```

Nhờ vậy các lỗ cửa đã khoét được trừ tự động. Tường 5m x 3m dày 0.22 được
3.300 m3; khoét cửa 1.0 x 2.2 thì còn đúng 2.816 m3. Con số này được kiểm chứng
trong `scripts/tu-kiem-tra.py`.

Cách đo này còn bắt được lỗi hình học mà số đo danh nghĩa giấu đi. Lúc phát
triển, cầu thang từng bị quay ngược mặt nên thể tích tính ra âm, phép so giữa
thể tích đo được và thể tích tính tay phát hiện ngay.

## Đọc DXF ở phía server

Việc đọc file DXF làm ở MCP server, không làm trong addon. Lý do: thư viện
ezdxf không có sẵn trong Python của Blender, mà bắt người dùng cài thêm vào
Blender thì phiền.

Server đọc DXF, rút ra trục tim tường và vị trí cột, rồi gửi sang addon dưới
dạng các lệnh dựng hình bình thường.

### Cách nhận ra một bức tường trên bản vẽ

Bản vẽ kiến trúc vẽ tường bằng polyline kín, hình chữ nhật rất dẹt. Thuật toán
trong `dxf.py`:

1. Tìm cạnh dài nhất của hình, lấy làm hướng
2. Chiếu mọi đỉnh lên hướng đó và lên hướng vuông góc
3. Phạm vi theo hướng dọc là chiều dài, theo hướng ngang là bề dày
4. Nếu chiều dài không gấp bề dày ít nhất 2.5 lần thì bỏ qua, không phải tường
5. Trục tim nằm giữa hai cạnh dài

Cách này đọc được cả tường vẽ xiên, không chỉ tường thẳng theo trục. Ngưỡng
2.5 lần lọc bỏ các hình vuông nhỏ như ký hiệu hay chú thích nằm nhầm trên
layer tường.

## Cây thư mục

```
src/vn_mcp_blender/
  __init__.py       Phiên bản, cổng mặc định
  server.py         Khai báo 30 công cụ MCP
  connection.py     Client socket, đóng gói bản tin
  dxf.py            Đọc bản vẽ DXF
  safe_mode.py      Soát code Python trước khi chạy
  addon_manager.py  Tìm Blender và chép addon vào
  cli.py            Dòng lệnh
  guides/           Hướng dẫn nghiệp vụ, công cụ huong_dan đọc từ đây
  bundled/addon.py  Addon chạy trong Blender
```
