#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist_dir="$repo_root/dist"
zip_path="$dist_dir/AARC_v1_0_4_arxiv.zip"
staging_dir="$dist_dir/arxiv_staging"

bash "$repo_root/scripts/write_spec_hash.sh"

python "$repo_root/scripts/gen_figures.py"

rm -rf "$staging_dir"
mkdir -p "$staging_dir/figures"

cp "$repo_root/paper/main.tex" "$staging_dir/"
cp "$repo_root/paper/arf.bib" "$staging_dir/"
cp "$repo_root/paper/spec_hash.tex" "$staging_dir/"
cp -R "$repo_root/paper/spec" "$staging_dir/spec"
cp "$repo_root/paper/figures/"*.pdf "$staging_dir/figures/"

mkdir -p "$dist_dir"
rm -f "$zip_path"

(
  cd "$staging_dir"
  zip -r "$zip_path" . >/dev/null
)

rm -rf "$staging_dir"

echo "Created $zip_path"
