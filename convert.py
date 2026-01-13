#!/usr/bin/env python3

import json
import sys
import pathlib
import re
import pandas as pd


PHASE_PATTERNS = {
    "Start of the Battle":[
        r"At the start of the battle"
    ],
    "Your Command Phase": [
        r"your command phase",
        r"command phase"
    ],
    "Your Battle-shock Phase": [
        r"battle-shock",
        r"leadership"
    ],
    "Your Movement Phase": [
        r"your movement phase",
        r"normal, advance or fall back move",
        r"advance move",
        r"fall back move",
        r"normal move",
        r"fell back"
    ],
    "Your Shooting Phase": [
        r"your shooting phase",
        r"\bshoot\b",
        r"wound roll",
        r"hit roll",
        r"damage roll",
        r"ballistic skill",
        r"selected to shoot"
    ],
    "Your Charge Phase": [
        r"your charge phase",
        r"declare a charge"
    ],
    "Your Fight Phase": [
        r"your fight phase",
        r"selected to fight",
        r"pile-in",
        r"consolidation",
        r"Wound roll",
        r"Hit roll",
        r"damage roll",
        r"weapon Skill"
    ],
    "Opponent's Shooting Phase": [
        r"opponent's shooting phase"
    ]
}

def main():
    if len(sys.argv) < 2:
        print("Usage: cheatsheet.py <roster.json>")
        sys.exit(1)

    path = pathlib.Path(sys.argv[1])

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    cheatsheet = {}

    for force in data["roster"]["forces"]:
        for sel in walk_selections(force["selections"]):

            source_name = sel.get("name", "Unknown")

            for profile in sel.get("profiles", []):
                if profile.get("typeName") != "Abilities":
                    continue

                desc = profile["characteristics"][0]["$text"]
                phases = detect_phases(desc)

                for phase in phases:
                    cheatsheet.setdefault(phase, []).append({
                        "Source": source_name,
                        "Name": profile["name"],
                        "Description": desc
                    })
    export_to_excel(dedupe_within_phases(cheatsheet), "army_cheatsheet.xlsx")
    print("Exported to army_cheatsheet.xlsx")

def walk_selections(selections):
    for sel in selections:
        yield sel
        if "selections" in sel:
            yield from walk_selections(sel["selections"])


def detect_phases(text):
    phases = set()
    lower = text.lower()

    for phase, patterns in PHASE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, lower):
                phases.add(phase)

    return phases

def export_to_excel(cheatsheet, output_path):
    rows = []

    for phase, abilities in cheatsheet.items():
        for ability in abilities:
            rows.append({
                "Phase": phase,
                "Source": ability["Source"],
                "Ability Name": ability["Name"],
                "Description": ability["Description"]
            })

    df = pd.DataFrame(rows)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Cheatsheet")

def dedupe_within_phases(cheatsheet):
    deduped = {}

    for phase, entries in cheatsheet.items():
        seen = set()
        unique_entries = []

        for entry in entries:
            key = (
                entry.get("Source"),
                entry.get("Name"),
                entry.get("Description")
            )

            if key in seen:
                continue

            seen.add(key)
            unique_entries.append(entry)

        deduped[phase] = unique_entries

    return deduped

if __name__ == "__main__":
    main()
