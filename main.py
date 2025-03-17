import argparse

from diac.writer import generate_fb_xml, write_to_file, generate_adapters, generate_fbn, replace_subappnetwork_in_file, \
    generate_complex_type
from radio.parser import Parser
from radio.utils import print_blocks, print_connections

def main():
    args = argparse.ArgumentParser(
        description='A command line tool to convert GNU Radio projects to Eclipse 4diac projects')
    args.add_argument('radio', type=str, help='Path to GNU Radio project file')
    args.add_argument('--diac', type=str, help='Path to Eclipse 4diac project file')
    args.add_argument('--fbn', type=str, help='Path to the 4diac function block network output directory')
    args.add_argument('--blocks', type=str, help='Path to the 4diac blocks output directory')
    args.add_argument('--types', type=str, help='Path to the 4diac types output directory')
    args.add_argument('--rules', required=False, type=str, help='Path to the rules file')
    args = args.parse_args()

    print("Reading GNU Radio project file...\n=====================")
    print(args.radio + "\n")
    parser = Parser(args.radio)
    parsed = parser.parse()
    print("\nConnections:\n=====================")
    print_connections(parsed)


    print("\nSetting up 4diac types and adapters...\n=====================")
    generate_complex_type(args.types)
    for block in parsed:
        if block.type == "complex":
            generate_adapters(args.types, "COMPLEX")
        if block.type == "float":
            generate_adapters(args.types, "REAL")


    print("\nGenerating 4diac FB interface definition...\n=====================")
    function_blocks = []
    function_blocks_names = []
    file_names = []
    for block in parsed:
        fb, fb_name = generate_fb_xml(block)
        function_blocks.append(fb)
        function_blocks_names.append(fb_name)
        file_names.append(args.blocks + "/fb_" + block.id + "_gen" + ".fbt")

    print("\nWriting Function block to file...\n=====================")
    for fb, file_name in zip(function_blocks, file_names):
        write_to_file(file_name, fb)

    print("\nGenerating 4diac FB network...\n=====================")
    fbn_file_content = generate_fbn(parsed, function_blocks_names)

    print("\nWriting Function block network to file...\n=====================")
    file_name = args.fbn + "/fbn_gen.sys"
    write_to_file(file_name, fbn_file_content)

    print("\nReplacing the function block network in the 4diac project file...\n=====================")
    replace_subappnetwork_in_file(args.diac, fbn_file_content)


if __name__ == '__main__':
    main()
