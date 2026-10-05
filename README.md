# MCP Xay Dung cho Blender

MCP server giup AI dung mo hinh nha 3D trong Blender tu du lieu kien truc,
doc duoc mat bang DXF tu AutoCAD va boc khoi luong tu chinh mo hinh.

Viet cho ho so nha o Viet Nam: tuong 220 va 110, cot betong, dam, san, cau
thang, mai bang. Moi so do tinh bang met.

## Lam duoc gi

| Nhom | Noi dung |
|---|---|
| Dung cau kien | Tuong, san, cot, dam, cau thang, mai, khoet lo cua |
| Doc ban ve | Nhap mat bang DXF, rut truc tim tuong va vi tri cot |
| Vat lieu | 10 vat lieu xay dung dung san: betong, gach, kinh, go, thep, ngoi |
| Nhin va render | Chup khung nhin de kiem tra, render anh phoi canh |
| Xuat | glb, fbx, obj, stl |
| Boc khoi luong | Do the tich tu hinh hoc that, da tru lo cua |

Tong cong 30 cong cu. Danh sach day du o [docs/cong-cu.md](docs/cong-cu.md).

## Cai dat

Can hai thu: MCP server va addon trong Blender. Xem huong dan tung buoc o
[docs/cai-dat.md](docs/cai-dat.md), hoac lam nhanh nhu duoi.

### Yeu cau

- Blender 3.0 tro len
- Python 3.10 tro len
- Claude Code, Claude Desktop, hoac bat ky ung dung nao noi duoc MCP

### Buoc 1: cai goi

```bash
pip install blender-mcp-xaydung
```

Hoac cai tu ma nguon:

```bash
git clone https://github.com/ck15/blender-mcp-xaydung
cd blender-mcp-xaydung
pip install -e .
```

### Buoc 2: cai addon vao Blender

```bash
blender-mcp-xaydung install-addon
```

Lenh nay tu tim Blender tren may va chep addon vao. Sau do trong Blender:

1. `Edit > Preferences > Add-ons`
2. Tim **MCP Xay Dung**, tich vao o ben trai de bat
3. Trong khung nhin 3D, bam phim **N** de mo thanh ben
4. Chon tab **MCP Xay Dung**, bam **Bat ket noi**

### Buoc 3: khai bao voi Claude

Them vao file cau hinh MCP:

```json
{
  "mcpServers": {
    "blender-xaydung": {
      "command": "blender-mcp-xaydung"
    }
  }
}
```

File cau hinh nam o:

| Ung dung | Duong dan |
|---|---|
| Claude Code | `~/.claude.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |

Khoi dong lai Claude, roi thu bao: "kiem tra ket noi Blender".

### Kiem tra nhanh khong can Claude

```bash
blender-mcp-xaydung check
```

## Dung thu

Mo Blender, bat addon, roi bao Claude:

> Dung cho toi nha pho 5m x 14m, 1 tang, tuong bao 220 cao 3.1m, san day 100,
> 4 cot 220x220 o bon goc. Xong thi cho toi xem anh.

Hoac dung tu ban ve co san:

> Doc file F:/ban-ve/mat-bang.dxf xem co layer gi, roi dung tuong len 3D.

## Kien truc

Blender khong noi chuyen MCP truc tiep duoc, nen bo nay chia hai nua:

```
Claude  <--stdio/MCP-->  MCP server  <--socket TCP 9877-->  Addon trong Blender
```

MCP server khai bao cong cu va doc file DXF. Addon lam moi viec dung hinh
bang thu vien bpy. Chi tiet o [docs/kien-truc.md](docs/kien-truc.md).

Cong mac dinh la **9877**, chon khac 9876 de khong dam voi addon blender-mcp
pho bien neu anh dang dung ca hai.

## Phat trien

```bash
pip install -e ".[dev]"
pytest
```

37 test chay duoc ma khong can mo Blender. Rieng phan hinh hoc co script tu
kiem tra chay trong Blender that:

```bash
blender --background --python scripts/tu-kiem-tra.py
```

Cach them cong cu moi: [docs/phat-trien.md](docs/phat-trien.md).

## An toan

Cong cu `chay_python` cho phep chay Python bat ky trong Blender. Code duoc
soat truoc de chan xoa file, chay lenh he thong, va cac thao tac lam mat ban
ve dang mo. Xem `src/blender_mcp_xaydung/safe_mode.py`.

Bo soat nay chan loi ro rang, khong phai tuong lua. Van nen doc code truoc
khi cho chay tren ban ve quan trong, va luu file truoc khi lam viec lon.

Bo cong cu nay **khong gui du lieu di dau**. Khong co telemetry.

## Giay phep

MIT. Xem [LICENSE](LICENSE).

Du an doc lap, khong lien quan den Blender Foundation.
