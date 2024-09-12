from gemmi import cif


TABLES = [
    "audit_author", 
    "cell1", 
    "chem_comp", 
    "citation", 
    "citation_author", 
    "database_2", 
    "diffrn_source", 
    "em_admin", 
    "em_author_list", 
    "em_depui", 
    "entity", 
    "entity_poly", 
    "exptl", 
    "ndb_struct_conf_na", 
    "pdbx_audit_revision_category", 
    "pdbx_audit_revision_details", 
    "pdbx_audit_revision_group", 
    "pdbx_audit_revision_history", 
    "pdbx_audit_revision_item", 
    "pdbx_contact_author", 
    "pdbx_database_PDB_obs_spr", 
    "pdbx_database_related", 
    "pdbx_database_status_history", 
    "pdbx_deposit_group", 
    "pdbx_depui_entry_details", 
    "pdbx_entity_nonpoly", 
    "pdbx_molecule", 
    "pdbx_molecule_features", 
    "pdbx_prerelease_seq", 
    "pdbx_struct_assembly", 
    "pdbx_struct_assembly_gen", 
    "pdbx_struct_oper_list", 
    "processing_status", 
    "rcsb_status", 
    "struct", 
    "struct_keywords", 
    "struct_site_keywords", 
    "symmetry", 
]

PREFILLED = [
    "text",
    "line",
    "float",
    "ucode",
    "code",
    "uline",
    "int",
    "uchar5",
    "orcid_id",
    "yyyy-mm-dd:hh:mm",
    "pdbx_PDB_obsoleted_db_id",
    "pdbx_related_db_id",
    "ec-type",
    "uchar1",
    "yyyy-mm-dd",
    "3x4_matrix",
    "operation_expression",
    "author",
    "positive_int",
]

class DictReader:
    def __init__(self, path: str) -> None:
        self._doc = cif.read_file(path)
        self._types = set()
    def _strip_value(self, value):
        if value is None:
            return None

        return value.strip('"').strip(";").strip()
    def get_categories(self):
        block = self._doc.sole_block()

        for i in block:
            if i.frame is None:
                continue

            frame = i.frame
            type_code = self._strip_value(frame.find_value('_item_type.code'))
            cat_name = frame.find_value('_item.category_id')
            if type_code and type_code not in self._types:
                # if cat_name in TABLES:
                if type_code not in PREFILLED:
                    print(f"{frame.name}: {type_code}")
                    self._types.add(type_code)
    def find_type(self, item):
        block = self._doc.sole_block()
        print(block.find_loop_item(item))


cr = DictReader(path="./mmcif_pdbx_v50.dic")
# cr.get_categories()
cr.find_type("_chem_comp_angle.comp_id")
