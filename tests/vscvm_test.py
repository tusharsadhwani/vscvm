import random

from pytest import CaptureFixture

import vscvm


def test_updates_url() -> None:
    links = vscvm.get_vscode_version_links()
    assert len(links) != 0


def test_list(capsys: CaptureFixture[str]) -> None:
    """Tests test_function from the package"""
    versions = vscvm.get_vscode_versions()
    assert len(versions) != 0


def test_fetch_download_url() -> None:
    versions = vscvm.get_vscode_versions()
    random_version = random.choice(versions)
    download_url = vscvm.fetch_download_url(random_version.url)
    assert random_version.version in download_url


def test_fetch_direct_download_url() -> None:
    versions = vscvm.get_vscode_versions()
    random_version = random.choice(versions)
    download_url = vscvm.fetch_download_url(random_version.url)
    direct_download_url = vscvm.fetch_direct_download_url(download_url)
    assert direct_download_url.endswith(".tar.gz")
