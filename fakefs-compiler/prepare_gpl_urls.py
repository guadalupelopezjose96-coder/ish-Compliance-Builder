#!/usr/bin/env python3
import json
from pathlib import Path

src_dir = Path("/root/ish-Compliance-Builder/gpl-source-archive")
manifest = json.loads((src_dir / "GPL_CORRESPONDING_SOURCE_MANIFEST.json").read_text())

lines = []
for origin, info in manifest.items():
    ver = info["version"]
    commit = info["commit"]
    pkg_dir = src_dir / f"{origin}-{ver}"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    out_file = pkg_dir / "APKBUILD"
    url_main = f"https://raw.githubusercontent.com/alpinelinux/aports/{commit}/main/{origin}/APKBUILD"
    url_comm = f"https://raw.githubusercontent.com/alpinelinux/aports/{commit}/community/{origin}/APKBUILD"
    lines.append(f"{out_file}|{url_main}|{url_comm}|{origin}|{ver}|{info['license']}|{commit}|{info['upstream_url']}")

(src_dir / "download_queue.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"[OK] Cola preparada para {len(lines)} paquetes GPL/LGPL.")
