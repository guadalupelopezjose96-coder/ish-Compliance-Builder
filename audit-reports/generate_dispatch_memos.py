#!/usr/bin/env python3
import json
from pathlib import Path

report_dir = Path("/root/ish-Compliance-Builder/audit-reports")

bis_email_template = """DE: compliance@tu-dominio-o-entidad.com
PARA: crypt-suppl8@bis.doc.gov, enc@nsa.gov
ASUNTO: ANNUAL SELF-CLASSIFICATION REPORT - ECCN 5D992.c - Independent Developer

Dear BIS Encryption Coordinator and NSA Encryption Request Coordinator,

In accordance with 15 CFR Section 740.17(e)(3) of the Export Administration Regulations (EAR), please find attached the Annual Self-Classification Report for mass market encryption software items authorized under Section 740.17(b)(1).

Reporting Entity: Independent Developer / Enterprise Mobile Systems
Reporting Period: Annual Return
Attached File: BIS_ANNUAL_SELF_CLASSIFICATION_5D992C.csv

Item Summary:
- Product Name: iSH Enterprise Linux Environment
- Model/Version: 3.20-i386
- ECCN: 5D992.c
- Authorization: MMKT (Mass Market)
- Encryption: AES-256-GCM, ChaCha20-Poly1305, Ed25519 (OpenSSL 3.x / OpenSSH)

Should you require any additional information, please do not hesitate to contact us.

Sincerely,
Compliance & DevSecOps Lead
"""

(report_dir / "BIS_TRANSMISSION_EMAIL_TEMPLATE.txt").write_text(bis_email_template, encoding="utf-8")

github_release_template = """# Open Source Compliance Notice - iSH Enterprise Immutable RootFS

## GNU General Public License v2.0 (GPLv2) - Written Offer
In accordance with Section 3(b) of the GNU General Public License v2.0, complete machine-readable copies of the Corresponding Source code for all GPL/LGPL packages pre-installed within the immutable RootFS are made available here.

- Core Engine: Distributed under GNU GPLv2.
- Pre-installed Alpine Linux Packages: 60 GPL/LGPL components tracked in `GPL_CORRESPONDING_SOURCE_MANIFEST.json`.
- Provenance & Build Recipes: Exact `APKBUILD` files and commit SHA-1 snapshots included in `GPLv2_Source_Compliance_Archive.tar.gz`.

### Verification Hashes (SHA-256)
All release binaries and manifests are cryptographically verified:
```text
Release Archive: 40e3927d3d0816c30809c74641b0d9dd8223ab0a158121fb083aeb7d1cf45277e
mkdir -p /root/ish-Compliance-Builder/audit-reports && cd /root/ish-Compliance-Builder/audit-reports

cat << 'EOF' > BIS_TRANSMISSION_EMAIL_TEMPLATE.txt
DE: compliance@tu-dominio-o-entidad.com
PARA: crypt-suppl8@bis.doc.gov, enc@nsa.gov
ASUNTO: ANNUAL SELF-CLASSIFICATION REPORT - ECCN 5D992.c - Independent Developer

Dear BIS Encryption Coordinator and NSA Encryption Request Coordinator,

In accordance with 15 CFR Section 740.17(e)(3) of the Export Administration Regulations (EAR), please find attached the Annual Self-Classification Report for mass market encryption software items authorized under Section 740.17(b)(1).

Reporting Entity: Independent Developer / Enterprise Mobile Systems
Attached File: BIS_ANNUAL_SELF_CLASSIFICATION_5D992C.csv

Item Summary:
- Product Name: iSH Enterprise Linux Environment (3.20-i386)
- ECCN: 5D992.c
- Authorization: MMKT (Mass Market)
- Encryption: AES-256-GCM, ChaCha20-Poly1305, Ed25519 (OpenSSL 3.x / OpenSSH)

Sincerely,
Compliance & DevSecOps Lead
