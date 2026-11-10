#!/usr/bin/env python3
import sys
import struct
import sqlite3
import hashlib
from pathlib import Path

bundle = Path(sys.argv[1]).resolve()
db_path = bundle / "meta.db"
sha_path = bundle / "meta.db.sha256"

actual_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()
expected_sha = sha_path.read_text().strip()

assert actual_sha == expected_sha, "Fallo de integridad SHA-256"
print(f"[VERIFICADO] Firma SHA-256 autentica: {actual_sha}")

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()
cur.execute("SELECT p.inode, p.path, s.stat FROM paths p JOIN stats s ON p.inode = s.inode;")
print("\nInodo | Modo Octal | UID:GID | Ruta en fakefs")
print("-" * 55)
for inode, path_blob, stat_blob in cur.fetchall():
    mode, uid, gid, rdev = struct.unpack("<IIII", stat_blob)
    ruta = path_blob.decode("utf-8") or "/"
    print(f"{inode:5d} | {oct(mode):10s} | {uid:3d}:{gid:<3d} | {ruta}")
conn.close()
