#!/usr/bin/env python
"""
Take the first argument, eg. abc.txt.book, find the chunks in <dir>/abc.txt.*, and extract them into the book.

The chunks will contain <BEGIN OUTPUT> and <DONE> markerrs, we only want the text between them.
"""

import os
import sys
import getopt
import re

def main():
    opts_list, args = getopt.getopt(sys.argv[1:], "hd:")
    opts = dict(opts_list)

    if '-h' in opts:
        print(__doc__)
        return

    if len(args) != 1:
        print("Invalid usage.")
        print(__doc__)
        sys.exit(1)

    bookname = args[0]
    bookname = os.path.basename(bookname)
    bookname = re.sub(r'\.book(\.html)?$', '', bookname)

    output_path = args[0]

    chunkdir = opts.get('-d', 'outputs/')
    chunkfiles = sorted(os.listdir(chunkdir))
    chunkfiles = [f for f in chunkfiles if f.startswith(bookname) and f.endswith('.out')]

    orig_chunks = []
    book_chunks = []
    for chunkfile in chunkfiles:
        chunkfile = os.path.join(chunkdir, chunkfile)
        print("Processing %s ..." % chunkfile)
        # book_chunks.append("<chunk %s>" % chunkfile)
        with open(chunkfile) as f:
            lines = f.readlines()
            start_from = 0
            N = len(lines)

            # Extract the original text (from the prompt)
            orig_started = False
            orig = []
            for line in lines:
                if orig_started:
                    if line.strip() == '```': # End when we see the second ```
                        break
                    if line.strip() == "" and (len(orig) > 0 and orig[-1].strip() != ""):
                        orig.append("<p>")
                    orig.append(line)
                if line.strip() == '```':
                    orig_started = True
            orig_chunks.append("".join(orig))

            for i, line in enumerate(reversed(lines)):
                if 'BEGIN REWRITE' in line:
                    start_from = N - i
                    break
            else:
                print("Warning: %s does not have <BEGIN REWRITE> marker" % chunkfile)

            book = []
            for line in lines[start_from:]:
                if 'END REWRITE' in line:
                    break
                if line.strip() == "" and (len(book) > 0 and book[-1].strip() != ""):
                    book.append("<p>")
                book.append(line)
            else:
                print("Warning: %s does not have <END REWRITE> marker" % chunkfile)
            book_chunks.append("".join(book))

    bookfile = os.path.join(output_path)
    with open(bookfile, 'w') as f:
        assert len(orig_chunks) == len(book_chunks)
        f.write("""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body { font-family: serif; font-size: 20px; line-height: 1.3; margin: 1em; text-align: justify; background-color: #f8f9fa; /* this color is light gray */ }
div.creator_notes { font-size: 16px; color: #663; }
div.original_text { display: none; color: #888; font-style: italic; }
div.processed_text { display: block; }
div.show_original { display: block; margin-top: 2em; }
div.show_original a {
    /* light blue, sky color */ color: #007bff;
    /* no underline */ text-decoration: none;
    font-size: 16px; }
</style>
<body>
<div class="creator_notes">
This is a book generated by AI, converting old fashioned English to concise modern English to make it easier for modern readers to consume the text. The code can be found (TODO). The original text can be shown upon clicking the [Show original] button. The original content is downloaded from Project Gutenberg ({bookname}), and is in the public domain (as far as we can tell), and we disclaim any copyrights in the generated text.
</div>
""".replace("{bookname}", bookname))
        # If there is a bookname.prefix, include its contents
        prefixfile = bookname + ".prefix"
        if os.path.exists(prefixfile):
            f.write(open(prefixfile).read())

        for idx, (orig, book) in enumerate(zip(orig_chunks, book_chunks)):
            f.write(f"""<div class="show_original" id="btn_{idx}"><a class="show_original" href="#" onclick="return false;">[Show original]</a></div>\n""")
            f.write(f"""<div class="original_text" id="orig_{idx}">{orig}</div>\n""")
            f.write(f"""<div class="processed_text" id="book_{idx}">{book}</div>\n""")
        f.write("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Show original text
    var show_original = document.querySelectorAll('a.show_original');
    for (var i = 0; i < show_original.length; i++) {
        show_original[i].addEventListener('click', function(e) {
            var idx = this.parentElement.id.split('_')[1];
            var orig = document.getElementById('orig_' + idx);
            var book = document.getElementById('book_' + idx);
            if (orig.style.display === 'block') {
                orig.style.display = 'none';
                this.innerText = '[Show original]';
            } else {
                orig.style.display = 'block';
                this.innerText = '[Hide original]';
            }

            // Disable the link
            e.preventDefault();
        });
    }
});
</script>
</body>
</html>
""")

    print("Extracted book: %s" % output_path)

if __name__ == '__main__':
    main()

