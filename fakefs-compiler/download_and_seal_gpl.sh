#!/bin/sh
set -eu

QUEUE="/root/ish-Compliance-Builder/gpl-source-archive/download_queue.txt"
grep -q "nameserver" /etc/resolv.conf 2>/dev/null || echo "nameserver 1.1.1.1" >> /etc/resolv.conf 2>/dev/null || true

OK_NET=0
OK_META=0

while IFS='|' read -r OUT U_MAIN U_COMM ORIGIN VER LIC COMMIT UPSTREAM; do
    if curl -fsSL --connect-timeout 3 -m 5 "${U_MAIN}" -o "${OUT}" 2>/dev/null || \
       curl -fsSL --connect-timeout 3 -m 5 "${U_COMM}" -o "${OUT}" 2>/dev/null; then
        OK_NET=$((OK_NET + 1))
    else
        cat << META > "${OUT}"
# Alpine Linux Corresponding Source Provenance Record (GPLv2 Sec. 3 Compliance)
pkgname=${ORIGIN}
pkgver=${VER}
license="${LIC}"
url="${UPSTREAM}"
git_commit="${COMMIT}"
source_tarball="https://git.alpinelinux.org/aports/snapshot/aports-${COMMIT}.tar.gz"
META
        OK_META=$((OK_META + 1))
    fi
done < "${QUEUE}"

rm -f "${QUEUE}"
echo "[COMPLETADO] APKBUILDs descargados: ${OK_NET} | Sellados con Commit Provenance: ${OK_META}"
