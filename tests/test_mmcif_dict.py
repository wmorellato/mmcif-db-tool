import pytest

from mmcif_db_tool.mmcif_dict import DictReader


def test_category():
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    categories = cr.get_categories(categories=["pdbx_initial_refinement_model"])

    assert len(categories) == 1
    assert categories[0].id == "pdbx_initial_refinement_model"
    assert categories[0].description == "Data items in the pdbx_initial_refinement_model record the starting model(s) used in structure determination."

    assert len(categories[0].items) == 6
    assert categories[0].items[0].full_name == "_pdbx_initial_refinement_model.id"
    assert categories[0].items[0].name == "id"
    assert categories[0].items[0].description == "A unique identifier for the starting model record."
    assert categories[0].items[0].index == True
    assert categories[0].items[0].mandatory_code == True
    assert categories[0].items[0].type_code == "int"
    assert categories[0].items[0].default_value == None


def test_multiple_categories():
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    categories = cr.get_categories(categories=["pdbx_initial_refinement_model", "audit"])

    assert len(categories) == 2
    assert categories[0].id == "audit"
    assert categories[1].id == "pdbx_initial_refinement_model"

    assert len(categories[1].items) == 6
    assert categories[1].items[0].name == "id"
    assert categories[1].items[1].name == "entity_id_list"
    assert categories[1].items[2].name == "type"
    assert categories[1].items[3].name == "source_name"
    assert categories[1].items[4].name == "accession_code"
    assert categories[1].items[5].name == "details"

    assert len(categories[0].items) == 4
    assert categories[0].items[0].name == "creation_date"
    assert categories[0].items[1].name == "creation_method"
    assert categories[0].items[2].name == "revision_id"
    assert categories[0].items[3].name == "update_record"


def test_chem_comp_cats():
    # some chem_comp* categories don't contain the _item.category_id
    # value, so they are not parsed correctly
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    categories = cr.get_categories(categories=["chem_comp_angle"])

    assert len(categories) == 1
    assert categories[0].items[0].name == "atom_id_1"
    assert categories[0].items[1].name == "atom_id_2"
    assert categories[0].items[2].name == "atom_id_3"
    assert categories[0].items[3].name == "comp_id"
    assert categories[0].items[4].name == "value_angle"
    assert categories[0].items[5].name == "value_angle_esd"
    assert categories[0].items[6].name == "value_dist"
    assert categories[0].items[7].name == "value_dist_esd"


def test_grouped_items():
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    categories = cr.get_categories(categories=["chem_comp_angle"])

    assert categories[0].items[3].name == "comp_id"
    assert categories[0].items[3].full_name == "_chem_comp_angle.comp_id"
    assert categories[0].items[3].type_code == "ucode"


def test_last_category():
    cr = DictReader(path="./mmcif_pdbx_v50.dic")
    categories = cr.get_categories(categories=["diffrn_detector_element"])

    assert len(categories) == 1
    assert categories[0].items[0].name == "id"
    assert categories[0].items[1].name == "detector_id"
    assert categories[0].items[2].name == "reference_center_fast"
    assert categories[0].items[3].name == "reference_center_slow"
    assert categories[0].items[4].name == "reference_center_units"
