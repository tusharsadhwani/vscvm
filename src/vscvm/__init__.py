"""VSCode version manager."""
import bs4
import urllib.request


def cli() -> None:
    """CLI interface"""
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
