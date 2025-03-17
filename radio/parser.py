# Parse the yaml GNU Radio project file

import yaml
from radio.block import Connection, Block, analyze_blocks


def set_sample_rate(blocks, sample_rate):
    for block in blocks:
        if 'samp_rate' in block.parameters:
            block.parameters['samp_rate'] = sample_rate
            # check if the block has a parameter called "sample_rate" and set it to the sample rate
        if 'sample_rate' in block.parameters:
            block.parameters['sample_rate'] = sample_rate
    return blocks


class Parser:
    def __init__(self, path):
        self.path = path

    def parse(self):
        with open(self.path, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            blocks = []
            sample_rate = None

            for block in data['blocks']:
                # Skip the sample block but save the sample rate
                if block['name'] == 'samp_rate':
                    sample_rate = block['parameters']['value']
                    continue
                b = Block(block['name'], block['id'])
                for key, value in block['parameters'].items():
                    b.add_parameter(key, value)
                blocks.append(b)

            for connection in data['connections']:
                c = Connection(connection[0], connection[2])
                for block in blocks:
                    if block.name == 'samp_rate':
                        continue
                    if block.name == c.src:
                        block.add_connection(c)
                        break
            analyze_blocks(blocks)
            blocks = self.set_type(blocks)
            blocks = set_sample_rate(blocks, sample_rate)
            return self.remove_advanced_tab(blocks)

    # Remove alias, affinity, minoutbuf, maxoutbuf and comment parameters
    def remove_advanced_tab(self, blocks):
        for block in blocks:
            for key in ['alias', 'affinity', 'minoutbuf', 'maxoutbuf', 'comment']:
                if key in block.parameters:
                    del block.parameters[key]
        return blocks

    # There are different types of block in GNU Radiom this method set the type of the block
    def set_type(self, blocks):
        for block in blocks:
            if 'type' in block.parameters:
                block.type = block.parameters['type']
                del block.parameters['type']
        return blocks
