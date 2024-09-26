Here is the Markdown documentation for the provided CLI:

# CLI Documentation for `mmcif_db_tool`

This command-line interface (CLI) processes categories from an MMCIF dictionary and provides options for including/excluding certain items or categories. The user can choose between two different models: `orm` and `core`.

## Command

```bash
mmcif-db-tool [OPTIONS] MMCIF_DICTIONARY
```

### Arguments

- **`MMCIF_DICTIONARY`**: The path to the MMCIF dictionary file. This argument is required.

### Options

- **`--categories`**: A comma-separated list of categories to be processed (e.g., `'chem_comp,chem_comp_atom'`).
- **`--categories-file`**: The path to a file containing the list of categories to be processed. This file should have one category per line.
- **`--model`**: Choose between the `orm` and `core` models for data processing. The default is `orm`.
- **`--include-items-file`**: Path to the file containing the list of categories and items to be included. The file should have one `category_name.item_name` per line. If this option is used, any item not listed in the file will be ignored. Cannot be used together with `--exclude-items-file`.
- **`--exclude-items-file`**: Path to the file containing the list of categories and items to be excluded. The file should have one `category_name.item_name` per line. If this option is used, only the items not in this list will be processed. Cannot be used together with `--include-items-file`.
- **`--output-file`**: An optional file path where the models will be printed. If omitted, models will be printed on the screen.

### Examples

#### Example 1: Basic usage with categories option
```bash
process_categories my_mmcif_dictionary.cif --categories "chem_comp,chem_comp_atom"
```
This command processes the `chem_comp` and `chem_comp_atom` categories from the provided MMCIF dictionary.

#### Example 2: Using categories from a file
```bash
process_categories my_mmcif_dictionary.cif --categories-file categories_list.txt
```
This command processes the categories listed in `categories_list.txt`.

#### Example 3: Choosing the model type
```bash
process_categories my_mmcif_dictionary.cif --categories "chem_comp,chem_comp_atom" --model "core"
```
This command processes the MMCIF dictionary using the `core` model instead of the default `orm` model.

#### Example 4: Including specific items using a file
```bash
process_categories my_mmcif_dictionary.cif --categories "chem_comp,chem_comp_atom" --include-items-file include_items.txt
```
This command processes only the items listed in `include_items.txt`. An example file would be:

```
chem_comp.id
chem_comp.description
chem_comp_atom.comp_id
another_category.another_item
```

In this case, the tool will only create models for the items `chem_comp.id`, `chem_comp.description` and `chem_comp_atom.comp_id`. Since `another_category` is not on the list of categories, it's ignored.

#### Example 5: Excluding specific items using a file
```bash
process_categories my_mmcif_dictionary.cif --categories "chem_comp,chem_comp_atom" --exclude-items-file exclude_items.txt
```
This command processes all categories and items except those listed in `exclude_items.txt`. An example file would be:

```
chem_comp.id
chem_comp.description
chem_comp_atom.comp_id
```

In this case, the tool will only create models for all the other items in `chem_comp`, and `chem_comp_atom`.

#### Example 6: Saving the output to a file
```bash
process_categories my_mmcif_dictionary.cif --categories "chem_comp,chem_comp_atom" --output-file processed_data.cif
```
This command saves the processed data to `processed_data.cif`.

### Notes
- The `--include-items-file` and `--exclude-items-file` options are mutually exclusive, meaning they cannot be used together in the same command.
- The user must provide either `--categories` or `--categories-file`.

### Mapping

For table info, the mapping below was used:

- description: _category.description
- name: _category.id
- indexes: _category_key.name

For column info:

- name: _item.name
- type: _item_type.code 
- nullable: _item.mandatory_code
- default value: _item_default.value
- foreign key: _item_linked.child_name (not implemented)
