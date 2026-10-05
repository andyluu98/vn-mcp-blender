# Huong dan dung nha

## Thu tu dung

Dung theo dung thu tu thi cac cau kien khop nhau, khong phai sua lai:

1. **San tang 1** truoc, lam mat chuan cho moi thu ben tren.
2. **Cot** theo luoi truc.
3. **Tuong** bao truoc, tuong ngan sau.
4. **Khoet cua** sau khi tuong da dung xong.
5. **Dam** o cao do day dam.
6. **San tang tren**, roi lap lai tu buoc 2.
7. **Cau thang** sau cung, khi da biet cao do thuc cua hai san.
8. **Mai** cuoi cung.

## Cao do: cho hay sai nhat

Ba con so hay bi lan:

| Khai niem | Nghia | Vi du |
|---|---|---|
| Cao do san | Mat tren cua san hoan thien | +3.900 |
| Chieu cao tang | Khoang cach giua hai cao do san | 3.600 |
| Chieu cao tuong | Chieu cao tang tru chieu cao dam | 3.600 - 0.350 = 3.250 |

Tuong xay tu mat san len den day dam, khong phai len den san tren. Nhap
`cao` cho `dung_tuong` la chieu cao tuong, khong phai chieu cao tang.

## Truc tim tuong

`dung_tuong` nhan hai diem tren **truc tim** tuong, khong phai mep tuong.
Tuong day 0.22 se an deu 0.11 moi ben so voi duong noi hai diem.

Khi nhap tu ban ve, neu ban ve ve theo mep thi phai doi ve truc tim truoc,
nếu khong tuong se lech nua be day.

## Luoi truc nha pho Viet Nam

Nha pho mat tien 5m thuong co:

- Hai hang cot sat hai tuong bien, cach nhau 4.78m (5.0 tru hai nua tuong 0.22)
- Buoc cot theo chieu sau 3.5m den 5m
- Cot 220x220 cho nha 3 tang, 220x300 tu 4 tang tro len

## Kich thuoc thuong dung

| Cau kien | Kich thuoc |
|---|---|
| Tuong bao | 0.22 |
| Tuong ngan | 0.11 |
| San | 0.10 den 0.12 |
| Dam chinh | 0.22 x 0.35 |
| Dam phu | 0.22 x 0.30 |
| Cua di chinh | 1.0 x 2.4 |
| Cua di phong | 0.9 x 2.2 |
| Cua di WC | 0.75 x 2.1 |
| Cua so | 1.2 x 1.5, be cua 0.9 |
| Bac thang | cao 0.165 den 0.180, rong 0.26 den 0.30 |

## Cau thang

Tich `so_bac x cao_bac` phai bang chieu cao tang. Vi du tang cao 3.15m:
18 bac moi bac 0.175m. Neu khong khop, thang se hut hoac vuot qua san tren.

Cong thuc kiem tra do thoai: `2 x cao_bac + rong_bac` nen nam trong khoang
0.60 den 0.65 met. Voi 0.175 va 0.27 thi duoc 0.615, dat.

Thang dung ra la ban nghieng day 0.12 cong cac bac nam tren, giong cau tao
that. Nho vay khoi luong betong boc ra dung, khoang 1.1 den 1.3 m3 moi ve
thang nha pho.

## Kiem tra lai bang mat

Sau moi buoc dung dang ke, goi `nhin` va thuc su nhin anh. Cac loi hay gap
ma chi nhin anh moi thay:

- Khoi bay lo lung vi nhap sai cao do
- Tuong xuyen qua nhau o goc
- Cau thang dam vao san tang tren
- Mai khong phu het tuong
- Ty le cua so qua to so voi tuong

Dung tin rang hinh da dung chi vi lenh chay khong bao loi.
