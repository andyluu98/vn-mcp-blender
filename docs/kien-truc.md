# Kien truc

## Vi sao phai chia hai phan

Blender khong noi chuyen MCP duoc. No la phan mem do hoa, chi chay Python
ben trong chinh no. MCP thi can mot chuong trinh doc ghi qua stdio theo
chuan rieng.

Nen bo nay chia lam hai:

```
          stdio (MCP)              socket TCP 9877
Claude <----------------> MCP server <-------------> Addon trong Blender
                          (tien trinh      JSON        (thu vien bpy)
                           rieng)
```

| Phan | Chay o dau | Lam gi |
|---|---|---|
| MCP server | Tien trinh rieng, Claude tu khoi dong | Khai bao 30 cong cu, doc file DXF, soat code |
| Addon | Ben trong Blender | Dung hinh, do khoi luong, chup anh |

Phan chia nay co mot he qua can nho: **MCP server khong dung duoc hinh nao
neu Blender chua bat ket noi**. Moi thao tac hinh hoc deu phai qua addon.

## Giao thuc

Moi ban tin gom hai phan:

```
[4 byte do dai, big-endian] [than ban tin, JSON UTF-8]
```

Yeu cau tu server sang addon:

```json
{"type": "create_wall", "params": {"diem_dau": [0, 0], "diem_cuoi": [5, 0]}}
```

Tra loi tu addon, mot trong hai dang:

```json
{"status": "success", "result": {"ten": "Tuong_220", "dai": 5.0}}
```

```json
{"status": "error", "message": "Khong co tuong ten X"}
```

### Vi sao ghi do dai len dau

Socket TCP khong giu ranh gioi ban tin. Gui mot cuc 10KB thi ben nhan co the
nhan thanh ba lan, hoac hai ban tin lien tiep dinh lam mot.

Mot so bo MCP Blender khac giai quyet bang cach doc them cho den khi JSON
parse duoc. Cach do chay duoc nhung mong manh: neu ban tin bi cat o dung cho
ma phan dau tinh co van la JSON hop le, no se cat nham.

Ghi do dai len dau thi khong phai doan. Ben nhan biet chinh xac can doc bao
nhieu byte. Test `test_ghep_dung_khi_du_lieu_ve_tung_manh` kiem chung dieu nay
bang cach gui tung byte mot.

## Addon chay tren luong chinh

Thu vien bpy khong an toan khi goi tu luong phu. Goi bpy tu thread khac co
the lam Blender sap ma khong bao gi.

Nen addon khong tao thread. No dang ky mot ham chay dinh ky qua
`bpy.app.timers`, cu 0.05 giay mot lan:

```python
def _tick(self):
    try:
        client, _ = self.sock.accept()   # socket dat che do khong chan
    except BlockingIOError:
        return TICK_SECONDS              # chua ai goi, cho luot sau
    self._serve(client)                  # xu ly ngay tren luong chinh
    return TICK_SECONDS
```

Socket dat che do khong chan nen `accept()` tra ve ngay neu chua ai goi.
Khi co ket noi thi xu ly luon tren luong chinh, dung bpy thoai mai.

Doi lai, mot lenh nang se lam Blender dung hinh trong luc chay. Day la danh
doi co chu y: tha de Blender dung vai giay con hon lam no sap.

## Moi ket noi mot lenh

MCP server khong giu ket noi lau. Moi lenh mo mot socket moi roi dong lai.

Giu ket noi lau se chet khi nguoi dung tat mo Blender, va phai viet them
logic noi lai. Chi phi mo socket noi bo chi vai phan nghin giay, khong dang
de danh doi lay su phuc tap do.

## Collection rieng

Moi thu addon dung ra deu nam trong collection ten `MCP_XayDung`. Nho vay:

- Nguoi dung xoa sach ket qua bang mot thao tac, khong dung toi vat tu lam
- Tool `xoa_toan_bo` mac dinh chi xoa trong collection nay
- Tool `boc_khoi_luong` chi dem cau kien trong day

## Nhan cau kien

Moi object addon tao ra deu duoc gan them thuoc tinh tuy bien bat dau bang `xd_`:

| Thuoc tinh | Y nghia |
|---|---|
| `xd_loai` | tuong, san, cot, dam, cau_thang, mai |
| `xd_day`, `xd_cao`, `xd_dai` | So do danh nghia luc dung |
| `xd_diem_dau`, `xd_diem_cuoi` | Truc tim tuong, dung de khoet cua sau nay |
| `xd_the_tich`, `xd_dien_tich` | So do tinh san |

Nho cac nhan nay ma `boc_khoi_luong` gom duoc theo loai cau kien, va
`khoet_cua` biet tuong nam o dau de dat khoi cat cho dung.

## Boc khoi luong do tu hinh that

`boc_khoi_luong` khong cong lai cac so do danh nghia. No do the tich thuc cua
tung khoi bang bmesh:

```python
bm.from_mesh(obj.data)
bm.transform(obj.matrix_world)
volume = abs(bm.calc_volume(signed=True))
```

Nho vay cac lo cua da khoet duoc tru tu dong. Tuong 5m x 3m day 0.22 duoc
3.300 m3; khoet cua 1.0 x 2.2 thi con dung 2.816 m3. Con so nay duoc kiem
chung trong `scripts/tu-kiem-tra.py`.

## Doc DXF o phia server

Viec doc file DXF lam o MCP server, khong lam trong addon. Ly do: thu vien
ezdxf khong co san trong Python cua Blender, ma bat nguoi dung cai them vao
Blender thi phien.

Server doc DXF, rut ra truc tim tuong va vi tri cot, roi gui sang addon duoi
dang cac lenh dung hinh binh thuong.

### Cach nhan ra mot buc tuong tren ban ve

Ban ve kien truc ve tuong bang polyline kin, hinh chu nhat rat det. Thuat toan
trong `dxf.py`:

1. Tim canh dai nhat cua hinh, lay lam huong
2. Chieu moi dinh len huong do va len huong vuong goc
3. Pham vi theo huong doc la chieu dai, theo huong ngang la be day
4. Neu chieu dai khong gap be day it nhat 2.5 lan thi bo qua, khong phai tuong
5. Truc tim nam giua hai canh dai

Cach nay doc duoc ca tuong ve xien, khong chi tuong thang theo truc. Nguong
2.5 lan loc bo cac hinh vuong nho nhu ky hieu hay chu thich nam nham tren
layer tuong.

## Cay thu muc

```
src/blender_mcp_xaydung/
  __init__.py       Phien ban, cong mac dinh
  server.py         Khai bao 29 tool MCP
  connection.py     Client socket, dong goi ban tin
  dxf.py            Doc ban ve DXF
  safe_mode.py      Soat code Python truoc khi chay
  addon_manager.py  Tim Blender va chep addon vao
  cli.py            Dong lenh
  guides/           Huong dan nghiep vu, tool huong_dan doc tu day
  bundled/addon.py  Addon chay trong Blender
```
