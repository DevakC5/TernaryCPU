#!/usr/bin/env perl

$pdf_mode = 1;                         # pdflatex
$bibtex_use = 2;                       # run bibtex when needed
$clean_ext = 'aux log out toc bbl blg fls fdb_latexmk run.xml';

# Use bibtex (not biber) for bibliography
$bibtex = 'bibtex';
