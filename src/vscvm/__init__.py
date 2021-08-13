"""VSCode version manager."""
import os
import os.path
import re
import subprocess
import urllib.request
from typing import Any, List, NamedTuple

import bs4
import click


VSCODE_BASE_URL = "https://code.visualstudio.com"
VSCODE_RELEASES_URL = VSCODE_BASE_URL + "/updates"


class VSCodeVersionInfo(NamedTuple):
    """Holds the version number and release month of a VSCode release"""

    url: str
    version: str
    month: str


def get_vscode_version_links() -> Any:
    with urllib.request.urlopen(VSCODE_RELEASES_URL) as request:
        html = request.read()

        page = bs4.BeautifulSoup(html, "html.parser")
        vscode_version_links = page.select("#docs-navbar a")
        return vscode_version_links


def get_vscode_versions() -> List[VSCodeVersionInfo]:
    """Gets the list of latest VSCode release versions"""
    versions: List[VSCodeVersionInfo] = []

    for link in get_vscode_version_links():
        url: str = link.get("href")
        if not url.startswith(VSCODE_BASE_URL):
            url = VSCODE_BASE_URL + url

        month = link.text

        _, _, version = url.rpartition("/")
        version = version.lstrip("v").replace("_", ".")

        versions.append(VSCodeVersionInfo(url, version, month))

    return versions


def fetch_download_url(version_url: str) -> str:
    """Gets the linux tar download link from a VSCode release webpage"""
    with urllib.request.urlopen(version_url) as request:
        html = request.read()
        page = bs4.BeautifulSoup(html, "html.parser")
        description = page.select(".body")[0]

        download_regex = re.compile("Downloads: Windows:")
        paragraph = description.find(text=download_regex)
        assert paragraph is not None

        links = paragraph.parent
        assert links is not None
        linux_link = links.find("a", text="tarball")
        assert isinstance(linux_link, bs4.element.Tag)

        download_url = linux_link.attrs["href"]
        return download_url


def fetch_direct_download_url(download_url: str) -> str:
    """Fetches the direct download link from a redirecting URL"""
    process = subprocess.Popen(
        [
            "curl",
            "-ILs",
            "-o/dev/null",
            "-w %{url_effective}",
            download_url,
        ],
        stdout=subprocess.PIPE,
    )
    assert process.stdout is not None
    direct_download_url = process.stdout.read().decode().strip()
    return direct_download_url


def download_vscode(url: str, version: str) -> str:
    """Downloads the vscode url and returns the download path"""
    download_url = fetch_download_url(url)
    direct_download_url = fetch_direct_download_url(download_url)

    filename = f"code-{version}.tar.gz"
    filepath = os.path.join("/tmp", filename)
    subprocess.call(
        [
            "curl",
            "-L",
            "--progress-bar",
            direct_download_url,
            "-o",
            filepath,
        ]
    )
    return filepath


def install_vscode(filepath: str, version: str) -> None:
    vscvm_path = os.path.expanduser("~/.vscvm")
    version_path = os.path.join(vscvm_path, version)
    if not os.path.exists(version_path):
        os.makedirs(version_path)

    subprocess.call(
        [
            "tar",
            "--strip-components=1",
            "-xzf",
            filepath,
            "-C",
            version_path,
        ]
    )

    code_script_path = os.path.join(vscvm_path, "code")
    code_binary_path = os.path.join(version_path, "bin/code")
    with open(code_script_path, "w") as file:
        file.write(f"{code_binary_path} $@")

    os.chmod(code_script_path, 0o755)


@click.group()
def cli() -> None:
    """VSCode version manager"""


@cli.command()
@click.option("--count", "-n", default=5, help="Number of versions to show")
def list(count: int) -> None:
    """List all VSCode versions"""
    for _, version, month in get_vscode_versions()[:count]:
        print(f"v{version} - {month}")


@cli.command()
@click.argument("version")
def install(version: str) -> None:
    """Install a version of VSCode"""
    version = version.lstrip("v")

    for url, version_num, month in get_vscode_versions():
        if version != "latest" and version != version_num:
            continue

        print(f"Downloading v{version_num} - {month}...")
        filepath = download_vscode(url, version_num)
        install_vscode(filepath, version_num)
        print(f"Successfully Installed v{version_num}!")
        break

    else:
        print(f"No version found matching: {version}")


def main() -> None:
    """Main function"""
    cli()
