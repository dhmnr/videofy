"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Videofy."""


if __name__ == "__main__":
    main(prog_name="videofy")  # pragma: no cover
