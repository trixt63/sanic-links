# cli/__init__.py
# declare the commands 
import click
from cli.api.count_view import count_view

@click.group()
def cli():
    pass

cli.add_command(count_view, 'count_view')