# Makefile for Trinary LaTeX research document
#
# Targets:
#   make          Build PDF (via latexmk)
#   make clean    Remove all build artefacts
#   make watch    Continuously rebuild on file changes

LATEXMK = latexmk
FLAGS   = -pdf -interaction=nonstopmode -halt-on-error
MAIN    = main

.PHONY: all clean watch

all:
	$(LATEXMK) $(FLAGS) $(MAIN)

clean:
	$(LATEXMK) -C $(MAIN)
	rm -f $(MAIN).bbl $(MAIN).run.xml $(MAIN)-blx.bib

watch:
	$(LATEXMK) $(FLAGS) -pvc $(MAIN)
