#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist_dir="$repo_root/dist"
zip_path="$dist_dir/ARF_v1_0_4_arxiv.zip"
staging_dir="$dist_dir/arxiv_staging"
tmp_dir=""

"$repo_root/scripts/write_spec_hash.sh"

rm -rf "$staging_dir"
mkdir -p "$staging_dir/figures"
mkdir -p "$staging_dir/spec"

cp "$repo_root/paper/main.tex" "$staging_dir/"
cp "$repo_root/paper/arf.bib" "$staging_dir/"
cp "$repo_root/paper/spec_hash.tex" "$staging_dir/"
cp "$repo_root/paper/figures/arf_lifecycle.pdf" "$staging_dir/figures/"
cp "$repo_root/paper/figures/arf_architecture.pdf" "$staging_dir/figures/"
cp "$repo_root/spec/"*v1_0_4* "$staging_dir/spec/"

mkdir -p "$dist_dir"
rm -f "$zip_path"

(
  cd "$staging_dir"
  find . -type f -print | LC_ALL=C sort | zip -X -@ "$zip_path" >/dev/null
)

tmp_dir="$(mktemp -d)"
unzip -q "$zip_path" -d "$tmp_dir"

if [[ ! -f "$tmp_dir/main.tex" ]]; then
  echo "Smoke test failed: main.tex missing at zip root." >&2
  exit 1
fi

if [[ ! -f "$tmp_dir/figures/arf_lifecycle.pdf" || ! -f "$tmp_dir/figures/arf_architecture.pdf" ]]; then
  echo "Smoke test failed: figures are missing from zip." >&2
  exit 1
fi

if [[ ! -f "$tmp_dir/spec/ARF_STATE_VECTOR.schema.v1_0_4.json" ]]; then
  echo "Smoke test failed: spec artifacts missing from zip." >&2
  exit 1
fi

rm -rf "$tmp_dir"
rm -rf "$staging_dir"

echo "Created $zip_path"
