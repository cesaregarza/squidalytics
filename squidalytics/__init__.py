import click

import squidalytics.analytics.pandas.accessor
from squidalytics.schemas import battleSchema


@click.group()
@click.pass_context
def main(ctx: click.Context) -> None:
    click.echo("Hello, world!")


@main.command()
@click.argument("file", type=click.Path(exists=True))
def load(file: str) -> None:
    click.echo("Loading data...")
    battle_schema = battleSchema.load(file)
    click.echo("Data loaded.")
    click.echo(f"Number of battles: {len(battle_schema)}")


if __name__ == "__main__":
    main()
