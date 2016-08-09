#!/usr/bin/env python3

import sys
import os
import tty
import termios
import fcntl
import struct

import itertools as it
import operator as op


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def tab_sections(lines):
    """
    Group lines of text into "paragraphs"... ie: sections separated by an empty
    line
    """
    yield from map(list, map(op.itemgetter(1),
                             it.groupby(lines, bool)))


def group_viewport(groups, height):
    """
    Group sections of lines into chunks that are at most `height` long
    """
    total_height = 0
    def grouper(g):
        nonlocal total_height
        total_height += len(g) + 1
        return total_height // height
    for key, group in it.groupby(groups, grouper):
        yield list(it.chain.from_iterable(group))


def chunker(seq, size):
    seq = list(seq)
    yield from (seq[pos:pos + size] for pos in range(0, len(seq), size))


def multicolumn(*cols, full_width=80):
    """
    Take multiple lists of strings and laminate them together, side by side,
    for a multi-column view
    """
    width = full_width // len(cols)
    for col_lines in it.zip_longest(*cols, fillvalue=''):
        yield ''.join(c.ljust(width) for c in col_lines[:-1]) +  \
              col_lines[-1]


def terminal_size():
    h, w, hp, wp = struct.unpack(
        'HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
                    struct.pack('HHHH', 0, 0, 0, 0))
    )
    return h, w


if __name__ == "__main__":
    filename = sys.argv[1]
    lines = list(map(str.strip, open(filename)))
    groups = tab_sections(lines)
    height, width = terminal_size()
    ncols = max(1, width // max(map(len, lines)))
    for cols in chunker(group_viewport(groups, height), ncols):
        os.system("clear")
        print("\n".join(multicolumn(*cols, full_width=width)))
        getch()
