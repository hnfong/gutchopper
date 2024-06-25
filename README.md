# README

This repository contains scripts that download books (text) from Project
Gutenberg, and then uses LLM to "translate" the original text (which are often
old-fashioned, wordy English) into modern, concise English.

It also includes a couple books that have been translated as *.book.html.

The script "ask" is just a wrapper around llama.cpp.

To run, ensure that environment variables:

1. LLAMA_CPP_PATH points to llama.cpp's llama-cli (or main)
2. MODEL_PATH (or ~/Downloads) has the model specified in the Makefile (as of writing, Meta-Llama-3-8B-Instruct.Q5_K_M)

Then just run "make all" a couple times.

The repository name `gutchopper` relates to the fact that most of the "difficult"
work is probably figuring out how to chop up the large book into sizable chunks
that can be processed by the LLM.
