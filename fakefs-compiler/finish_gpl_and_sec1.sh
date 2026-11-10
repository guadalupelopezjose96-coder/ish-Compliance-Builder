#!/bin/sh
set -eu

BASE_DIR="/root/ish-Compliance-Builder"
SRC_DIR="${BASE_DIR}/gpl-source-archive"
REPORT_DIR="${BASE_DIR}/audit-reports"
GPL_TAR="${BASE_DIR}/GPLv2_Source_Compliance_Archive.tar.gz"
FINAL_ARCHIVE="${BASE_DIR}/iSH_Immutable_Compliance_Release.tar.gz"
DB_PATH="${BASE_DIR}/ImmutableRootFS.bundle/meta.db"

# 1. Empaquetar y sellar los 60 APKBUILDs descargados
tar -czf "${GPL_TAR}" -C "${BASE_DIR}" gpl-source-archive
sha256sum "${GPL_TAR}" > "${GPL_TAR}.sha256"

# 2. Re-empaquetar el release maestro con el archivo de fuentes GPL integrado
tar -czf "${FINAL_ARCHIVE}" -C "${BASE_DIR}" ImmutableRootFS.bundle audit-reports gpl-source-archive
sha256sum "${FINAL_ARCHIVE}" > "${FINAL_ARCHIVE}.sha256"

# 3. [sec_1] Validar integridad SQLite y modo de almacenamiento
python3 -c "
import sqlite3
c = sqlite3.connect('${DB_PATH}')
cur = c.cursor()
cur.execute('PRAGMA integrity_check;')
res = cur.fetchone()[0]
assert res == 'ok', f'Fallo en SQLite: {res}'
print('[sec_1 VERIFICADO] Integridad SQLite de meta.db: OK')
c.close()
"

echo "[OK] GPLv2 Source Archive generado ($(ls -lh "${GPL_TAR}" | awk '{print $5}'))"
echo "[OK] Release Maestro Sellado ($(ls -lh "${FINAL_ARCHIVE}" | awk '{print $5}'))"
cat "${FINAL_ARCHIVE}.sha256"
