import sys
import click
import logging

from mmcif_db_tool.mmcif_dict import DictReader, ItemFilter
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


def get_filtered_items(path):
    with open(path) as f:
        return set([line.strip() for line in f])


@click.command()
@click.argument("mmcif_dictionary", type=click.Path())
@click.option("--categories", help="A comma-separated list of categories to be processed, e.g. 'chem_comp,chem_comp_atom'")
@click.option("--categories-file", type=click.Path(exists=True), help="A file containing the list of categories to be processed")
@click.option("--model", type=str, default="orm", help="Choose between 'orm' and 'core' models")
@click.option("--include-items-file", type=click.Path(), help="Path to the file containing the list of categories and items to be included. The file have one 'category_name.item_name' per line. Any item not included in the file will be ignored. Cannot be used with --exclude-items-file.")
@click.option("--exclude-items-file", type=click.Path(), help="Path to the file containing the list of categories and items to be included. The file have one 'category_name.item_name' per line. Any item not included in the file will be processed. Cannot be used with --include-items-file.")
@click.option("--output-file", type=click.Path(), help="Path to the output file")
def process_categories(mmcif_dictionary, categories, categories_file, model, include_items_file, exclude_items_file, output_file):
    """Create SQLAlchemy models for categories based on the
    input MMCIF_DICTIONARY.

    If you want to pass a file with the list of categories through
    the option `--categories-file`, set CATEGORIES to "-".
    """
    click.echo(f"Processing categories: {categories}")
    cr = DictReader(path=mmcif_dictionary)

    if [categories, categories_file].count(None) == 2 or [categories, categories_file].count(None) == 0:
        raise click.UsageError("Either provide a list of categories or a file containing the list of categories")

    if include_items_file and exclude_items_file:
        raise click.UsageError("These options are mutually exclusive: --include-items-file, --exclude-items-file")

    if categories_file:
        categories = get_cats_from_file(categories_file)

    if include_items_file:
        included_items = get_filtered_items(include_items_file)

    if exclude_items_file:
        excluded_items = get_filtered_items(exclude_items_file)

    filter = ItemFilter(include_items=included_items, exclude_items=excluded_items)
    cat_objs = cr.get_categories(categories=categories, filter=filter)

    with open(output_file, "w") if output_file else sys.stdout as f:
        mp = get_printer(model, include_imports=True, fp=f)
        sm = SchemaMap(printer=mp, ignore_relationships=True)
        sm.add_categories(cat_objs)
        sm.print_models()


if __name__ == "__main__":
    process_categories()
