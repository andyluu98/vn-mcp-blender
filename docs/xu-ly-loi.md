# Xử lý lỗi

## Không nối được tới Blender

Thông báo đầy đủ:

> Không nối được tới Blender ở localhost:9877. Mở Blender, vào thanh bên khung
> nhìn 3D (phím N), chọn tab 'MCP Xây Dựng', rồi bấm 'Bật kết nối'.

Kiểm tra lần lượt:

### 1. Blender đã mở chưa

Addon chỉ chạy khi Blender đang mở. Đóng Blender là mất kết nối.

### 2. Addon đã bật chưa

`Edit > Preferences > Add-ons`, gõ "MCP" vào ô tìm, xem dòng **MCP Xây Dựng**
đã được tích chưa.

Nếu không thấy dòng nào, addon chưa được cài. Chạy lại:

```bash
vn-mcp-blender install-addon
```

Rồi khởi động lại Blender.

### 3. Đã bấm "Bật kết nối" chưa

Bật addon trong Preferences **chưa đủ**. Còn phải bấm nút Bật kết nối:

1. Đưa chuột vào khung nhìn 3D, bấm phím **N**
2. Chọn tab **MCP Xây Dựng**
3. Bấm **Bật kết nối**
4. Phải thấy dòng chữ "Đang chạy ở cổng 9877" kèm dấu tích

Đây là bước hay bị quên nhất.

### 4. Cổng có bị chiếm không

Nếu bấm Bật kết nối mà hiện lỗi đó, có chương trình khác đang giữ cổng 9877.

Xem ai đang giữ cổng:

```bash
netstat -ano | findstr 9877
```

Trên macOS hoặc Linux:

```bash
lsof -i :9877
```

Đổi cổng trong ô "Cổng" ngay trên nút Bật kết nối, rồi sửa lại cấu hình bên
MCP server cho khớp.

### 5. Hai cửa sổ Blender cùng mở

Chỉ một cửa sổ giữ được cổng. Cửa sổ thứ hai bấm Bật kết nối sẽ báo lỗi. Đóng
bớt đi còn một.

## Blender không trả lời, bị treo

Thông báo:

> Blender không trả lời lệnh 'X' trong 120 giây.

Addon chạy lệnh ngay trên luồng chính của Blender, nên một lệnh nặng sẽ làm
giao diện đứng hình. Đây là thiết kế có chủ ý, đổi lại là bpy chạy an toàn.

Làm gì:

1. Đợi thêm. Lệnh dựng vài nghìn cấu kiện thật sự tốn thời gian.
2. Mở cửa sổ Console của Blender để xem nó đang làm gì:
   - Windows: `Window > Toggle System Console`
   - macOS, Linux: khởi động Blender từ terminal sẽ thấy log
3. Nếu treo hẳn, tắt Blender rồi mở lại. Nhớ lưu file trước khi làm việc lớn.

## Code bị chặn

Thông báo:

> Code bị chặn vì các lý do sau: dòng 3: nhập module bị chặn 'subprocess'

Công cụ `chay_python` soát code trước khi chạy, chặn các thao tác có thể xóa
file hoặc làm mất bản vẽ.

Nếu đoạn code thật sự an toàn và bạn cần chạy:

```powershell
$env:VN_MCP_UNSAFE = "1"
```

Trên macOS hoặc Linux:

```bash
export VN_MCP_UNSAFE=1
```

Rồi khởi động lại MCP server (khởi động lại Claude).

Cân nhắc kỹ trước khi tắt. Lớp soát này tồn tại vì code chạy trong Blender có
đầy đủ quyền của bạn trên máy.

## Lỗi khi đọc file DXF

### "Không đọc được file DXF"

- Kiểm tra đường dẫn có đúng không. Trên Windows dùng dấu gạch chéo xuôi hoặc
  gạch chéo ngược nhân đôi: `F:/ban-ve/a.dxf` hoặc `F:\\ban-ve\\a.dxf`
- File phải là `.dxf`. Thư viện ezdxf không đọc được `.dwg`. Trong AutoCAD
  dùng `Save As` chọn định dạng DXF.

### Đọc được nhưng không ra tường nào

Gọi `doc_layer_dxf` xem bản vẽ đặt tên layer gì, rồi truyền đúng tên vào
`layer_tuong`:

```
doc_mat_bang_dxf(duong_dan="...", layer_tuong=["TUONG-220", "TUONG-110"])
```

### Tường ra sai kích thước, to gấp nghìn lần

Bản vẽ dùng đơn vị mét chứ không phải milimet. Đặt `ty_le=1.0`.

Ngược lại, nếu nhà chỉ bé bằng hạt gạo thì bản vẽ dùng mét mà bạn để
`ty_le=0.001`.

### Đọc được cả 5 mặt bằng chồng lên nhau

Hồ sơ Việt Nam hay xếp nhiều mặt bằng cạnh nhau trên cùng một không gian.
Dùng `vung` để lấy riêng một cái:

```
doc_mat_bang_dxf(duong_dan="...", vung=[0, 0, 5000, 20000])
```

Tọa độ trong `vung` tính theo đơn vị bản vẽ (milimet), không phải mét.

Dùng `goc` để đưa mặt bằng đó về gốc tọa độ:

```
doc_mat_bang_dxf(duong_dan="...", vung=[9000, 0, 14000, 20000], goc=[9000, 0])
```

## Lỗi hình học

### Tường lệch nửa bề dày

`dung_tuong` nhận hai điểm trên **trục tim**, không phải mép tường. Nếu bản vẽ
của bạn ghi theo mép, phải cộng trừ nửa bề dày trước khi nhập.

### Tường bay lơ lửng

Kiểm tra `cao_do`. Đây là cao độ chân tường, không phải cao độ sàn tầng. Tường
tầng 2 có sàn ở cao độ 3.9 thì chân tường cũng ở 3.9.

### Cầu thang đâm vào sàn tầng trên

Tích `so_bac x cao_bac` phải đúng bằng chiều cao tầng. Tầng cao 3.6m:

- 20 bậc x 0.180 = 3.60, đạt
- 18 bậc x 0.175 = 3.15, hụt 0.45m

### Khoét cửa không ăn gì

- Tên tường phải lấy từ kết quả trả về của `dung_tuong`, không tự đặt
- Chỉ khoét được trên tường do chính bộ này dựng ra
- `khoang_cach` tính từ điểm đầu của tường. Nếu vượt quá chiều dài tường thì
  khối cắt nằm ngoài, không cắt vào đâu

### Ảnh render ra tối om hoặc trống rỗng

Thiếu ánh sáng môi trường. Chỉ có một nguồn SUN thì mọi mặt quay khỏi hướng
nắng đều đen sì. Gọi cả hai:

```
tao_den(kieu="SUN", goc_do=[55, 0, 25], cong_suat=4.0)
anh_sang_moi_truong(cuong_do=1.2)
```

Nếu vẫn trống rỗng thì chưa có camera, hoặc camera hướng ra chỗ khác. Gọi
`tao_camera` với `nhin_vao` trỏ vào giữa ngôi nhà.

### Nhà biến mất hoàn toàn sau khi gán vật liệu

Vật liệu có độ đục quá thấp sẽ làm cấu kiện tàng hình. Mười vật liệu dựng sẵn
đều đã đặt đúng, chỉ `kinh` mới trong suốt. Nếu bạn tự truyền `mau` bốn thành
phần thì thành phần thứ tư là độ đục, đặt 1.0 cho vật liệu đặc.

## Lỗi khi xuất file

### "Thư mục không tồn tại"

Tạo thư mục trước. MCP server không tự tạo thư mục, để tránh ghi nhầm chỗ.

### Xuất obj hoặc stl báo không có lệnh

Tên lệnh xuất đổi giữa các bản Blender. Bộ này dùng `bpy.ops.wm.obj_export` và
`bpy.ops.wm.stl_export`, có từ Blender 3.3 trở lên. Bản cũ hơn thì xuất `glb`
hoặc `fbx`.

## Cách lấy thêm thông tin

Mở Console của Blender, mọi lỗi trong addon đều in đầy đủ vết lỗi ở đó:

- Windows: `Window > Toggle System Console`
- macOS, Linux: khởi động Blender từ terminal

Kiểm tra nhanh cả đường truyền, không cần Claude:

```bash
vn-mcp-blender check
```

Kiểm tra phần hình học, không cần mở giao diện Blender:

```bash
blender --background --python scripts/tu-kiem-tra.py
```
