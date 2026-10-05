# Hướng dẫn dựng nhà

## Thứ tự dựng

Dựng theo đúng thứ tự thì các cấu kiện khớp nhau, không phải sửa lại:

1. **Sàn tầng 1** trước, làm mặt chuẩn cho mọi thứ bên trên.
2. **Cột** theo lưới trục.
3. **Tường** bao trước, tường ngăn sau.
4. **Khoét cửa** sau khi tường đã dựng xong.
5. **Dầm** ở cao độ đáy dầm.
6. **Sàn tầng trên**, rồi lặp lại từ bước 2.
7. **Cầu thang** sau cùng, khi đã biết cao độ thực của hai sàn.
8. **Mái** cuối cùng.

## Cao độ: chỗ hay sai nhất

Ba con số hay bị lẫn:

| Khái niệm | Nghĩa | Ví dụ |
|---|---|---|
| Cao độ sàn | Mặt trên của sàn hoàn thiện | +3.900 |
| Chiều cao tầng | Khoảng cách giữa hai cao độ sàn | 3.600 |
| Chiều cao tường | Chiều cao tầng trừ chiều cao dầm | 3.600 - 0.350 = 3.250 |

Tường xây từ mặt sàn lên đến đáy dầm, không phải lên đến sàn trên. Nhập `cao`
cho `dung_tuong` là chiều cao tường, không phải chiều cao tầng.

## Trục tim tường

`dung_tuong` nhận hai điểm trên **trục tim** tường, không phải mép tường.
Tường dày 0.22 sẽ ăn đều 0.11 mỗi bên so với đường nối hai điểm.

Khi nhập từ bản vẽ, nếu bản vẽ vẽ theo mép thì phải đổi về trục tim trước,
nếu không tường sẽ lệch nửa bề dày.

## Lưới trục nhà phố Việt Nam

Nhà phố mặt tiền 5m thường có:

- Hai hàng cột sát hai tường biên, cách nhau 4.78m (5.0 trừ hai nửa tường 0.22)
- Bước cột theo chiều sâu 3.5m đến 5m
- Cột 220x220 cho nhà 3 tầng, 220x300 từ 4 tầng trở lên

## Kích thước thường dùng

| Cấu kiện | Kích thước |
|---|---|
| Tường bao | 0.22 |
| Tường ngăn | 0.11 |
| Sàn | 0.10 đến 0.12 |
| Dầm chính | 0.22 x 0.35 |
| Dầm phụ | 0.22 x 0.30 |
| Cửa đi chính | 1.0 x 2.4 |
| Cửa đi phòng | 0.9 x 2.2 |
| Cửa đi WC | 0.75 x 2.1 |
| Cửa sổ | 1.2 x 1.5, bệ cửa 0.9 |
| Bậc thang | cao 0.165 đến 0.180, rộng 0.26 đến 0.30 |

## Cầu thang

Tích `so_bac x cao_bac` phải bằng chiều cao tầng. Ví dụ tầng cao 3.15m: 18 bậc
mỗi bậc 0.175m. Nếu không khớp, thang sẽ hụt hoặc vượt qua sàn tầng trên.

Công thức kiểm tra độ thoải: `2 x cao_bac + rong_bac` nên nằm trong khoảng
0.60 đến 0.65 mét. Với 0.175 và 0.27 thì được 0.615, đạt.

Thang dựng ra là bản nghiêng dày 0.12 cộng các bậc nằm trên, giống cấu tạo
thật. Nhờ vậy khối lượng bê tông bóc ra đúng, khoảng 1.1 đến 1.3 m3 mỗi vế
thang nhà phố.

## Kiểm tra lại bằng mắt

Sau mỗi bước dựng đáng kể, gọi `nhin` và thực sự nhìn ảnh. Các lỗi hay gặp mà
chỉ nhìn ảnh mới thấy:

- Khối bay lơ lửng vì nhập sai cao độ
- Tường xuyên qua nhau ở góc
- Cầu thang đâm vào sàn tầng trên
- Mái không phủ hết tường
- Tỷ lệ cửa sổ quá to so với tường

Đừng tin rằng hình đã đúng chỉ vì lệnh chạy không báo lỗi.

## Nếu ảnh render ra tối om

Thiếu ánh sáng môi trường. Gọi cả hai:

```
tao_den(kieu="SUN", goc_do=[55, 0, 25], cong_suat=4.0)
anh_sang_moi_truong(cuong_do=1.2)
```

Xem thêm hướng dẫn `vat-lieu`.
