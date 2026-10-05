# Xu ly loi

## Khong noi duoc toi Blender

Thong bao day du:

> Khong noi duoc toi Blender o localhost:9877. Mo Blender, vao thanh ben
> View3D (phim N), tab 'MCP Xay Dung', bam 'Bat ket noi'.

Kiem tra lan luot:

### 1. Blender da mo chua

Addon chi chay khi Blender dang mo. Dong Blender la mat ket noi.

### 2. Addon da bat chua

`Edit > Preferences > Add-ons`, go "MCP" vao o tim, xem dong **MCP Xay Dung**
da duoc tich chua.

Neu khong thay dong nao, addon chua duoc cai. Chay lai:

```bash
blender-mcp-xaydung install-addon
```

Roi khoi dong lai Blender.

### 3. Da bam "Bat ket noi" chua

Bat addon trong Preferences **chua du**. Con phai bam nut Bat ket noi:

1. Dua chuot vao khung nhin 3D, bam phim **N**
2. Chon tab **MCP Xay Dung**
3. Bam **Bat ket noi**
4. Phai thay dong chu "Dang chay o cong 9877" kem dau tich

Day la buoc hay bi quen nhat.

### 4. Cong co bi chiem khong

Neu bam Bat ket noi ma hien loi do, co chuong trinh khac dang giu cong 9877.

Xem ai dang giu cong:

```bash
# Windows
netstat -ano | findstr 9877

# macOS, Linux
lsof -i :9877
```

Doi cong trong o "Cong" ngay tren nut Bat ket noi, roi sua lai cau hinh ben
MCP server cho khop.

### 5. Hai cua so Blender cung mo

Chi mot cua so giu duoc cong. Cua so thu hai bam Bat ket noi se bao loi.
Dong bot di con mot.

## Blender khong tra loi, bi treo

Thong bao:

> Blender khong tra loi lenh 'X' trong 120 giay.

Addon chay lenh ngay tren luong chinh cua Blender, nen mot lenh nang se lam
giao dien dung hinh. Day la thiet ke co chu y, doi lai la bpy chay an toan.

Lam gi:

1. Doi them. Lenh dung vai nghin cau kien that su ton thoi gian.
2. Mo cua so Console cua Blender de xem no dang lam gi:
   - Windows: `Window > Toggle System Console`
   - macOS, Linux: khoi dong Blender tu terminal se thay log
3. Neu treo han, tat Blender roi mo lai. Nho luu file truoc khi lam viec lon.

## Code bi chan

Thong bao:

> Code bi chan vi cac ly do sau: dong 3: nhap module bi chan 'subprocess'

Tool `chay_python` soat code truoc khi chay, chan cac thao tac co the xoa
file hoac lam mat ban ve.

Neu doan code that su an toan va anh can chay:

```bash
# Windows PowerShell
$env:BLENDER_MCP_UNSAFE = "1"

# macOS, Linux
export BLENDER_MCP_UNSAFE=1
```

Roi khoi dong lai MCP server (khoi dong lai Claude).

Can nhac ky truoc khi tat. Lop soat nay ton tai vi code chay trong Blender
co day du quyen cua anh tren may.

## Loi khi doc file DXF

### "Khong doc duoc file DXF"

- Kiem tra duong dan co dung khong. Tren Windows dung dau gach cheo xuoi
  hoac gach cheo nguoc nhan doi: `F:/ban-ve/a.dxf` hoac `F:\\ban-ve\\a.dxf`
- File phai la `.dxf`. Thu vien ezdxf khong doc duoc `.dwg`. Trong AutoCAD
  dung `Save As` chon dinh dang DXF.

### Doc duoc nhung khong ra tuong nao

Goi `doc_layer_dxf` xem ban ve dat ten layer gi, roi truyen dung ten vao
`layer_tuong`:

```
doc_mat_bang_dxf(duong_dan="...", layer_tuong=["TUONG-220", "TUONG-110"])
```

### Tuong ra sai kich thuoc, to gap nghin lan

Ban ve dung don vi met chu khong phai milimet. Dat `ty_le=1.0`.

Nguoc lai, neu nha chi be bang hat gao thi ban ve dung met ma anh de
`ty_le=0.001`.

### Doc duoc ca 5 mat bang chong len nhau

Ho so Viet Nam hay xep nhieu mat bang canh nhau tren cung mot khong gian.
Dung `vung` de lay rieng mot cai:

```
doc_mat_bang_dxf(duong_dan="...", vung=[0, 0, 5000, 20000])
```

Toa do trong `vung` tinh theo don vi ban ve (milimet), khong phai met.

Dung `goc` de dua mat bang do ve goc toa do:

```
doc_mat_bang_dxf(duong_dan="...", vung=[9000, 0, 14000, 20000], goc=[9000, 0])
```

## Loi hinh hoc

### Tuong lech nua be day

`dung_tuong` nhan hai diem tren **truc tim**, khong phai mep tuong. Neu ban
ve cua anh ghi theo mep, phai cong tru nua be day truoc khi nhap.

### Tuong bay lo lung

Kiem tra `cao_do`. Day la cao do chan tuong, khong phai cao do san tang.
Tuong tang 2 co san o cao do 3.9 thi chan tuong cung o 3.9.

### Cau thang dam vao san tang tren

Tich `so_bac x cao_bac` phai dung bang chieu cao tang. Tang cao 3.6m:
- 20 bac x 0.180 = 3.60, dat
- 18 bac x 0.175 = 3.15, hut 0.45m

### Khoet cua khong an gi

- Ten tuong phai lay tu ket qua tra ve cua `dung_tuong`, khong tu dat
- Chi khoet duoc tren tuong do chinh bo nay dung ra
- `khoang_cach` tinh tu diem dau cua tuong. Neu vuot qua chieu dai tuong thi
  khoi cat nam ngoai, khong cat vao dau

### Nhin anh thay trong rong

Chua co den. Goi `tao_den(kieu="SUN")` truoc.

Hoac chua co camera, hoac camera huong ra cho khac. Goi `tao_camera` voi
`nhin_vao` tro vao giua ngoi nha.

## Loi khi xuat file

### "Thu muc khong ton tai"

Tao thu muc truoc. MCP server khong tu tao thu muc, de tranh ghi nham cho.

### Xuat obj hoac stl bao khong co lenh

Ten lenh xuat doi giua cac ban Blender. Bo nay dung `bpy.ops.wm.obj_export`
va `bpy.ops.wm.stl_export`, co tu Blender 3.3 tro len. Ban cu hon thi xuat
`glb` hoac `fbx`.

## Cach lay them thong tin

Mo Console cua Blender, moi loi trong addon deu in day du vet loi o do:

- Windows: `Window > Toggle System Console`
- macOS, Linux: khoi dong Blender tu terminal

Kiem tra nhanh ca duong truyen, khong can Claude:

```bash
blender-mcp-xaydung check
```

Kiem tra phan hinh hoc, khong can mo giao dien Blender:

```bash
blender --background --python scripts/tu-kiem-tra.py
```
