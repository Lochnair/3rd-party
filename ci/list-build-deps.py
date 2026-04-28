#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <pspec.xml>", file=sys.stderr)
        return 1

    pspec_path = sys.argv[1]
    root = ET.parse(pspec_path).getroot()

    deps: list[str] = []
    seen: set[str] = set()

    for dep in root.findall(".//BuildDependencies/Dependency"):
        name = (dep.text or "").strip()
        if name and name not in seen:
            seen.add(name)
            deps.append(name)

    for dep in deps:
        print(dep)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())