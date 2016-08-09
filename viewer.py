#!/usr/bin/env python3

import sys
import os
import itertools as it
import tty
import termios
import fcntl
import struct


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
    group = []
    for line in lines:
        if line:
            group.append(line)
        else:
            if group:
                yield group
                group = []
    if group:
        yield group


def group_viewport(groups, height):
    cur_height = 0
    cur_window = []
    for group in groups:
        cur_height += len(group) + 1
        if cur_height > height:
            yield cur_window
            cur_window = []
            cur_height = len(group) + 1
        cur_window.extend(group)
        cur_window.append('')
    yield cur_window


def chunker(seq, size):
    seq = list(seq)
    yield from (seq[pos:pos + size] for pos in range(0, len(seq), size))


def two_column(*cols, full_width=80):
    width = full_width // len(cols)
    for col_lines in it.zip_longest(*cols, fillvalue=''):
        yield ''.join(c.ljust(width) for c in col_lines[:-1]) +  \
              col_lines[-1]


def terminal_size():
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return h, w


if __name__ == "__main__":
    filename = sys.argv[1]
    lines = list(map(str.strip, open(filename)))
    groups = tab_sections(lines)
    height, width = terminal_size()
    ncols = max(1, width // max(map(len, lines)))
    for cols in chunker(group_viewport(groups, height), ncols):
        os.system("clear")
        print("\n".join(two_column(*cols, full_width=width)))
        getch()
