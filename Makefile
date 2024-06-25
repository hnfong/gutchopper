DOWNLOADS:=$(shell cat urls.dat | while read -r line; do echo $$(basename $$line).gz; done)
CHOPPED_TEXT_GENERATIONS=$(shell ls outputs/*.txt | while read -r line; do echo $${line}.out; done)
EXTRACT_BOOKS=$(shell cat urls.dat | while read -r line; do echo $$(basename $$line).book.html; done)
MODEL=Meta-Llama-3-8B-Instruct.Q5_K_M

all: chop

chop: $(DOWNLOADS)
	mkdir -p outputs/
	for ff in *.txt.gz; do python3 gutchopper.py -t modern_english.template -f "$$ff" -o ./outputs/; done
	echo "All done"

gen: $(CHOPPED_TEXT_GENERATIONS)
	echo "All done"

book: $(EXTRACT_BOOKS)
	echo "All done"

%.txt.gz: # urls.dat -- we don't want to re-download the file every time urls.dat changes
	# Remove .gz from the filename and grep from urls.dat for the url
	curl -o "$(basename $@)" $(shell grep -F $(basename $@) urls.dat)
	gzip "$(basename $@)"

outputs/%.txt.out: outputs/%.txt
	[ -f "$@" ] || ./ask -X "-BEGIN REWRITE-" -c 6144 -m $(MODEL) -f "$<" -o '{f}.out'
	# Validate  by checking whether there is some "END REWRITE" in the output file
	# Workaround bugs that include (but not limited to) https://github.com/ggerganov/llama.cpp/issues/8098
	# -b is for #8098 above, and increased temp works around any issues with the model itself
	while ! grep -qE "^-END REWRITE" "$@"; do echo "Problem encountered, trying again in 3 seconds"; sleep 3; rm -vf "$@"; ./ask -k -t 0.5 -X "-BEGIN REWRITE-" -c 6144 -m $(MODEL) -f "$<" -o '{f}.out' -P "-b 2052"; done


%.book.html:
	# Extract the book from the .txt file
	python3 extract_book.py "$@"
