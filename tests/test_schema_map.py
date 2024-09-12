import pytest
import tempfile

from schema_map import SchemaMap, SqlAlchemyPrinter
from mmcif_dict import DictReader


def test_model():
    output_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    mp = SqlAlchemyPrinter(fp=output_file, include_imports=False)
    categories = cr.get_categories(categories=["pdbx_initial_refinement_model"])
    sm = SchemaMap(printer=mp, ignore_relationships=True)
    sm.add_categories(categories)
    sm.print_models()
    output_file.close()

    with open(output_file.name, "r") as f:
        content = f.read()
        assert content.startswith("class PdbxInitialRefinementModel(Base):")
        assert "id: Mapped[Optional[int]] = mapped_column(primary_key=True" in content


def test_chem_comp():
    output_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    mp = SqlAlchemyPrinter(fp=output_file, include_imports=False)
    categories = cr.get_categories(categories=["chem_comp_angle"])
    sm = SchemaMap(printer=mp, ignore_relationships=True)
    sm.add_categories(categories)
    sm.print_models()
    output_file.close()