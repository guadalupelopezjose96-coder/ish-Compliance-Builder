#!/usr/bin/env python3
"""
Compilador de archivos tar.gz de Alpine Linux (i386) al formato nativo fakefs de iSH.
Genera meta.db (SQLite 3) y la jerarquia de datos para empaquetado inmutable.
"""

import os
import sys
import stat
import struct
import tarfile
import sqlite3
import hashlib
import shutil
from pathlib import Path


def encode_ish_stat(uid: int, gid: int, mode: int, rdev: int = 0) -> bytes:
    return struct.pack("<IIII", mode, uid, gid, rdev)


def build_fakefs(tar_gz_path: Path, output_fs_dir: Path) -> None:
    if not tar_gz_path.exists():
        raise FileNotFoundError(f"No se encontro el archivo RootFS: {tar_gz_path}")

    if output_fs_dir.exists():
        shutil.rmtree(output_fs_dir)

    data_dir = output_fs_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    db_path = output_fs_dir / "meta.db"

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("PRAGMA page_size = 4096;")
    cursor.execute("PRAGMA journal_mode = DELETE;")
    cursor.execute("PRAGMA synchronous = OFF;")

    cursor.execute("CREATE TABLE meta (id INTEGER UNIQUE DEFAULT 0, db_inode INTEGER);")
    cursor.execute("CREATE TABLE stats (inode INTEGER PRIMARY KEY, stat BLOB);")
    cursor.execute("CREATE TABLE paths (path BLOB PRIMARY KEY, inode INTEGER REFERENCES stats(inode));")
    cursor.execute("CREATE INDEX inode_to_path ON paths (inode, path);")

    root_stat = encode_ish_stat(uid=0, gid=0, mode=stat.S_IFDIR | 0o755, rdev=0)
    cursor.execute("INSERT INTO stats (stat) VALUES (?);", (root_stat,))
    root_inode = cursor.lastrowid
    cursor.execute("INSERT INTO paths (path, inode) VALUES (?, ?);", (b"", root_inode))

    hardlink_map: dict[str, int] = {}

    with tarfile.open(tar_gz_path, "r:gz") as tar:
        for member in tar.getmembers():
            clean_name = member.name.lstrip("./")
            if not clean_name:
                continue

            norm_path = "/" + clean_name.rstrip("/")
            path_bytes = norm_path.encode("utf-8")
            host_target = data_dir / clean_name

            if member.islnk():
                target_norm = "/" + member.linkname.lstrip("./").rstrip("/")
                if target_norm in hardlink_map:
                    linked_inode = hardlink_map[target_norm]
                    cursor.execute(
                        "INSERT OR REPLACE INTO paths (path, inode) VALUES (?, ?);",
                        (path_bytes, linked_inode),
                    )
                    target_host_file = data_dir / member.linkname.lstrip("./")
                    if target_host_file.exists():
                        host_target.parent.mkdir(parents=True, exist_ok=True)
                        os.link(target_host_file, host_target)
                continue

            perms = member.mode & 0o7777
            rdev = 0

            if member.isdir():
                mode = stat.S_IFDIR | perms
                host_target.mkdir(parents=True, exist_ok=True)
            elif member.issym():
                mode = stat.S_IFLNK | 0o777
                host_target.parent.mkdir(parents=True, exist_ok=True)
                with open(host_target, "wb") as f_sym:
                    f_sym.write(member.linkname.encode("utf-8"))
            elif member.ischr():
                mode = stat.S_IFCHR | perms
                rdev = (member.devmajor << 8) | member.devminor
                host_target.parent.mkdir(parents=True, exist_ok=True)
                host_target.touch()
            elif member.isblk():
                mode = stat.S_IFBLK | perms
                rdev = (member.devmajor << 8) | member.devminor
                host_target.parent.mkdir(parents=True, exist_ok=True)
                host_target.touch()
            elif member.isfifo():
                mode = stat.S_IFIFO | perms
                host_target.parent.mkdir(parents=True, exist_ok=True)
                host_target.touch()
            else:
                mode = stat.S_IFREG | perms
                host_target.parent.mkdir(parents=True, exist_ok=True)
                extracted = tar.extractfile(member)
                with open(host_target, "wb") as f_reg:
                    if extracted:
                        shutil.copyfileobj(extracted, f_reg)

            stat_blob = encode_ish_stat(
                uid=member.uid, gid=member.gid, mode=mode, rdev=rdev
            )
            cursor.execute("INSERT INTO stats (stat) VALUES (?);", (stat_blob,))
            inode_id = cursor.lastrowid
            cursor.execute(
                "INSERT OR REPLACE INTO paths (path, inode) VALUES (?, ?);",
                (path_bytes, inode_id),
            )
            hardlink_map[norm_path] = inode_id

    cursor.execute("INSERT INTO meta (id, db_inode) VALUES (0, 0);")
    conn.commit()
    cursor.execute("VACUUM;")
    conn.close()

    sha256_hash = hashlib.sha256(db_path.read_bytes()).hexdigest()
    (output_fs_dir / "meta.db.sha256").write_text(sha256_hash, encoding="utf-8")
    print(f"[OK] fakefs compilado en: {output_fs_dir}")
    print(f"[OK] SHA-256 (meta.db): {sha256_hash}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Uso: {sys.argv[0]} <ruta_rootfs.tar.gz> <directorio_salida_fakefs>")
        sys.exit(1)

    build_fakefs(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
