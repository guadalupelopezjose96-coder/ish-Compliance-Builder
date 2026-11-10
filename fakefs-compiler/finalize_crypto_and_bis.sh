#!/bin/sh
set -eu

REPORT_DIR="/root/ish-Compliance-Builder/audit-reports"

echo "[1/3] Endureciendo cliente OpenSSH y generando par Ed25519..."
mkdir -p /root/.ssh
chmod 0700 /root/.ssh

if [ ! -f /root/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -a 100 -N "" -C "ish-secops-enterprise-key" -f /root/.ssh/id_ed25519 >/dev/null
fi

cat << 'SSHCFG' > /root/.ssh/config
Host *
    Protocol 2
    KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256,curve25519-sha256@libssh.org
    Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com
    MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
    HostKeyAlgorithms ssh-ed25519,rsa-sha2-512
    IdentitiesOnly yes
    HashKnownHosts yes
    StrictHostKeyChecking ask
SSHCFG
chmod 0600 /root/.ssh/config /root/.ssh/id_ed25519
chmod 0644 /root/.ssh/id_ed25519.pub

echo "[2/3] Generando Reporte Anual CSV oficial para BIS (15 CFR 740.17)..."
cat << 'CSV' > "${REPORT_DIR}/BIS_ANNUAL_SELF_CLASSIFICATION_5D992C.csv"
"PRODUCT NAME","MODEL/SERIES NUMBER","MANUFACTURER","ECCN","AUTHORIZATION TYPE","ITEM TYPE","CRYPTOSYSTEMS"
"iSH Enterprise Linux Environment","3.20-i386","Independent Developer","5D992.c","MMKT","Client Application / OS Emulator","AES-256-GCM, ChaCha20-Poly1305, Ed25519, RSA-4096, SHA-256 (OpenSSL 3.x / OpenSSH)"
CSV

echo "[3/3] Generando llaves de cumplimiento para Info.plist de Xcode..."
cat << 'PLIST' > "${REPORT_DIR}/Xcode_Compliance_InfoPlist_Keys.xml"
<!-- Insertar dentro del diccionario principal <dict> de Info.plist en Xcode -->
<key>ITSAppUsesNonExemptEncryption</key>
<true/>
<key>ITSEncryptionExportComplianceCode</key>
<string>ECCN-5D992C-SELF-CLASSIFIED</string>
<key>UIFileSharingEnabled</key>
<false/>
<key>LSSupportsOpeningDocumentsInPlace</key>
<true/>
PLIST

echo "=========================================================="
echo "[COMPLETADO] Huella de tu llave publica SSH Ed25519:"
ssh-keygen -lf /root/.ssh/id_ed25519.pub
echo "Archivos regulatorios listos en ${REPORT_DIR}:"
ls -lh "${REPORT_DIR}"
echo "=========================================================="
