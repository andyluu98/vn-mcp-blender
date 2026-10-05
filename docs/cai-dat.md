# Huong dan cai dat chi tiet

Tai lieu nay viet cho nguoi chua tung cai MCP bao gio. Lam tung buoc, moi
buoc deu co cach kiem tra da dat chua truoc khi sang buoc sau.

## Hieu truoc khi cai

Anh se cai **hai** thu, khong phai mot:

1. **MCP server**: mot chuong trinh Python. Claude tu khoi dong no khi can.
2. **Addon**: mot file Python nap vao trong Blender.

Hai thu nay noi chuyen voi nhau qua cong 9877 tren chinh may anh.

Vi nhu goi dien cho nguoi trong phong kin: MCP server la nguoi truc tong dai,
addon la nguoi cam may ben trong. Thieu mot ben la khong noi duoc.

## Buoc 0: kiem tra may da san sang

```bash
python --version
```

Phai tu 3.10 tro len. Neu chua co Python, tai o python.org, nho tich o
"Add Python to PATH" khi cai tren Windows.

Blender phai tu ban 3.0 tro len. Mo Blender, vao `Help > About Blender` de xem.

## Buoc 1: cai goi Python

### Cach a: cai tu PyPI

```bash
pip install blender-mcp-xaydung
```

### Cach b: cai tu ma nguon

```bash
git clone https://github.com/ck15/blender-mcp-xaydung
cd blender-mcp-xaydung
pip install -e .
```

### Kiem tra

```bash
blender-mcp-xaydung --version
```

Ra so phien ban la dat. Neu bao "command not found", thu:

```bash
python -m blender_mcp_xaydung.cli --version
```

Neu cach nay chay duoc thi thu muc script cua Python chua nam trong PATH.
Khong sao, o buoc 3 anh khai bao bang `python -m` thay vi ten lenh.

## Buoc 2: cai addon vao Blender

### Cach a: de lenh tu lam

```bash
blender-mcp-xaydung install-addon
```

Lenh nay tim moi ban Blender tren may roi chep addon vao. No in ra duong dan
da chep.

### Cach b: cai tay

Lay duong dan file addon:

```bash
blender-mcp-xaydung addon-path
```

Roi trong Blender: `Edit > Preferences > Add-ons > Install...`, chon dung file do.

### Bat addon

1. Trong Blender mo `Edit > Preferences > Add-ons`
2. Go "MCP" vao o tim kiem
3. Thay dong **Interface: MCP Xay Dung**, tich vao o vuong ben trai
4. Dong cua so Preferences

### Bat ket noi

1. Dua chuot vao khung nhin 3D, bam phim **N**. Mot thanh doc hien ra ben phai.
2. Trong thanh do co cac tab doc. Chon tab **MCP Xay Dung**.
3. Bam nut **Bat ket noi**.
4. Dong chu doi thanh "Dang chay o cong 9877" kem dau tich.

### Kiem tra

Mo mot cua so dong lenh khac, giu Blender dang mo:

```bash
blender-mcp-xaydung check
```

Phai in ra thong tin Blender. Neu bao khong noi duoc, xem [xu-ly-loi.md](xu-ly-loi.md).

## Buoc 3: khai bao voi Claude

### Claude Code

Mo file `~/.claude.json` (tren Windows la `C:\Users\<ten>\.claude.json`),
tim muc `mcpServers`, them vao:

```json
{
  "mcpServers": {
    "blender-xaydung": {
      "type": "stdio",
      "command": "blender-mcp-xaydung",
      "args": []
    }
  }
}
```

Tren Windows, neu ten lenh khong chay duoc thi dung:

```json
{
  "mcpServers": {
    "blender-xaydung": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "blender_mcp_xaydung.cli"]
    }
  }
}
```

### Claude Desktop

File cau hinh:

| He dieu hanh | Duong dan |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Noi dung giong Claude Code o tren.

### Kiem tra

Khoi dong lai Claude, roi go:

> kiem tra ket noi Blender

Claude phai tra ve phien ban Blender va so doi tuong dang co.

## Thu tu khoi dong hang ngay

Moi lan lam viec, lam theo thu tu nay:

1. Mo Blender truoc
2. Bam **Bat ket noi** trong tab MCP Xay Dung
3. Mo Claude

Neu mo Claude truoc roi moi mo Blender van duoc, chi can bam Bat ket noi la
xong, khong phai khoi dong lai Claude.

## Dung chung voi addon blender-mcp khac

Bo nay dung cong **9877**, con addon `blender-mcp` pho bien dung 9876. Hai
cai chay song song duoc, khong dam nhau.

Neu muon doi cong, sua o ca hai noi:

- Trong Blender: o "Cong" ngay tren nut Bat ket noi
- Trong cau hinh MCP: them bien moi truong, hoac sua `DEFAULT_PORT` trong
  `src/blender_mcp_xaydung/__init__.py` neu cai tu ma nguon

## Go cai dat

```bash
pip uninstall blender-mcp-xaydung
```

Addon trong Blender go rieng: `Edit > Preferences > Add-ons`, tim MCP Xay Dung,
bam mui ten mo rong roi chon Remove.
