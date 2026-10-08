#!/usr/bin/env bash
# Checks every skills/<name>/SKILL.md: frontmatter present, `name` matches the
# folder, `description` is set, and relative markdown links resolve.
set -euo pipefail

cd "$(dirname "$0")/.."
status=0
fail() { echo "FAIL $1: $2" >&2; status=1; }

for dir in skills/*/; do
  dir=${dir%/}
  folder=${dir#skills/}
  file="$dir/SKILL.md"
  [[ -f $file ]] || { fail "$folder" "missing SKILL.md"; continue; }
  [[ $(head -n1 "$file") == "---" ]] || { fail "$folder" "SKILL.md must start with YAML frontmatter"; continue; }

  front=$(awk 'NR==1{next} /^---$/{exit} {print}' "$file")
  name=$(sed -n 's/^name:[[:space:]]*//p' <<<"$front" | head -n1)
  desc=$(sed -n 's/^description:[[:space:]]*//p' <<<"$front" | head -n1)

  [[ $name == "$folder" ]] || fail "$folder" "name '$name' does not match folder name"
  [[ $name =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || fail "$folder" "name must be lowercase kebab-case"
  (( ${#name} <= 64 )) || fail "$folder" "name longer than 64 characters"
  [[ -n $desc ]] || fail "$folder" "description is empty"
  (( ${#desc} <= 1024 )) || fail "$folder" "description longer than 1024 characters"

  # Paths like `workflows/foo.md` mentioned in backticks must exist.
  while read -r ref; do
    [[ -e "$dir/$ref" ]] || fail "$folder" "referenced file '$ref' not found"
  done < <(grep -oE '`(workflows|references|scripts|templates)/[^`[:space:]]+`' "$file" | tr -d '`' | sort -u)

  # Other skills it names ("the `bf-cli` skill") must exist in this repo.
  while read -r other; do
    [[ -f "skills/$other/SKILL.md" ]] || fail "$folder" "refers to the '$other' skill, which is not in skills/"
  done < <(grep -oE 'the `[a-z0-9-]+` skill' "$file" | sed -E 's/the `(.*)` skill/\1/' | sort -u)

  [[ $status -eq 0 ]] && echo "ok   $folder"
done

exit $status
