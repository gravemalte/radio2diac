from gnuradio import blocks
import inspect
from collections import defaultdict

def categorize_blocks_by_type():
    """
    Categorizes all blocks in the blocks module of GNU Radio into predefined types.
    """
    # Predefined categories based on typical block purposes
    predefined_categories = {
        "Audio": ["audio_source", "audio_sink"],
        "Boolean Operators": ["and_bb", "or_bb", "xor_bb", "not_bb"],
        "Byte Operators": ["pack_k_bits_bb", "unpack_k_bits_bb"],
        "Filters": ["fir_filter_ccf", "iir_filter_ffd", "band_pass_filter"],
        # Add more categories and blocks as needed
    }


    default_category = "Miscellaneous"

    categories = defaultdict(list)

    for name, obj in inspect.getmembers(blocks):
        if inspect.isclass(obj) or inspect.isfunction(obj):
            found = False
            for category, block_list in predefined_categories.items():
                if name in block_list:
                    categories[category].append(name)
                    found = True
                    break

            if not found:
                categories[default_category].append(name)

    return categories

if __name__ == "__main__":
    block_categories = categorize_blocks_by_type()

    print("Blocks grouped by categories:")
    for category, block_names in block_categories.items():
        print(f"\nCategory: {category}")
        for block in sorted(block_names):
            print(f"  - {block}")
