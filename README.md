# README

This repository contains scripts that download books (text) from Project
Gutenberg, and then uses LLM to "translate" the original text (which are often
old-fashioned, wordy English) into modern, concise English.

It also includes a couple books that have been translated as *.book.html.

The script "ask" is just a wrapper around llama.cpp.

To run, ensure that environment variables:

1. LLAMA_CPP_PATH points to llama.cpp's llama-cli (or main)
2. MODEL_PATH (or ~/Downloads) has the model specified in the Makefile (as of writing, Meta-Llama-3-8B-Instruct.Q5_K_M)

Then just run "make chop" "make gen" "make book"

If you want to add books, you'll need to update `gutchopper.py` to make it
correctly chop up your chapters, see commit 279d1f6 for an example of what you
may need to change.

The repository name `gutchopper` relates to the fact that most of the "difficult"
work is probably figuring out how to chop up the large book into sizable chunks
that can be processed by the LLM.

## Examples / Samples

- [Pride and Prejudice - Jane Austen](https://hnfong.github.io/gutchopper/1342-0.txt.book.html)
- [An Inquiry into the Nature and Causes of the Wealth of Nations - Adam Smith](https://hnfong.github.io/gutchopper/3300-0.txt.book.html)
- [The End of the Middle Ages - A. Mary F. Robinson](https://hnfong.github.io/gutchopper/53475-0.txt.book.html)

