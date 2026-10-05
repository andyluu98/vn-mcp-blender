# Hướng dẫn vật liệu và ánh sáng

## Vật liệu có sẵn

Gọi `tao_vat_lieu` với một trong các loại sau:

| Loại | Dùng cho |
|---|---|
| `be_tong` | Sàn, cột, dầm, mái lộ bê tông |
| `gach` | Tường gạch không trát |
| `tuong_son` | Tường đã trát và sơn, màu kem nhạt |
| `kinh` | Cửa sổ, vách kính, lan can kính |
| `go` | Cửa đi, sàn gỗ, lam gỗ |
| `thep` | Lan can, khung sắt |
| `ngoi` | Mái ngói |
| `gach_lat` | Sàn lát gạch |
| `da` | Ốp đá, bậc thang đá |
| `nhom` | Khung cửa nhôm kính |

Muốn màu khác thì truyền thêm `mau` dạng `[r, g, b]`, mỗi số từ 0 đến 1.

Nếu truyền `mau` bốn thành phần thì thành phần thứ tư là độ đục. Đặt 1.0 cho
vật liệu đặc; đặt thấp sẽ làm cấu kiện tàng hình khi render.

## Gắn vật liệu nhanh cho cả công trình

Gắn theo loại cấu kiện thay vì từng object:

1. Gọi `xem_canh` với `chi_cua_addon=True` để lấy danh sách kèm `loai_cau_kien`.
2. Tạo sẵn các vật liệu cần dùng.
3. Gọi `gan_vat_lieu` cho từng object theo loại của nó.

Cách gắn thông dụng: tường dùng `tuong_son`, sàn và cột và dầm dùng `be_tong`,
mái dùng `be_tong`, lan can dùng `kinh`.

## Ánh sáng

Một bộ đèn tối thiểu để nhìn rõ mô hình gồm **hai** thứ:

```
tao_den(kieu="SUN", goc_do=[55, 0, 25], cong_suat=4.0)
anh_sang_moi_truong(cuong_do=1.2)
```

Thiếu ánh sáng môi trường thì mọi mặt quay khỏi hướng nắng đều đen sì, ảnh
render ra tối om dù đã có nắng. Đây là lỗi hay gặp nhất khi ảnh render đầu
tiên ra không nhìn thấy gì.

Góc xoay quyết định hướng nắng. Thành phần thứ ba là hướng la bàn, tính ngược
chiều kim đồng hồ từ trục X dương:

| Hướng nắng | `goc_do` thứ ba |
|---|---|
| Đông | 0 |
| Bắc | 90 |
| Tây | 180 |
| Nam | 270 |

Nhà Việt Nam thường lấy nắng chiều từ hướng Tây, đặt 180 đến 225.

Quan trọng hơn: nắng phải chiếu vào đúng mặt mà camera đang nhìn. Nếu camera
đứng ở góc trước bên trái mà nắng rọi từ phía sau thì ảnh ra toàn bóng tối.

## Camera

Đặt camera cách nhà khoảng 1.5 đến 2 lần chiều rộng mặt tiền, cao ngang tầm
mắt khoảng 1.6m nếu muốn góc nhìn người đi đường, hoặc cao 8 đến 15m nếu muốn
nhìn bao quát.

```
tao_camera(vi_tri=[18, -16, 12], nhin_vao=[2.5, 6, 6], tieu_cu=35)
```

Tiêu cự 35 cho góc rộng, hợp với nhà phố chật hẹp. Tiêu cự 50 gần với mắt
người hơn nhưng phải lùi xa mới lấy hết nhà.

## Render

`nhin` chụp nhanh khung nhìn, dùng để kiểm tra trong lúc dựng.
`render_anh` chậm hơn nhưng cho ảnh đẹp, dùng khi đã dựng xong.

Engine nhanh là `BLENDER_EEVEE_NEXT` trên Blender 4.2 trở lên. Bản cũ hơn dùng
`BLENDER_EEVEE`. Nếu nhập sai tên, thông báo lỗi sẽ liệt kê tên hợp lệ.
