#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck disable=SC1091
source "$repo_root/SPEC_VERSION"

version_slug="${AARC_VERSION//./_}"
dist_dir="$repo_root/dist"
zip_path="$dist_dir/AARC_v${version_slug}_arxiv.zip"
staging_dir="$dist_dir/arxiv_staging"

bash "$repo_root/scripts/write_spec_hash.sh"
rm -f "$repo_root/paper/figures/aarc_"*.pdf
python "$repo_root/scripts/gen_figures.py"

rm -rf "$staging_dir"
mkdir -p "$staging_dir/figures" "$staging_dir/spec"

cp "$repo_root/paper/main.tex" "$staging_dir/"
cp "$repo_root/paper/aarc.bib" "$staging_dir/"
cp "$repo_root/paper/spec_hash.tex" "$staging_dir/"
cp "$repo_root/paper/figures/"*.pdf "$staging_dir/figures/"

mapfile -d '' spec_files < <(
  find "$repo_root/spec" -maxdepth 1 -type f -name "*v${version_slug}*" -print0 | sort -z
)
if [[ ${#spec_files[@]} -eq 0 ]]; then
  echo "No normative v$AARC_VERSION specs found for arXiv bundle." >&2
  exit 1
fi
cp "${spec_files[@]}" "$staging_dir/spec/"

mkdir -p "$dist_dir"
rm -f "$zip_path"
(
  cd "$staging_dir"
  zip -r "$zip_path" . >/dev/null
)
rm -rf "$staging_dir"

test -s "$zip_path"
echo "Created $zip_path from normative AARC v$AARC_VERSION specs"
