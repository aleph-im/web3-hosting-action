#!/usr/bin/env python3
"""Upload a directory to the Aleph IPFS gateway without authentication.

Used for free previews: the content isn't pinned by any STORE message,
so the gateway garbage-collects it ~24 hours after upload and no
credits are consumed. Production deployments don't use this script,
they go through the Aleph CLI instead (see action.yml).
"""
import json
import sys
from pathlib import Path

import requests

IPFS_GATEWAY = "https://ipfs.aleph.cloud"


def upload_directory(folder: Path, gateway: str) -> str:
    url = f"{gateway}/api/v0/add"
    # cid-version=1 returns a base32 CID directly, as required for the
    # case-insensitive subdomain gateway URLs (https://<cid>.ipfs.aleph.sh).
    # raw-leaves matches the Aleph CLI upload defaults so a preview and a
    # deployment of the same content produce the same CID.
    params = {
        "recursive": "true",
        "wrap-with-directory": "true",
        "cid-version": "1",
        "raw-leaves": "true",
    }

    # The filename of each part must be the path relative to the uploaded
    # folder, or the gateway can't rebuild the directory tree / infer MIME
    # types and serves everything as text/plain.
    files = []
    for path in sorted(folder.rglob("*")):
        if path.is_file():
            relative_path = path.relative_to(folder)
            files.append(("file", (str(relative_path), open(path, "rb"))))

    if not files:
        raise RuntimeError(f"No files found in {folder}")

    response = requests.post(url, params=params, files=files, timeout=1200)
    response.raise_for_status()

    # The response streams one JSON line per file; the wrapper directory
    # containing the whole site is the last entry.
    lines = response.text.strip().splitlines()
    cid = json.loads(lines[-1]).get("Hash") if lines else None

    if not cid:
        raise RuntimeError("CID not found in response.")
    return cid


if __name__ == "__main__":
    path = Path(sys.argv[1])
    if not path.is_dir():
        print("Error: path must be a directory")
        sys.exit(1)

    cid = upload_directory(path.resolve(), IPFS_GATEWAY)
    print(json.dumps({"cid": cid}))
