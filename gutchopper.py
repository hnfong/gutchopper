#!/usr/bin/env python3

"""
This script takes a file (currently Gutenberg books) and chops it into pieces of a specified size along chapter/paragraph boundaries.

Usage:

gutchopper.py

-f <file>       The file to chop
-s <size>       The size of each chunk in "words" (default 1200)
-o <output_dir> The output directory (default ".")
-c <type>       The type of file to chop (default "gutenberg")
-t <template>   The template file to use. The content of the template file will be inserted at the marker {CHOPPER_CONTENT}

"""

import re
import os
import sys
import getopt

class Default:

    # When this is true, we are in a starting block. This means that we should emit the buffer before taking in the new line
    def block_start(line, buffer):
        assert False

    # When this is true, we are in a ending block. This means that we should emit the buffer after taking in the new line
    def block_end(line, buffer):
        assert False

    # Can emit (returns 1 if inclusive, 2 if exclusive, None if not a start marker)
    def can_emit(line, buffer):
        assert None

    # Start Marker (returns 1 if inclusive, 2 if exclusive, None if not a start marker)
    def start_marker(line):
        return None

    def __init__(self, f, opts):
        self.f = f
        self.opts = opts
        self.buffer = []
        self.block = []
        self.in_block = False
        self.in_start_block = False
        self.in_end_block = False
        self.emit_count = 0
        self.started = False
        self.rough_word_count = 0

    def chop(self):

        while line := self.f.readline():
            if not self.started:
                if which := self.start_marker(line):
                    self.started = True
                    if which == 2:
                        continue # Skip this line since start marker returned "2" so it is exclusive

                continue

            if self.block_start(line):
                if self.buffer:
                    self.emit()

            self.buffer.append(line)
            self.rough_word_count += len(line.split())

        self.emit()

    def emit_inner(self, fr, to):
        output_dir = self.opts.get("-o", ".")
        original_file = os.path.basename(self.opts.get("-f"))
        count_string = "%03d" % self.emit_count
        template_path = self.opts.get("-t", None)
        if template_path:
            template = open(template_path, "rt").read()
        else:
            template = "{CHOPPER_CONTENT}"

        print('writing', output_dir + os.path.sep + f"{original_file}_{count_string}.txt")
        with open(output_dir + os.path.sep + f"{original_file}_{count_string}.txt", "w") as f:
            if fr is None:
                data = self.buffer
            else:
                # Note: to can be None, we rely on the fact that None is treated as the end of the list
                data = self.buffer[fr:to]
            f.write(template.replace("{CHOPPER_CONTENT}", "".join(data)))
        self.emit_count += 1


    def emit(self):
        block_size_limit = int(self.opts.get("-s", 1200))
        if self.rough_word_count > block_size_limit:
            # Try to split the current block into roughly equal parts
            import math
            num_splits = self.rough_word_count * 1.0 / block_size_limit
            # Round up
            num_splits = int(math.ceil(num_splits))
            split_size = self.rough_word_count // num_splits
            # Loop through the buffer and call emit_inner when we reach the split size
            z = 0
            last_to = 0
            for i, line in enumerate(self.buffer):
                z += len(line.split())
                if z >= split_size and (which := self.can_emit(line)):
                    # Include the line if the can_emit function returns 1
                    to_delta = 0 if which == 2 else 1
                    self.emit_inner(fr=last_to, to=i+to_delta)
                    last_to = i+to_delta
                    z = 0

            self.emit_inner(fr=last_to, to=None)

        elif self.rough_word_count < int(self.opts.get('-x', 100)):
            return

        else:
            self.emit_inner(fr=None, to=None)

        self.buffer = []
        self.rough_word_count = 0


class Gutenberg(Default):
    def block_start(self, line):

        # Wealth of nations
        if line.startswith("CHAPTER ") and self.buffer and self.buffer[-1].strip() == "":
            return True

        # Pride and Prejudice
        if line.startswith("Chapter ") and self.buffer and self.buffer[-1].strip() == "":
            return True


        # This usually is a chapter heading, like "                       CHAPTER I."
        if not line.startswith("              "):
            return False

        # Check whether we have a word that starts with lowercase, eg '\s[a-z]'
        if re.search(r"\s[a-z]", line):
            return False

        return True


    def block_end(self, line):
        return False

    def can_emit(self, line):
        if line.strip() == "":
            return 1 # Can emit, inclusive

    def start_marker(self, line):
        if '----------------------------' in line:
            return 2 # This is a start marker, but do not include this line

        if 'START OF THE PROJECT GUTENBERG EBOOK' in line:
            return 2

        if line.strip() == 'Contents':
            return 2

def smart_open(file_path):
    if file_path.endswith(".gz"):
        import gzip
        return gzip.open(file_path, "rt")
    elif file_path.endswith(".bz2"):
        import bz2
        return bz2.open(file_path, "rt")
    else:
        return open(file_path, "rt")


def main():
    opts_list, args = getopt.getopt(sys.argv[1:], "f:s:o:c:x:t:")
    opts = dict(opts_list)

    if "-f" not in opts:
        print(__doc__)
        sys.exit(2)

    file_path = opts.get("-f")
    assert os.path.exists(file_path)

    block_type = opts.get("-c", "gutenberg")
    block_classes = {
        "gutenberg": Gutenberg,
    }
    block_class = block_classes[block_type]

    with smart_open(file_path) as f:
        chopper = block_class(f, opts)
        chopper.chop()


if __name__ == "__main__":
    main()
