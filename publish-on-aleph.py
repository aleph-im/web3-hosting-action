#!/usr/bin/env python3

"""
This script uploads the build SPA to IPFS.
It does not pin it or do anything else yet, so the result can only be accessed
as long as the files are not garbage collected.
"""

import asyncio
import logging
from pathlib import Path
import sys
from cid import make_cid
import aioipfs
import json

logger = logging.getLogger(__file__)

async def upload_site(files: list[Path], multiaddr: str) -> str:
    client = aioipfs.AsyncIPFS(maddr=multiaddr)

    try:
        cid_v0 = None
        async for added_file in client.add(*files, recursive=True):
            logger.debug(
                f"Uploaded file {added_file['Name']} with CID: {added_file['Hash']}"
            )
            cid_v0 = added_file["Hash"]

        # The last CID is the CID of the directory uploaded
        cid_v1 = make_cid(cid_v0).to_v1().encode('base32').decode('utf-8')
        return json.dumps({"cid_v0": cid_v0, "cid_v1": cid_v1})
    finally:
        await client.close()


async def publish_site(multiaddr: str, path: str) -> str:
    cid = await upload_site(files=[path], multiaddr=multiaddr)
    return cid


if __name__ == "__main__":
    path = sys.argv[1]
    logging.basicConfig(level=logging.INFO)
    print(asyncio.run(publish_site("/dns4/ipfs-2.aleph.im/tcp/443/https", path)))
