# Utility functions
import os


def print_blocks(blocks):
    for block in blocks:
        print(block)

def print_connections(blocks):
    for block in blocks:
        for connection in block.connections:
            print(f'{block.name} -> {connection.dst}')


def remove_file(path):
    os.remove(path)
