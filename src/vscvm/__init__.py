"""VSCode version manager."""
import argparse
import bs4
import urllib.request

import click


@click.group()
def cli() -> None:
    """VSCode version manager"""


@cli.command()
def list() -> None:
    """List all VSCode versions"""
    with urllib.request.urlopen("https://code.visualstudio.com/updates") as request:
        html = request.read()

        soup = bs4.BeautifulSoup(html, "html.parser")
        vscode_version_links = soup.select("#docs-navbar a")
        for link in vscode_version_links[:5]:
            url = link.get("href")
            _, _, version = url.rpartition("/")
            month = link.text
            print(f"{version} - {month}")


def main() -> None:
    """Main function"""
    cli()
