# Huong dan vat lieu va anh sang

## Vat lieu co san

Goi `tao_vat_lieu` voi mot trong cac loai sau:

| Loai | Dung cho |
|---|---|
| `be_tong` | San, cot, dam, mai lo be tong |
| `gach` | Tuong gach khong trat |
| `tuong_son` | Tuong da trat va son, mau kem nhat |
| `kinh` | Cua so, vach kinh, lan can kinh |
| `go` | Cua di, san go, lam go |
| `thep` | Lan can, khung sat |
| `ngoi` | Mai ngoi |
| `gach_lat` | San lat gach |
| `da` | Op da, bac thang da |
| `nhom` | Khung cua nhom kinh |

Muon mau khac thi truyen them `mau` dang `[r, g, b]`, moi so tu 0 den 1.

## Gan vat lieu nhanh cho ca cong trinh

Gan theo loai cau kien thay vi tung object:

1. Goi `xem_canh` voi `chi_cua_addon=True` de lay danh sach kem `loai_cau_kien`.
2. Tao san cac vat lieu can dung.
3. Goi `gan_vat_lieu` cho tung object theo loai cua no.

Cach gan thong dung: tuong dung `tuong_son`, san va cot va dam dung `be_tong`,
mai dung `be_tong`, lan can dung `kinh`.

## Anh sang

Mot bo den toi thieu de nhin ro mo hinh gom **hai** thu:

```
tao_den(kieu="SUN", goc_do=[55, 0, 25], cong_suat=4.0)
anh_sang_moi_truong(cuong_do=1.2)
```

Thieu anh sang moi truong thi moi mat quay khoi huong nang deu den si, anh
render ra toi om du da co nang. Day la loi hay gap nhat khi anh render dau
tien ra khong nhin thay gi.

Goc xoay quyet dinh huong nang. Thanh phan thu ba la huong la ban, tinh
nguoc chieu kim dong ho tu truc X duong:

| Huong nang | goc_do thu ba |
|---|---|
| Dong | 0 |
| Bac | 90 |
| Tay | 180 |
| Nam | 270 |

Nha Viet Nam thuong lay nang chieu buoi chieu tu huong Tay, dat 180 den 225.

## Camera

Dat camera cach nha khoang 1.5 den 2 lan chieu rong mat tien, cao ngang
tam mat khoang 1.6m neu muon goc nhin nguoi di duong, hoac cao 8 den 15m
neu muon nhin bao quat.

```
tao_camera(vi_tri=[12, -12, 8], nhin_vao=[2.5, 7, 3], tieu_cu=35)
```

Tieu cu 35 cho goc rong, hop voi nha pho chat hep. Tieu cu 50 gan voi mat
nguoi hon nhung phai lui xa moi lay het nha.

## Render

`nhin` chup nhanh khung nhin, dung de kiem tra trong luc dung.
`render_anh` cham hon nhung cho anh dep, dung khi da dung xong.

Engine nhanh la `BLENDER_EEVEE_NEXT` tren Blender 4.2 tro len. Ban cu hon
dung `BLENDER_EEVEE`. Neu nhap sai ten, thong bao loi se liet ke ten hop le.
