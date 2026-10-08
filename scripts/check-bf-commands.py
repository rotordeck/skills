"""Check that every `bf ...` command in the skills exists in the bf CLI.

Usage: npx --yes @rotordeck/bf schema --json | python3 scripts/check-bf-commands.py [skills-dir]

Looks at inline code and fenced code blocks. Shorthand like `bf pid get|set`
or `bf pid get/set` is expanded and each alternative is checked. Options are
checked against the command's own options plus bf's global options.
"""
import json
import pathlib
import re
import sys

GLOBAL_OPTIONS = {"-p", "--port", "--baud", "--timeout", "--json", "-q", "--quiet", "-v", "--verbose", "-h", "--help"}

commands = {}
for c in json.load(sys.stdin)["data"]:
    flags = set()
    for o in c["options"]:
        for f in re.split(r"[ ,]+", o["flags"]):
            if f.startswith("-"):
                flags.add(f)
                if f.startswith("--no-"):
                    flags.add("--" + f[5:])
    commands[tuple(c["command"].split()[1:])] = flags
groups = {words[0] for words in commands}


def code_snippets(text):
    for m in re.finditer(r"```[^\n]*\n(.*?)```", text, re.S):
        yield from m.group(1).splitlines()
    for m in re.finditer(r"`([^`\n]+)`", re.sub(r"```.*?```", "", text, flags=re.S)):
        yield m.group(1)


def invocations(snippet):
    """Yield the tokens after each `bf` in a shell-ish snippet."""
    snippet = snippet.split(" #")[0].replace("\\|", "\0")
    for part in re.split(r"[|;&]|\$\(", snippet):
        toks = part.replace("\0", "|").split()
        if "bf" in toks:
            yield toks[toks.index("bf") + 1:]


def resolve(words):
    """Longest command matching the leading words, or None."""
    for n in range(min(3, len(words)), 0, -1):
        if tuple(words[:n]) in commands:
            return tuple(words[:n])
    return None


def is_group(words):
    return any(k[: len(words)] == tuple(words) for k in commands)


problems = []
checked = 0
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "skills")
for md in sorted(root.rglob("*.md")):
    for snippet in code_snippets(md.read_text()):
        for toks in invocations(snippet):
            if not toks or toks[0].startswith(("-", "<")) or toks[0] == "...":
                continue
            words = [t for t in toks if not t.startswith("-")]
            if words[0] not in groups:
                problems.append(f"{md}: unknown command 'bf {words[0]}'")
                continue
            # expand `get|set` / `get/set` shorthand in the subcommand position
            if len(words) > 1 and re.fullmatch(r"[a-z-]+([|/][a-z -]+)+", words[1]):
                for alt in re.split(r"[|/]", words[1]):
                    checked += 1
                    if not is_group([words[0], *alt.split()]):
                        problems.append(f"{md}: unknown command 'bf {words[0]} {alt}'")
                continue
            match = resolve(words)
            if match is None:
                if len(words) == 1 or words[1] in ("...", "<cmd>"):
                    continue  # bare group mention like `bf serial`
                problems.append(f"{md}: unknown command 'bf {' '.join(words[:3])}'")
                continue
            checked += 1
            for t in toks:
                flag = t.split("=")[0]
                if flag.startswith("-") and flag not in GLOBAL_OPTIONS and flag not in commands[match]:
                    problems.append(f"{md}: 'bf {' '.join(match)}' has no option {flag}")

for p in sorted(set(problems)):
    print("FAIL", p, file=sys.stderr)
print(f"checked {checked} bf commands, {len(set(problems))} problems")
sys.exit(1 if problems else 0)
