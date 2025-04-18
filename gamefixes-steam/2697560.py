"""Game fix for Mojika - Truth Rears Its Ugly Head"""

import os
from gzip import open as gzip_open
from hashlib import sha256
from tempfile import mkdtemp
from urllib.request import urlopen

from protonfixes import util
from protonfixes.logger import log


def main() -> None:
    arc = 'https://github.com/user-attachments/files/16788423/xaudio2_8.dll.gz'
    hashsum_file = '173cac0a7931989d66338e0d7779e451f2f01b2377903df7954d86c07c1bc8fb'
    tmp = f'{mkdtemp()}/xaudio2_8.dll.gz'
    hashsum = sha256()
    path_dll = f'{util.get_game_install_path()}/xaudio2_8.dll'

    if os.path.exists(path_dll):
        log.info(
            f"xaudio2_8.dll exists in '{util.get_game_install_path()}', skipping..."
        )
        return

    # Download the archive
    with urlopen(arc, timeout=30) as resp:
        if resp.status != 200:
            log.warn(f'github returned the status code: {resp.status}')
            return

        with open(tmp, mode='wb', buffering=0) as file:
            chunk_size = 64 * 1024  # 64 KB
            buffer = bytearray(chunk_size)
            view = memoryview(buffer)

            while size := resp.readinto(buffer):
                file.write(view[:size])
                hashsum.update(view[:size])

    # Verify the compessed file
    if hashsum_file != hashsum.hexdigest():
        log.warn(f'Digest mismatch: {arc}')
        log.warn(f"Expected '{hashsum_file}', skipping...")
        return

    # Write xaudio2_8.dll to the game directory
    # NOTE: The file is actually xaudio2_9.dll from winetricks but renamed
    log.info("Applying fix for 'Mojika Truth Rears Its Head'...")
    with gzip_open(tmp, 'rb') as reader:
        with open(path_dll, 'wb') as writer:
            writer.write(reader.read())
    util.disable_protonmediaconverter()
