import click
import logging

from mmcif_db_tool.mmcif_dict import DictReader
from mmcif_db_tool.schema_map import SchemaMap, SqlAlchemyOrmPrinter, SqlAlchemyCorePrinter

# logging.basicConfig(level=logging.DEBUG)
logging.getLogger("mmcif_dict").setLevel(logging.DEBUG)


@click.command()
@click.argument("input-dict", type=click.Path())
@click.argument("categories", nargs=-1)
@click.option("--model", type=str, default="orm", help="Choose between 'orm' and 'core' models")
@click.option("--output-file", type=click.Path(), help="Path to the output file")
def process_categories(input_dict, categories, model, output_file):
    click.echo(f"Processing categories: {categories}")

    cr = DictReader(path=input_dict)
    categories = cr.get_categories(categories=categories)

    if output_file:
        with open(output_file, "w") as f:
            if model == "orm":
                mp = SqlAlchemyOrmPrinter(fp=f, include_imports=True)
            elif model == "core":
                mp = SqlAlchemyCorePrinter(fp=f, include_imports=True)
            sm = SchemaMap(printer=mp, ignore_relationships=True)
            sm.add_categories(categories)
            sm.print_models()
    else:
        if model == "orm":
            mp = SqlAlchemyOrmPrinter(include_imports=True)
        elif model == "core":
            mp = SqlAlchemyCorePrinter(include_imports=True)
        sm = SchemaMap(printer=mp, ignore_relationships=True)
        sm.add_categories(categories)
        sm.print_models()


if __name__ == "__main__":
    process_categories()
