# Danh sach cong cu

30 cong cu, chia 9 nhom. Moi so do tinh bang **met**, moi goc tinh bang **do**.

Toa do theo quy uoc Blender: X sang phai, Y ra xa, Z len tren. Mat bang nam
tren mat phang XY, cao do la truc Z.

## 1. Ket noi va huong dan

### `kiem_tra_ket_noi()`

Kiem tra noi duoc toi Blender chua. Goi dau tien moi phien lam viec.

Tra ve phien ban Blender, phien ban addon, file dang mo, so doi tuong.

### `huong_dan(chu_de)`

Doc huong dan nghiep vu. Bo trong `chu_de` de xem danh sach.

| Chu de | Noi dung |
|---|---|
| `dung-nha` | Thu tu dung, cach tinh cao do, kich thuoc thong dung |
| `vat-lieu` | Bang vat lieu, cach dat den va camera |

## 2. Xem canh

### `xem_canh(chi_cua_addon=False, gioi_han=100)`

Liet ke doi tuong trong canh kem vi tri, kich thuoc, loai cau kien, vat lieu.

Dat `chi_cua_addon=True` de chi xem nhung thu bo cong cu nay dung ra.

### `xem_doi_tuong(ten)`

Chi tiet mot doi tuong: vi tri, goc xoay, ty le, kich thuoc, vat lieu,
modifier, va toan bo thuoc tinh `xd_` da gan luc dung.

## 3. Dung cau kien

### `dung_tuong(diem_dau, diem_cuoi, day=0.22, cao=3.0, cao_do=0.0, ten=None)`

Dung mot buc tuong thang.

| Tham so | Y nghia |
|---|---|
| `diem_dau`, `diem_cuoi` | `[x, y]` hai dau **truc tim** tuong, khong phai mep |
| `day` | Be day. Tuong bao 0.22, tuong ngan 0.11 |
| `cao` | Chieu cao tuong, bang chieu cao tang tru chieu cao dam |
| `cao_do` | Cao do chan tuong |

Tra ve ten object, chieu dai, dien tich mat, the tich.

Luu ten object lai neu sau nay con khoet cua tren buc tuong do.

### `dung_san(dinh, day=0.10, cao_do=0.0, ten=None)`

Dung tam san betong tu da giac mat bang.

`dinh` la danh sach `[x, y]` theo thu tu vong quanh, it nhat 3 diem.

`cao_do` la cao do **mat tren** cua san. Tam san do xuong duoi con so nay,
dung nhu cach thi cong that.

### `dung_cot(vi_tri, rong=0.22, sau=0.22, cao=3.0, cao_do=0.0, ten=None)`

Dung cot chu nhat. `vi_tri` la `[x, y]` tam cot.

### `dung_dam(diem_dau, diem_cuoi, rong=0.22, cao=0.35, cao_do_day=2.65, ten=None)`

Dung dam ngang. `cao_do_day` la cao do **day dam**, khong phai dinh dam.

### `khoet_cua(ten_tuong, khoang_cach, rong, cao, be_cua=0.0)`

Khoet lo cua di hoac cua so tren tuong da dung.

| Tham so | Y nghia |
|---|---|
| `ten_tuong` | Ten object tuong, lay tu ket qua `dung_tuong` |
| `khoang_cach` | Tu diem dau cua tuong den **mep trai** lo cua |
| `be_cua` | Cao do day lo so voi chan tuong. Cua di 0, cua so thuong 0.9 |

Chi khoet duoc tren tuong do chinh bo cong cu nay dung, vi phai doc lai truc
tim da luu trong thuoc tinh `xd_diem_dau`.

### `dung_cau_thang(diem_dau, huong_do=0, so_bac=18, cao_bac=0.175, rong_bac=0.27, rong_thang=1.0, cao_do=0.0, day_ban=0.12, ten=None)`

Dung cau thang betong mot ve: ban nghieng cong cac bac nam tren.

`huong_do` la huong di len: 0 theo truc X duong, 90 theo truc Y duong.

Tich `so_bac x cao_bac` phai bang chieu cao tang. Tang cao 3.15m thi 18 bac
moi bac 0.175m.

`day_ban` la be day ban thang, do vuong goc voi mat nghieng.

Thang duoc dung dung cau tao that chu khong dap mot khoi dac. Khac biet nay
quan trong khi boc khoi luong: thang 18 bac rong 1m dung dung cau tao ra
1.12 m3 betong, con dap khoi dac ra khoang 10 m3, sai gan 9 lan.

### `dung_mai(dinh, kieu="bang", day=0.10, cao_do=0.0, do_doc=0.02, vuon=0.0, ten=None)`

Dung mai betong.

| Tham so | Y nghia |
|---|---|
| `kieu` | `bang` cho mai bang co doc thoat nuoc, `doc` cho mai mot doc |
| `do_doc` | Ty le doc, 0.02 la 2 phan tram |
| `vuon` | Phan mai dua ra ngoai mep tuong |

## 4. Dung ca cong trinh mot luot

### `dung_tu_mo_ta(mo_ta)`

Cach nen dung khi dung nguyen mot ngoi nha. Nhanh hon nhieu so voi goi tung
tool, vi chi mot luot trao doi thay vi hang chuc luot.

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

Truong `tuong` trong moi muc cua la **so thu tu** buc tuong trong danh sach
`tuong` cua chinh tang do, dem tu 0.

Tra ve so luong da dung tung loai, danh sach ten tuong theo tang, va danh
sach loi neu co. Mot cau kien loi khong lam dung ca me.

Co file mau o [examples/nha-pho-5x20m.json](../examples/nha-pho-5x20m.json).

## 5. Doc ban ve DXF

### `doc_layer_dxf(duong_dan)`

Liet ke layer trong file DXF kem so luong doi tuong tung loai.

**Goi tool nay truoc** khi dung `dung_nha_tu_dxf`, vi moi don vi thiet ke dat
ten layer mot kieu.

### `doc_mat_bang_dxf(duong_dan, layer_tuong, layer_cot, vung, ty_le=0.001, goc)`

Doc mat bang va tra ve danh sach tuong, cot. Chua dung gi trong Blender,
dung de kiem tra so lieu truoc.

| Tham so | Y nghia |
|---|---|
| `layer_tuong` | Danh sach ten layer chua tuong. Mac dinh `A-WALL-220`, `A-WALL-110`, `A-WALL`, `TUONG` |
| `layer_cot` | Mac dinh `A-COL`, `COT`, `A-COLUMN` |
| `vung` | `[x0, y0, x1, y1]` theo don vi ban ve, de lay rieng mot mat bang |
| `ty_le` | 0.001 cho ban ve milimet, 1.0 cho ban ve met |
| `goc` | `[x, y]` diem se duoc dua ve goc toa do |

Tham so `vung` can khi ho so xep nhieu mat bang canh nhau tren cung mot
khong gian, kieu tang 1 tang 2 tang 3 nam ngang hang.

### `dung_nha_tu_dxf(duong_dan, cao_tuong=3.0, cao_do=0.0, ...)`

Doc mat bang DXF roi dung thang tuong va cot trong Blender. Nhan cung cac
tham so nhu tool tren, them `cao_tuong`, `cao_do`, `dung_cot_luon`.

## 6. Vat lieu

### `tao_vat_lieu(ten, loai="be_tong", mau=None)`

| Loai | Dung cho |
|---|---|
| `be_tong` | San, cot, dam, mai lo betong |
| `gach` | Tuong gach khong trat |
| `tuong_son` | Tuong da trat va son |
| `kinh` | Cua so, vach kinh, lan can kinh |
| `go` | Cua di, san go |
| `thep` | Lan can, khung sat |
| `ngoi` | Mai ngoi |
| `gach_lat` | San lat gach |
| `da` | Op da, bac thang da |
| `nhom` | Khung cua nhom kinh |

Truyen `mau` dang `[r, g, b]`, moi so tu 0 den 1, de doi mau rieng.

### `gan_vat_lieu(ten_doi_tuong, ten_vat_lieu)`

Gan vat lieu da tao len mot object.

## 7. Sua, xoa, nhan ban

### `sua_doi_tuong(ten, vi_tri, xoay_do, ty_le, ten_moi)`

Doi vi tri, goc xoay, ty le hoac ten. Tham so nao bo trong thi giu nguyen.

### `xoa_doi_tuong(ten)`

### `nhan_ban(ten, lech, ten_moi=None)`

`lech` la `[dx, dy, dz]`. Tien de tao cac tang giong nhau: dung tang 1 xong
thi nhan ban len cao do tang 2.

### `xoa_toan_bo(chi_cua_addon=True)`

Mac dinh chi xoa trong collection `MCP_XayDung`, khong dung toi vat nguoi
dung tu lam. Dat `False` de xoa sach ca canh, can nhac ky.

## 8. Nhin, render, xuat

### `tao_den(kieu="SUN", vi_tri, cong_suat=5.0, goc_do, ten)`

`kieu`: `SUN`, `POINT`, `SPOT`, `AREA`.

### `anh_sang_moi_truong(cuong_do=1.0, mau=None)`

Dat anh sang moi truong, dong vai bau troi hat sang vao cong trinh.

Chi co mot nguon SUN thi moi mat quay khoi huong nang deu den si, nhin khong
ra hinh khoi. **Goi tool nay cung voi `tao_den`**, neu khong anh render ra
toi om.

| `cuong_do` | Dung cho |
|---|---|
| 0.5 | Troi chieu nang gat, bong do dam |
| 1.0 | Troi quang |
| 2.0 | Troi nhieu may, hoac muon nhin ro moi chi tiet |

### `tao_camera(vi_tri, nhin_vao, tieu_cu=35.0, dat_lam_chinh=True, ten)`

Dat camera va tu huong no vao mot diem.

### `cai_dat_render(rong=1920, cao=1080, engine=None, mau_anh=None)`

Engine thuong dung: `BLENDER_EEVEE_NEXT` cho nhanh, `CYCLES` cho dep. Ten
engine khac nhau giua cac ban Blender; nhap sai thi thong bao loi se liet ke
ten hop le.

### `nhin(kich_thuoc_toi_da=1200)`

Chup khung nhin, tra ve anh. **Goi sau moi buoc dung dang ke.** Nhieu loi chi
nhin anh moi phat hien: khoi bay lo lung, tuong xuyen nhau, sai ty le.

### `render_anh(duong_dan=None, kich_thuoc_toi_da=1600)`

Render bang engine dang chon. Cham hon `nhin` nhung cho anh dep.

### `xuat_file(duong_dan, dinh_dang="glb", chi_cua_addon=False)`

`dinh_dang`: `glb`, `fbx`, `obj`, `stl`.

glb hop de xem tren web va dien thoai, fbx hop de dua sang phan mem khac.

### `boc_khoi_luong()`

Do the tich tung cau kien tu hinh hoc that, gom theo loai. Cac lo cua da
khoet duoc tru tu dong.

Tra ve tung nhom cau kien kem so luong, the tich, dien tich; va tong betong,
tong khoi xay.

## 9. Nang cao

### `chay_python(code)`

Chay Python bat ky trong Blender, dung khi khong co tool san phu hop.

Gan gia tri vao bien ten `ket_qua` de nhan lai gia tri do.

Code duoc soat truoc de chan xoa file, chay lenh he thong, va cac thao tac
lam mat ban ve. Chi tiet o [phat-trien.md](phat-trien.md).

Khi viet code chay tren may nguoi khac:

- Tim node shader theo thuoc tinh `type`, khong theo ten, vi ten doi theo
  ngon ngu giao dien
- Khong viet cung ten enum, doc danh sach hop le tu `bl_rna` truoc
