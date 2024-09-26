import sys
import click
import logging

from mmcif_db_tool.mmcif_dict import DictReader
from mmcif_db_tool.schema_map import SchemaMap, SqlAlchemyOrmPrinter, SqlAlchemyCorePrinter

# logging.basicConfig(level=logging.DEBUG)
logging.getLogger("mmcif_dict").setLevel(logging.DEBUG)


def get_printer(model, include_imports, fp=None):
    if model == "orm":
        return SqlAlchemyOrmPrinter(fp=fp, include_imports=include_imports)
    elif model == "core":
        return SqlAlchemyCorePrinter(fp=fp, include_imports=include_imports)


def get_cats_from_file(path):
    with open(path) as f:
        return [line.strip() for line in f]


@click.command()
@click.argument("input-dict", type=click.Path())
@click.argument("categories", nargs=-1)
@click.option("--input-cats", type=click.Path(exists=True), help="A file containing the list of categories to be processed")
@click.option("--model", type=str, default="orm", help="Choose between 'orm' and 'core' models")
@click.option("--include-items-file", type=click.Path(), help="Path to the file containing the list of categories and items to be included. The file have one 'category_name.item_name' per line. Any item not included in the file will be ignored. CATEGORIES must be set to '-'. Cannot be used with --input-cats or --exclude-items-file.")
@click.option("--exclude-items-file", type=click.Path(), help="Path to the file containing the list of categories and items to be included. The file have one 'category_name.item_name' per line. Any item not included in the file will be processed. CATEGORIES must be set to '-'. Cannot be used with --input-cats or --include-items-file.")
@click.option("--output-file", type=click.Path(), help="Path to the output file")
def process_categories(input_dict, categories, input_cats, model, include_items_file, exclude_items_file, output_file):
    """Create SQLAlchemy models for CATEGORIES based on the
    input dictionary file INPUT_DICT.

    If you want to pass a file with the list of categories through
    the option `--input-cats`, set CATEGORIES to "-".
    """
    click.echo(f"Processing categories: {categories}")
    cr = DictReader(path=input_dict)

    if [input_cats, include_items_file, exclude_items_file].count(True) > 1:
        raise click.UsageError("Either provide a list of categories or a file containing the list of categories")

    if input_cats:
        if categories[0] != "-":
            raise click.UsageError("Either provide a list of categories or a file containing the list of categories")
        categories = get_cats_from_file(input_cats)
    print(categories)
    cat_objs = cr.get_categories(categories=categories)

    with open(output_file, "w") if output_file else sys.stdout as f:
        mp = get_printer(model, include_imports=True, fp=f)
        sm = SchemaMap(printer=mp, ignore_relationships=True)
        sm.add_categories(cat_objs)
        sm.print_models()


if __name__ == "__main__":
    process_categories()
