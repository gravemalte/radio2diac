import os
import yaml

def extract_ids_and_categories_from_yaml(directory):
    """
    Extracts `id` and `category` from YAML files in the specified directory.

    :param directory: Path to the directory containing YAML files.
    :return: A tuple containing two lists: unique ids and unique categories.
    """
    ids = set()
    categories = set()

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        if os.path.isfile(filepath) and filepath.endswith('.yml'):
            try:
                with open(filepath, 'r') as file:
                    data = yaml.safe_load(file)

                    # Check for `id` and `category` fields
                    block_id = data.get('id', None)
                    category = data.get('category', None)

                    if block_id:
                        ids.add(block_id)
                    if category:
                        categories.add(category)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

    return sorted(ids), sorted(categories)

if __name__ == "__main__":
    yaml_directory = "/usr/share/gnuradio/grc/blocks"

    if os.path.exists(yaml_directory):
        ids, categories = extract_ids_and_categories_from_yaml(yaml_directory)

        print("Unique IDs:")
        for block_id in ids:
            print(block_id)

        print("\nUnique Categories:")
        for category in categories:
            print(category)
    else:
        print(f"Directory does not exist: {yaml_directory}")
