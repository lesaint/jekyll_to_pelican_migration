#!/bin/env python3

import pathlib
import sys
import shutil

HELP = """Usage: migrate_md.py pattern

pattern: pattern relative to the current directory, ending with ".md" (eg. *.md, foo.md)
"""


class LineProcessor:
    def process_line(self, line_number: int, line: str) -> (bool, str | None):
        return False, line


class HeaderTransformer(LineProcessor):
    def __init__(self):
        self.primed: bool = False
        self.completed: bool = False
        self.content: dict[str: str | list[str]] = {}
        self.current_tag: str | None = None

    def _process_tag(self, tag: str, value: str) -> None:
        # force lower case to ease search
        tag = tag.strip().lower()
        # remove extra spaces but most importantly, remove new line char
        value = value.strip()
        self.current_tag = tag
        if value:
            self.content[self.current_tag] = value

    def _process_item(self, item: str):
        # remove extra spaces but most importantly, remove new line char
        item = item.strip()
        if not self.current_tag:
            raise RuntimeError("item found while there is no current tag")
        if self.current_tag in self.content:
            if isinstance(self.content[self.current_tag], str):
                raise RuntimeError(f"item found but tag {self.current_tag} already has a value")
            self.content[self.current_tag].append(item)
        else:
            self.content[self.current_tag] = [item]

    def _new_header_content(self) -> list[str]:
        res = []
        for k, v in self.content.items():
            match k:
                case "title":
                    res.append("Title: " + v.strip('"'))
                case "tags":
                    res.append("Tags: " + ", ".join(v))
                case "description":
                    res.append("Summary: " + v)

        return res

    def process_line(self, line_number: int, line: str) -> (bool, str | None):
        if line_number == 0 and line == "---\n":
            self.primed = True
            return True, None

        if not self.primed or self.completed:
            return False, line

        try:
            colon_index = line.index(":")
            if colon_index > 1:
                self._process_tag(line[:colon_index], line[colon_index+1:])
            return True, None
        except ValueError:
            pass

        if line.lstrip().startswith("- "):
            self._process_item(line[line.index("-")+1:].strip())
            return True, None

        if line == "---\n":
            self.completed = True
            new_lines = self._new_header_content()
            if new_lines:
                return True, "\n".join(new_lines) + "\n"
            return True, None

        return False, line


class CodeBlocks(LineProcessor):
    _opening_start = "{% highlight"
    _opening_end = "%}"

    def process_line(self, line_number: int, line: str) -> (bool, str | None):
        try:
            s = line.index(self._opening_start)
            e = line.index(self._opening_end, s + len(self._opening_start))
            language = line[s+len(self._opening_start):e].strip()
            return True, f"```{language}\n"
        except ValueError:
            pass

        if "{% endhighlight %}" in line:
            return True, "```\n"

        return False, line


class Toc(LineProcessor):
    def process_line(self, line_number: int, line: str) -> (bool, str | None):
        if "* Table of Contents" in line:
            return True, None
        if "{:toc}" in line:
            return True, "[TOC]\n"

        return False, line


def _new_processor():
    return [
        HeaderTransformer(),
        CodeBlocks(),
        Toc(),
    ]


def migrate(md_file):
    print(f"Migrating {md_file}...")

    backup_file = md_file.parent / f"{md_file.stem}.md.backup"

    if not backup_file.exists():
        shutil.copy(md_file, backup_file)

    processors = _new_processor()
    with backup_file.open('r') as f_backup, md_file.open('w') as f_md:
        for n,l in enumerate(f_backup):
            modified = False
            for p in processors:
                modified, new_line = p.process_line(n, l)
                # stops at 1st processor modifying the line
                if modified:
                    if new_line:
                        f_md.write(new_line)
                    break
            # if no processor modified the line, keep it
            if not modified:
                f_md.write(l)


def main():
    if len(sys.argv) != 2:
        print(HELP)
        exit(1)

    pattern = sys.argv[1]
    if not pattern.endswith(".md"):
        print(HELP)
        exit(1)

    for f in pathlib.Path().glob(pattern):
        migrate(f)


if __name__ == "__main__":
    main()
