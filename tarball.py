from LSP.plugin.core.typing import Optional
import gzip
import os
import tarfile
import urllib.request
import zipfile


def decompress(tarball: str, dst_dir: Optional[str] = None) -> None:
    """
    Decompress the tarball.

    :param      tarball:  The tarball
    :param      dst_dir:  The destination directory
    """

    if not dst_dir:
        dst_dir = os.path.dirname(tarball)

    if tarball.endswith(".tar.gz"):
        with tarfile.open(tarball, "r:gz") as f:
            f.extractall(dst_dir)
        return

    if tarball.endswith(".tar"):
        with tarfile.open(tarball, "r:") as f:
            f.extractall(dst_dir)
        return

    if tarball.endswith(".zip"):
        with zipfile.ZipFile(tarball) as f:
            f.extractall(dst_dir)
        return


def download(url: str, save_path: str, chunk_size: int = 512 * 1024) -> None:
    """
    Downloads a file.

    :param url:       The url
    :param save_path: The path of the saved file
    """

    response = urllib.request.urlopen(url)
    data = b""
    while True:
        chunk = response.read(chunk_size)
        if not chunk:
            break
        data += chunk

    if response.info().get("Content-Encoding") == "gzip":
        data = gzip.decompress(data)

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(data)
