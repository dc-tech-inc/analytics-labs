.PHONY: all python marketing r clean

# One command for everything that runs without R: `make`
all: python marketing

python:
	cd python && pip install -e ".[dev]" && ruff check . && ruff format --check . && pytest

marketing:
	cd marketing-ga4-synthetic && pip install -e ".[dev]" && ruff check . && pytest && ga4-synth generate && ga4-synth report
	@echo "open marketing-ga4-synthetic/dist/index.html"

# Needs R (>= 4.1) with the packages in r-quarto/DESCRIPTION, and Quarto
r:
	cd r-quarto && Rscript tests/testthat.R && quarto render report.qmd

clean:
	rm -rf outputs marketing-ga4-synthetic/data marketing-ga4-synthetic/dist r-quarto/report.html
