#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "\${BASH_SOURCE[0]}")/.." && pwd)"

bash "$repo_root/scripts/write_spec_hash.sh"

rm -f "$repo_root/paper/figures/aarc_"*.pdf
python "$repo_root/scripts/gen_figures.py"

if ! command -v pdflatex >/dev/null 2>&1; then
  echo "pdflatex is required for the publication build." >&2
  exit 127
fi
if ! command -v bibtex >/dev/null 2>&1; then
  echo "bibtex is required for the publication build." >&2
  exit 127
fi

pushd "$repo_root/paper" >/dev/null

rm -f main.aux main.bbl main.blg main.log main.out main.pdf
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

test -s main.pdf

popd >/dev/null

echo "Built paper/main.pdf"
