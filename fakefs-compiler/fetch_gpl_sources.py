#!/usr/bin/env python3
import json
import urllib.request
from pathlib import Path

db_file = Path("/lib/apk/db/installed")
src_dir = Path("/root/ish-Compliance-Builder/gpl-source-archive")
src_dir.mkdir(parents=True, exist_ok=True)

blocks = db_file.read_text(encoding="utf-8", errors="replace").strip().split("\n\n")
gpl_origins = {}

for b in blocks:
    meta = {}
    for line in b.splitlines():
        if len(line) > 2 and line[1] == ":":
            meta[line[0]] = line[2:].strip()
    lic = meta.get("L", "")
    if any(k in lic.upper() for k in ("GPL", "LGPL", "AGPL")):
        pkg = meta.get("P", "")
        ver = meta.get("V", "")
        origin = meta.get("o", pkg)
        commit = meta.get("c", "master")
        url = meta.get("U", "")
        gpl_origins[origin] = {
            "binary_package": pkg,
            "version": ver,
            "license": lic,
            "commit": commit,
            "upstream_url": url
        }

manifest_path = src_dir / "GPL_CORRESPONDING_SOURCE_MANIFEST.json"
manifest_path.write_text(json.dumps(gpl_origins, indent=2) + "\n", encoding="utf-8")
print(f"[AUDITADO] Paquetes origen con Copyleft (GPL/LGPL) detectados: {len(gpl_origins)}")

fetched = 0
for origin, info in list(gpl_origins.items()):
    pkg_dir = src_dir / f"{origin}-{info['version']}"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    for repo in ("main", "community"):
        raw_url = f"https://gitlab.alpinelinux.org/alpine/aports/-/raw/3.20-stable/{repo}/{origin}/APKBUILD"
        try:
            req = urllib.request.Request(raw_url, headers={"User-Agent": "iSH-GPL-Compliance/1.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status == 200:
                    (pkg_dir / "APKBUILD").write_bytes(resp.read())
                    fetched += 1
                    break
        except Exception:
            continue

print(f"[OK] Recetas de compilacion APKBUILD descargadas: {fetched}/{len(gpl_origins)}")
