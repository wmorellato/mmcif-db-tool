import pytest
import tempfile

from mmcif_db_tool.schema_map import SchemaMap, SqlAlchemyOrmPrinter, SqlAlchemyCorePrinter
from mmcif_db_tool.mmcif_dict import DictReader


def test_orm_model():
    output_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    mp = SqlAlchemyOrmPrinter(fp=output_file, include_imports=False)
    categories = cr.get_categories(categories=["pdbx_initial_refinement_model"])
    sm = SchemaMap(printer=mp, ignore_relationships=True)
    sm.add_categories(categories)
    sm.print_models()
    output_file.close()

    with open(output_file.name, "r") as f:
        content = f.read()
        assert "class PdbxInitialRefinementModel(Base):" in content
        assert "id: Mapped[Optional[int]] = mapped_column(primary_key=True" in content


def test_core_model():
    output_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    mp = SqlAlchemyCorePrinter(fp=output_file, include_imports=False)
    categories = cr.get_categories(categories=["chem_comp_angle"])
    sm = SchemaMap(printer=mp, ignore_relationships=True)
    sm.add_categories(categories)
    sm.print_models()
    output_file.close()

    with open(output_file.name, "r") as f:
        content = f.read()
        print(content)
        assert "chem_comp_angle = Table(" in content
        assert '"chem_comp_angle",' in content
        assert "metadata_obj," in content
        assert 'Column("atom_id_1", String(6), primary_key=True' in content
        assert 'Column("atom_id_2", String(6), primary_key=True' in content
        assert 'Column("atom_id_3", String(6), primary_key=True' in content
        assert 'Column("comp_id", String(10), primary_key=True' in content
        assert 'Column("value_angle", Float),' in content
