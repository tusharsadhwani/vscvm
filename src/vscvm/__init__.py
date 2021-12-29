"""VSCode version manager."""
import os
import os.path
import re
import shutil
import subprocess
import urllib.request
from typing import Any, List, NamedTuple, Optional, Set

import bs4
import click

VSCVM_PATH = os.path.expanduser("~/.vscvm")

VSCODE_BASE_URL = "https://code.visualstudio.com"
VSCODE_RELEASES_URL = VSCODE_BASE_URL + "/updates"

VSCODE_DESKTOP_DATA = """\
[Desktop Entry]
Name=Visual Studio Code
Comment=Code Editing. Redefined.
GenericName=Text Editor
Exec={path} --unity-launch %F
Icon={icon_path}
Type=Application
StartupNotify=false
StartupWMClass=Code
Categories=Utility;TextEditor;Development;IDE;
MimeType=text/plain;inode/directory;application/x-code-workspace;
Actions=new-empty-window;
Keywords=vscode;

X-Desktop-File-Install-Version=0.26

[Desktop Action new-empty-window]
Name=New Empty Window
Exec={path} --new-window %F
Icon={icon_path}
"""


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


def setup_vscode_version(url: str, version_num: str) -> bool:
    """Downloads and extracts the given VSCode version"""
    version_path = os.path.join(VSCVM_PATH, version_num)

    is_cached = os.path.isdir(version_path) and os.listdir(version_path)
    if is_cached:
        # Directory exists and is not empty. Assume it's already downloaded.
        return True

    filepath = download_vscode(url, version_num)
    extract_vscode(filepath, version_path)
    return False


def download_vscode(url: str, version: str) -> str:
    """Downloads the VSCode url and returns the download path"""
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


def extract_vscode(filepath: str, version: str) -> None:
    """Extracts the downloaded VSCode zipfile in the appropriate folder"""
    version_path = os.path.join(VSCVM_PATH, version)
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


def install_vscode(version: str) -> None:
    """Adds the VSCode runner script and .desktop file"""
    version_path = os.path.join(VSCVM_PATH, version)

    code_script_path = os.path.join(VSCVM_PATH, "code")
    code_binary_path = os.path.join(version_path, "bin/code")
    with open(code_script_path, "w") as file:
        file.write(f"{code_binary_path} $@")

    os.chmod(code_script_path, 0o755)

    # Add Desktop Icon metadata
    icon_folder_path = os.path.expanduser("~/.local/share/applications")
    if not os.path.exists(icon_folder_path):
        os.makedirs(icon_folder_path)

    icon_path = os.path.join(version_path, "resources/app/resources/linux/code.png")
    icon_data = VSCODE_DESKTOP_DATA.format(path=code_binary_path, icon_path=icon_path)
    icon_file_path = os.path.join(icon_folder_path, "code.desktop")
    with open(icon_file_path, "w") as icon_file:
        icon_file.write(icon_data)


def get_installed_versions() -> Set[str]:
    """Returns all vscode versions installed on the system"""
    installed_versions: Set[str] = set()

    version_regex = re.compile(r"\d+\.\d+")
    for folder in os.listdir(VSCVM_PATH):
        if version_regex.match(folder):
            installed_versions.add(folder)

    return installed_versions


def get_active_version() -> Optional[str]:
    """Returns currently active vscode version, or None"""
    script_file_path = os.path.join(VSCVM_PATH, "code")
    if not os.path.isfile(script_file_path):
        return None

    with open(script_file_path) as script_file:
        script_data = script_file.read()

    script_regex = re.compile(r"/home/.+/\.vscvm/(\d+\.\d+)")
    match = script_regex.match(script_data)

    if match is None:
        return None

    (version,) = match.groups()
    return version


@click.group()
def cli() -> None:
    """VSCode version manager"""


@cli.command()
@click.option("--count", "-n", default=5, help="Number of versions to show")
@click.option("--installed", is_flag=True, help="Only show installed versions")
@click.option("--active", is_flag=True, help="Only show currently active version")
def list(count: int, installed: bool, active: bool) -> None:
    """List all VSCode versions"""
    active_version = get_active_version()
    installed_versions = get_installed_versions()
    for _, version, month in get_vscode_versions()[:count]:
        if version == active_version:
            status = "[Active]"

        elif version in installed_versions:
            # If --active flag was passed, don't print this one
            if active:
                continue

            status = "[Installed]"

        else:
            # If installed or active flag was passed, don't print this one
            if active or installed:
                continue

            status = ""

        print(f"v{version:5} - {month:14} {status}")


@cli.command()
@click.argument("version")
def install(version: str) -> None:
    """Install a version of VSCode"""
    version = version.lstrip("v")

    for url, version_num, month in get_vscode_versions():
        if version != "latest" and version != version_num:
            continue

        print(f"Downloading v{version_num} - {month}...")
        is_cached = setup_vscode_version(url, version_num)
        if is_cached:
            print(f"Using cached v{version_num}...")

        install_vscode(version_num)
        print(f"Successfully Installed v{version_num}!")
        break

    else:
        print(f"No version found matching: {version}")


@cli.command()
@click.argument("version", default="")
def uninstall(version: str) -> None:
    _uninstall(version)


def _uninstall(version: str) -> None:
    """Uninstall a VSCode versions"""
    version = version.lstrip("v")

    if version == "":
        active_version = get_active_version()
        if active_version is None:
            print("No active VSCode version found. Aborting.")
            return

        version = active_version

    version = version.lstrip("v")
    version_path = os.path.join(VSCVM_PATH, version)
    if not os.path.exists(version_path):
        print(f"{version} does not exist in installed versions.")
        return

    shutil.rmtree(version_path)

    active_version = get_active_version()
    if version == active_version:
        script_file_path = os.path.join(VSCVM_PATH, "code")
        os.remove(script_file_path)

        launcher_file = os.path.expanduser("~/.local/share/applications/code.desktop")
        if os.path.exists(launcher_file):
            os.remove(launcher_file)

    print(f"Uninstalled v{version}.")


@cli.command()
def cleanup() -> None:
    """Cleans up older, unused versions of vscode"""
    active_version = get_active_version()
    installed_versions = get_installed_versions()

    for version in installed_versions:
        if version == active_version:
            continue

        _uninstall(version)


def check_update() -> None:
    """Check for updates at startup"""
    if os.path.exists("/tmp/vscvm_check_update"):
        return

    try:
        # Create a temp file as an indication that we have run the update check
        open("/tmp/vscvm_check_update", "w").close()

        print("vscvm is checking for updates, please wait...")
        vscode_versions = get_vscode_versions()
        latest_version = vscode_versions[0].version
        installed_versions = get_installed_versions()
        if all(version < latest_version for version in installed_versions):
            print(f"A new version of VSCode is available: v{latest_version}")
            print(f"Run 'vsc install latest' to install it.")

    except:
        pass


def main() -> None:
    """Main function"""
    cli()
