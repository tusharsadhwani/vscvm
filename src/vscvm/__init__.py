"""VSCode version manager."""
import re
import subprocess
import urllib.request
from typing import List, NamedTuple

import bs4
import click


class VSCodeVersionInfo(NamedTuple):
    """Holds the version number and release month of a VSCode release"""

    url: str
    version: str
    month: str


def get_vscode_versions() -> List[VSCodeVersionInfo]:
    versions: List[VSCodeVersionInfo] = []
    with urllib.request.urlopen("https://code.visualstudio.com/updates") as request:
        html = request.read()

        page = bs4.BeautifulSoup(html, "html.parser")
        vscode_version_links = page.select("#docs-navbar a")
        for link in vscode_version_links[:5]:
            url: str = link.get("href")
            if url.startswith("/updates"):
                url = "https://code.visualstudio.com" + url

            month = link.text

            _, _, version = url.rpartition("/")
            version = version.lstrip("v").replace("_", ".")

            versions.append(VSCodeVersionInfo(url, version, month))

    return versions


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

        with urllib.request.urlopen(url) as request:
            html = request.read()
            page = bs4.BeautifulSoup(html, "html.parser")
            description = page.select(".body")[0]

            download_regex = re.compile("Downloads: Windows:")
            links = description.find(text=download_regex).parent

            linux_link = links.find("a", text="tarball")
            download_url = linux_link["href"]

            print(f"Downloading v{version_num} - {month}...")

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

            subprocess.call(
                [
                    "curl",
                    "-L",
                    "--progress-bar",
                    direct_download_url,
                    "-o",
                    f"code-{version_num}.tar.gz",
                ]
            )
            break
    else:
        print(f"No version found matching: {version}")


def main() -> None:
    """Main function"""
    cli()
