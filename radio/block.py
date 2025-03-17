# Data structure for a block in GNU Radio

class Block:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.connections = []
        self.parameters = {}
        self.type = None
        self.has_inputs = False
        self.has_outputs = False

    def add_connection(self, connection):
        self.connections.append(connection)

    def add_parameter(self, key, value):
        self.parameters[key] = value

    def change_parameter(self, key, value):
        self.parameters[key] = value

    def __str__(self):
        return f'Block({self.name}, {self.id}, {self.connections}, {self.parameters})'

    def __repr__(self):
        return str(self)


def analyze_blocks(blocks):
    """
    Analyze blocks to set their input/output attributes based on connections.

    :param blocks: A list of Block objects.
    """
    # Build dictionaries to look up blocks quickly
    block_dict = {block.name: block for block in blocks}

    # Iterate through all connections to mark blocks with inputs and outputs
    for block in blocks:
        for conn in block.connections:
            # Source of a connection has outputs
            if conn.src in block_dict:
                block_dict[conn.src].has_outputs = True
            # Destination of a connection has inputs
            if conn.dst in block_dict:
                block_dict[conn.dst].has_inputs = True


class Connection:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __str__(self):
        return f'Connection({self.src}, {self.dst})'

    def __repr__(self):
        return str(self)

