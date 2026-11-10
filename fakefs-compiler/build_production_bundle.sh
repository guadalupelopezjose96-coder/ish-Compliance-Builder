#!/bin/sh
set -eu

OUT_DIR="/root/ish-Compliance-Builder/ImmutableRootFS.bundle"
SNAP_TAR="/root/ish-Compliance-Builder/alpine_system_snapshot.tar.gz"

echo "[1/3] Generando SBOM CycloneDX y Manifiesto GPLv2/SPDX..."
python3 /root/ish-Compliance-Builder/fakefs-compiler/generate_sbom_cyclonedx.py

echo "[2/3] Empaquetando binarios esenciales y licencias de Alpine i386..."
tar -czf "${SNAP_TAR}" \
    /bin /sbin /lib \
    /usr/share/licenses/compliance \
    /etc/passwd /etc/group /etc/profile /etc/os-release /etc/apk/repositories 2>/dev/null || true

echo "[3/3] Compilando base de datos fakefs inmutable de produccion..."
python3 /root/ish-Compliance-Builder/fakefs-compiler/compile_fakefs.py "${SNAP_TAR}" "${OUT_DIR}"
rm -f "${SNAP_TAR}"

echo "=========================================================="
echo "[COMPLETADO] Contenido de ${OUT_DIR}:"
ls -lh "${OUT_DIR}"
echo "Total de inodos registrados en meta.db:"
python3 -c "import sqlite3; c=sqlite3.connect('${OUT_DIR}/meta.db').cursor(); print(c.execute('SELECT COUNT(*) FROM stats;').fetchone()[0], 'inodos verificados.')"
echo "=========================================================="
