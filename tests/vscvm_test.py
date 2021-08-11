from pytest import CaptureFixture

import vscvm


def test_updates_url() -> None:
    links = vscvm.get_vscode_version_links()
    assert len(links) != 0


def test_list(capsys: CaptureFixture[str]) -> None:
    """Tests test_function from the package"""
    versions = vscvm.get_vscode_versions()
    assert len(versions) != 0
