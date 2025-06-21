#!/usr/bin/env python3

"""
This script uploads the build SPA to IPFS.
It does not pin it or do anything else yet, so the result can only be accessed
as long as the files are not garbage collected.
"""
import asyncio, aiohttp, json, logging
from pathlib import Path
from cid import make_cid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ipfs-upload")

async def upload_dir_via_http(path: Path, gateway: str, timeout_sec=120):
    # Build multipart/form-data for all files in the directory
    mp = aiohttp.MultipartWriter()
    for file in path.rglob('*'):
        if file.is_file():
            part = mp.append(file.read_bytes())
            part.set_content_disposition(
                'form-data',
                name='file',
                filename=str(file.relative_to(path.parent))
            )
    url = f"{gateway}/api/v0/add?recursive=true&wrap-with-directory=true"
    timeout = aiohttp.ClientTimeout(total=timeout_sec)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, data=mp) as resp:
            resp.raise_for_status()
            cid_v0 = None
            async for line in resp.content:
                j = json.loads(line.decode())
                logger.debug("Got entry: %s", j)
                cid_v0 = j.get("Hash")

    if not cid_v0:
        raise RuntimeError("No CID returned")
    cid_v1 = make_cid(cid_v0).to_v1().encode('base32').decode()
    return {"cid_v0": cid_v0, "cid_v1": cid_v1}

async def main():
    import sys
    path = Path(sys.argv[1])
    gw = "https://ipfs-2.aleph.im"
    result = await upload_dir_via_http(path, gw)
    print(json.dumps(result))

if __name__ == "__main__":
    asyncio.run(main())
