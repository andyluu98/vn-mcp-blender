# Danh sách công cụ

30 công cụ, chia 9 nhóm. Mọi số đo tính bằng **mét**, mọi góc tính bằng **độ**.

Tọa độ theo quy ước Blender: X sang phải, Y ra xa, Z lên trên. Mặt bằng nằm
trên mặt phẳng XY, cao độ là trục Z.

Tên công cụ và tên tham số để không dấu, vì đó là định danh trong mã nguồn.

## 1. Kết nối và hướng dẫn

### `kiem_tra_ket_noi()`

Kiểm tra nối được tới Blender chưa. Gọi đầu tiên mỗi phiên làm việc.

Trả về phiên bản Blender, phiên bản addon, file đang mở, số đối tượng.

### `huong_dan(chu_de)`

Đọc hướng dẫn nghiệp vụ. Bỏ trống `chu_de` để xem danh sách.

| Chủ đề | Nội dung |
|---|---|
| `dung-nha` | Thứ tự dựng, cách tính cao độ, kích thước thông dụng |
| `vat-lieu` | Bảng vật liệu, cách đặt đèn và camera |

## 2. Xem cảnh

### `xem_canh(chi_cua_addon=False, gioi_han=100)`

Liệt kê đối tượng trong cảnh kèm vị trí, kích thước, loại cấu kiện, vật liệu.

Đặt `chi_cua_addon=True` để chỉ xem những thứ bộ công cụ này dựng ra.

### `xem_doi_tuong(ten)`

Chi tiết một đối tượng: vị trí, góc xoay, tỷ lệ, kích thước, vật liệu,
modifier, và toàn bộ thuộc tính `xd_` đã gắn lúc dựng.

## 3. Dựng cấu kiện

### `dung_tuong(diem_dau, diem_cuoi, day=0.22, cao=3.0, cao_do=0.0, ten=None)`

Dựng một bức tường thẳng.

| Tham số | Ý nghĩa |
|---|---|
| `diem_dau`, `diem_cuoi` | `[x, y]` hai đầu **trục tim** tường, không phải mép |
| `day` | Bề dày. Tường bao 0.22, tường ngăn 0.11 |
| `cao` | Chiều cao tường, bằng chiều cao tầng trừ chiều cao dầm |
| `cao_do` | Cao độ chân tường |

Trả về tên object, chiều dài, diện tích mặt, thể tích.

Lưu tên object lại nếu sau này còn khoét cửa trên bức tường đó.

### `dung_san(dinh, day=0.10, cao_do=0.0, ten=None)`

Dựng tấm sàn bê tông từ đa giác mặt bằng.

`dinh` là danh sách `[x, y]` theo thứ tự vòng quanh, ít nhất 3 điểm.

`cao_do` là cao độ **mặt trên** của sàn. Tấm sàn đổ xuống dưới con số này,
đúng như cách thi công thật.

### `dung_cot(vi_tri, rong=0.22, sau=0.22, cao=3.0, cao_do=0.0, ten=None)`

Dựng cột chữ nhật. `vi_tri` là `[x, y]` tâm cột.

### `dung_dam(diem_dau, diem_cuoi, rong=0.22, cao=0.35, cao_do_day=2.65, ten=None)`

Dựng dầm ngang. `cao_do_day` là cao độ **đáy dầm**, không phải đỉnh dầm.

### `khoet_cua(ten_tuong, khoang_cach, rong, cao, be_cua=0.0)`

Khoét lỗ cửa đi hoặc cửa sổ trên tường đã dựng.

| Tham số | Ý nghĩa |
|---|---|
| `ten_tuong` | Tên object tường, lấy từ kết quả `dung_tuong` |
| `khoang_cach` | Từ điểm đầu của tường đến **mép trái** lỗ cửa |
| `be_cua` | Cao độ đáy lỗ so với chân tường. Cửa đi 0, cửa sổ thường 0.9 |

Chỉ khoét được trên tường do chính bộ công cụ này dựng, vì phải đọc lại trục
tim đã lưu trong thuộc tính `xd_diem_dau`.

### `dung_cau_thang(diem_dau, huong_do=0, so_bac=18, cao_bac=0.175, rong_bac=0.27, rong_thang=1.0, cao_do=0.0, day_ban=0.12, ten=None)`

Dựng cầu thang bê tông một vế: bản nghiêng cộng các bậc nằm trên.

`huong_do` là hướng đi lên: 0 theo trục X dương, 90 theo trục Y dương.

Tích `so_bac x cao_bac` phải bằng chiều cao tầng. Tầng cao 3.15m thì 18 bậc
mỗi bậc 0.175m.

`day_ban` là bề dày bản thang, đo vuông góc với mặt nghiêng.

Thang được dựng đúng cấu tạo thật chứ không đắp một khối đặc. Khác biệt này
quan trọng khi bóc khối lượng: thang 18 bậc rộng 1m dựng đúng cấu tạo ra
1.12 m3 bê tông, còn đắp khối đặc ra khoảng 10 m3, sai gần 9 lần.

### `dung_mai(dinh, kieu="bang", day=0.10, cao_do=0.0, do_doc=0.02, vuon=0.0, ten=None)`

Dựng mái bê tông.

| Tham số | Ý nghĩa |
|---|---|
| `kieu` | `bang` cho mái bằng có dốc thoát nước, `doc` cho mái một dốc |
| `do_doc` | Tỷ lệ dốc, 0.02 là 2 phần trăm |
| `vuon` | Phần mái đưa ra ngoài mép tường |

## 4. Dựng cả công trình một lượt

### `dung_tu_mo_ta(mo_ta)`

Cách nên dùng khi dựng nguyên một ngôi nhà. Nhanh hơn nhiều so với gọi từng
công cụ, vì chỉ một lượt trao đổi thay vì hàng chục lượt.

```json
{
  "ten": "Nha pho 5x14",
  "tang": [
    {
      "ten": "Tang1",
      "cao_do": 0.0,
      "cao_tuong": 3.1,
      "san":  {"dinh": [[0,0],[5,0],[5,14],[0,14]], "day": 0.1},
      "tuong": [
        {"diem_dau": [0,0], "diem_cuoi": [5,0],  "day": 0.22},
        {"diem_dau": [5,0], "diem_cuoi": [5,14], "day": 0.22}
      ],
      "cot": [
        {"vi_tri": [0,0], "rong": 0.22, "sau": 0.22}
      ],
      "cua": [
        {"tuong": 0, "khoang_cach": 2.0, "rong": 1.0, "cao": 2.4, "be_cua": 0}
      ]
    }
  ]
}
```

Trường `tuong` trong mỗi mục cửa là **số thứ tự** bức tường trong danh sách
`tuong` của chính tầng đó, đếm từ 0.

Trả về số lượng đã dựng từng loại, danh sách tên tường theo tầng, và danh sách
lỗi nếu có. Một cấu kiện lỗi không làm đổ cả mẻ.

Có file mẫu ở [examples/nha-pho-5x20m.json](../examples/nha-pho-5x20m.json).

## 5. Đọc bản vẽ DXF

### `doc_layer_dxf(duong_dan)`

Liệt kê layer trong file DXF kèm số lượng đối tượng từng loại.

**Gọi công cụ này trước** khi dùng `dung_nha_tu_dxf`, vì mỗi đơn vị thiết kế
đặt tên layer một kiểu.

### `doc_mat_bang_dxf(duong_dan, layer_tuong, layer_cot, vung, ty_le=0.001, goc)`

Đọc mặt bằng và trả về danh sách tường, cột. Chưa dựng gì trong Blender, dùng
để kiểm tra số liệu trước.

| Tham số | Ý nghĩa |
|---|---|
| `layer_tuong` | Danh sách tên layer chứa tường. Mặc định `A-WALL-220`, `A-WALL-110`, `A-WALL`, `TUONG` |
| `layer_cot` | Mặc định `A-COL`, `COT`, `A-COLUMN` |
| `vung` | `[x0, y0, x1, y1]` theo đơn vị bản vẽ, để lấy riêng một mặt bằng |
| `ty_le` | 0.001 cho bản vẽ milimet, 1.0 cho bản vẽ mét |
| `goc` | `[x, y]` điểm sẽ được đưa về gốc tọa độ |

Tham số `vung` cần khi hồ sơ xếp nhiều mặt bằng cạnh nhau trên cùng một không
gian, kiểu tầng 1 tầng 2 tầng 3 nằm ngang hàng.

### `dung_nha_tu_dxf(duong_dan, cao_tuong=3.0, cao_do=0.0, ...)`

Đọc mặt bằng DXF rồi dựng thẳng tường và cột trong Blender. Nhận cùng các tham
số như công cụ trên, thêm `cao_tuong`, `cao_do`, `dung_cot_luon`.

## 6. Vật liệu

### `tao_vat_lieu(ten, loai="be_tong", mau=None)`

| Loại | Dùng cho |
|---|---|
| `be_tong` | Sàn, cột, dầm, mái lộ bê tông |
| `gach` | Tường gạch không trát |
| `tuong_son` | Tường đã trát và sơn |
| `kinh` | Cửa sổ, vách kính, lan can kính |
| `go` | Cửa đi, sàn gỗ |
| `thep` | Lan can, khung sắt |
| `ngoi` | Mái ngói |
| `gach_lat` | Sàn lát gạch |
| `da` | Ốp đá, bậc thang đá |
| `nhom` | Khung cửa nhôm kính |

Truyền `mau` dạng `[r, g, b]`, mỗi số từ 0 đến 1, để đổi màu riêng.

### `gan_vat_lieu(ten_doi_tuong, ten_vat_lieu)`

Gắn vật liệu đã tạo lên một object.

## 7. Sửa, xóa, nhân bản

### `sua_doi_tuong(ten, vi_tri, xoay_do, ty_le, ten_moi)`

Đổi vị trí, góc xoay, tỷ lệ hoặc tên. Tham số nào bỏ trống thì giữ nguyên.

### `xoa_doi_tuong(ten)`

Xóa một đối tượng khỏi cảnh.

### `nhan_ban(ten, lech, ten_moi=None)`

`lech` là `[dx, dy, dz]`. Tiện để tạo các tầng giống nhau: dựng tầng 1 xong
thì nhân bản lên cao độ tầng 2.

### `xoa_toan_bo(chi_cua_addon=True)`

Mặc định chỉ xóa trong collection `MCP_XayDung`, không đụng tới vật người dùng
tự làm. Đặt `False` để xóa sạch cả cảnh, cân nhắc kỹ.

## 8. Nhìn, render, xuất

### `tao_den(kieu="SUN", vi_tri, cong_suat=5.0, goc_do, ten)`

Tạo nguồn sáng. `kieu`: `SUN`, `POINT`, `SPOT`, `AREA`.

SUN dùng làm ánh nắng mặt trời, `goc_do` quyết định hướng nắng.

### `anh_sang_moi_truong(cuong_do=1.0, mau=None)`

Đặt ánh sáng môi trường, đóng vai bầu trời hắt sáng vào công trình.

Chỉ có một nguồn SUN thì mọi mặt quay khỏi hướng nắng đều đen sì, nhìn không
ra hình khối. **Gọi công cụ này cùng với `tao_den`**, nếu không ảnh render ra
tối om.

| `cuong_do` | Dùng cho |
|---|---|
| 0.5 | Trời chiều nắng gắt, bóng đổ đậm |
| 1.0 | Trời quang |
| 2.0 | Trời nhiều mây, hoặc muốn nhìn rõ mọi chi tiết |

### `tao_camera(vi_tri, nhin_vao, tieu_cu=35.0, dat_lam_chinh=True, ten)`

Đặt camera và tự hướng nó vào một điểm.

Tiêu cự 35 cho phối cảnh rộng, hợp nhà phố chật hẹp. Tiêu cự 50 gần với mắt
người hơn nhưng phải lùi xa mới lấy hết nhà.

### `cai_dat_render(rong=1920, cao=1080, engine=None, mau_anh=None)`

Engine thường dùng: `BLENDER_EEVEE_NEXT` cho nhanh, `CYCLES` cho đẹp. Tên
engine khác nhau giữa các bản Blender; nhập sai thì thông báo lỗi sẽ liệt kê
tên hợp lệ.

### `nhin(kich_thuoc_toi_da=1200)`

Chụp khung nhìn, trả về ảnh. **Gọi sau mỗi bước dựng đáng kể.** Nhiều lỗi chỉ
nhìn ảnh mới phát hiện: khối bay lơ lửng, tường xuyên nhau, sai tỷ lệ.

### `render_anh(duong_dan=None, kich_thuoc_toi_da=1600)`

Render bằng engine đang chọn. Chậm hơn `nhin` nhưng cho ảnh đẹp. Truyền
`duong_dan` để lưu lại file.

### `xuat_file(duong_dan, dinh_dang="glb", chi_cua_addon=False)`

`dinh_dang`: `glb`, `fbx`, `obj`, `stl`.

glb hợp để xem trên web và điện thoại, fbx hợp để đưa sang phần mềm khác.

### `boc_khoi_luong()`

Đo thể tích từng cấu kiện từ hình học thật, gom theo loại. Các lỗ cửa đã khoét
được trừ tự động.

Trả về từng nhóm cấu kiện kèm số lượng, thể tích, diện tích; và tổng bê tông,
tổng khối xây.

## 9. Nâng cao

### `chay_python(code)`

Chạy Python bất kỳ trong Blender, dùng khi không có công cụ sẵn phù hợp.

Gán giá trị vào biến tên `ket_qua` để nhận lại giá trị đó.

Code được soát trước để chặn xóa file, chạy lệnh hệ thống, và các thao tác làm
mất bản vẽ. Chi tiết ở [phat-trien.md](phat-trien.md).

Khi viết code chạy trên máy người khác:

- Tìm node shader theo thuộc tính `type`, không theo tên, vì tên đổi theo ngôn
  ngữ giao diện
- Không viết cứng tên enum, đọc danh sách hợp lệ từ `bl_rna` trước
