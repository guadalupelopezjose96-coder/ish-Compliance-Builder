#!/usr/bin/env python3
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

installed_db = Path("/lib/apk/db/installed")
out_dir = Path("/usr/share/licenses/compliance")
out_dir.mkdir(parents=True, exist_ok=True)

components = []
txt_lines = []

if installed_db.exists():
    raw_blocks = installed_db.read_text(encoding="utf-8", errors="replace").strip().split("\n\n")
    for block in raw_blocks:
        pkg = {}
        for line in block.splitlines():
            if len(line) > 2 and line[1] == ":":
                pkg[line[0]] = line[2:].strip()
        if "P" in pkg and "V" in pkg:
            name, ver = pkg["P"], pkg["V"]
            lic = pkg.get("L", "UNKNOWN")
            url = pkg.get("U", "")
            arch = pkg.get("A", "x86")
            txt_lines.append(f"{name}-{ver} | License: {lic} | Arch: {arch} | URL: {url}")
            components.append({
                "type": "library",
                "name": name,
                "version": ver,
                "licenses": [{"license": {"name": lic}}],
                "purl": f"pkg:apk/alpine/{name}@{ver}?arch={arch}"
            })

(out_dir / "INSTALLED_PACKAGES_AND_LICENSES.txt").write_text("\n".join(sorted(txt_lines)) + "\n", encoding="utf-8")

sbom = {
    "bomFormat": "CycloneDX",
    "specVersion": "1.5",
    "version": 1,
    "metadata": {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "component": {"type": "operating-system", "name": "iSH-Alpine-Immutable-RootFS", "version": "3.20"}
    },
    "components": components
}
sbom_bytes = json.dumps(sbom, indent=2).encode("utf-8")
(out_dir / "SBOM_CycloneDX.json").write_bytes(sbom_bytes)
print(f"[OK] SBOM CycloneDX generado ({len(components)} paquetes auditados).")
print(f"[OK] SHA-256 SBOM: {hashlib.sha256(sbom_bytes).hexdigest()}")
