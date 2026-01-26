#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "$repo_root/scripts/write_spec_hash.sh"

rm -f "$repo_root/paper/figures/aarc_"*.pdf
rm -f "$repo_root/paper/figures/arf_"*.pdf

python "$repo_root/scripts/gen_figures.py"

if ! command -v pdflatex >/dev/null; then
  echo "pdflatex missing; skipping PDF build."
  exit 0
fi

pushd "$repo_root/paper" >/dev/null

pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main || true
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

popd >/dev/null

echo "Built paper/main.pdf"
