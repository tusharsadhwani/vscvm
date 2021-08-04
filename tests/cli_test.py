from pytest import CaptureFixture

from vscvm import cli


def test_cli(capsys: CaptureFixture[str]) -> None:
    """Tests test_function from the package"""
    cli()
    captured = capsys.readouterr()
    assert captured.out == "VSCode version manager.\n"
