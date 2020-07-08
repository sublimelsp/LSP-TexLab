import bz2
import os
import tarfile
import zipfile

from LSP.plugin.core.typing import Optional


def decompress(tarball: str, dst_dir: Optional[str] = None) -> None:
    """
    @brief Decompress the tarball.

    @param tarball The tarball
    @param dst_dir The destination directory
    """

    if not dst_dir:
        dst_dir = os.path.dirname(tarball)

    if tarball.endswith(".bz2"):
        with bz2.BZ2File(tarball) as f:
            f.extractall(dst_dir)
        return

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
