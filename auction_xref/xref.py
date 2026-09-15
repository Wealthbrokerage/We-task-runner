#!/usr/bin/env python3
"""Cross-reference our tracked auction lots against an Auction House London page dump.

Usage:
    python3 xref.py <site-dump> [<site-dump> ...] [--lots lots.csv]

A <site-dump> is any text file saved from the auction house site -- pasted page
text, a print-to-PDF run through a text extractor, or a CSV. The parser only
needs each property to appear on a line containing a UK postcode; everything
else is treated as that entry's descriptive text.

Name the dumps so their status is obvious, e.g.:
    still-available.txt   -> lots offered post-auction, still buyable
    october-catalogue.txt -> re-entered into the 7-8 Oct sale
The stem of each filename becomes the status reported for lots found in it.

Matching is on postcode first (the only reliable key -- lot numbers and
property names drift between our sheet and the site), then on the leading
house number or flat/unit identifier to separate multiple lots at one postcode.
"""

import csv
import pathlib
import re
import sys
from collections import defaultdict

POSTCODE = re.compile(
    r"\b([A-Z]{1,2}[0-9][A-Z0-9]?)\s*([0-9][A-Z]{2})\b", re.IGNORECASE
)

# Leading identifier: "Flat 41", "Apartment 006", "Unit SU8", "23", "196A", "Plot 2".
LEADER = re.compile(
    r"^(?:(?:flat|apartment|apt|unit|plot|garage|compound|parking\s+space)\s*)?"
    r"([0-9]+[a-z]?)\b",
    re.IGNORECASE,
)


def norm_postcode(text):
    m = POSTCODE.search(text or "")
    return f"{m.group(1)}{m.group(2)}".upper() if m else None


def leader(address):
    """Leading house/flat number, used to disambiguate lots sharing a postcode."""
    for part in (p.strip() for p in (address or "").split(",")):
        if not part:
            continue
        m = LEADER.search(part)
        if m:
            return m.group(1).upper()
    return None


def load_lots(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def parse_dump(path):
    """Yield one record per line carrying a postcode.

    A line shaped "lot | address | guide" is split into those fields; anything
    else is scanned whole. Splitting matters: without it the leading lot number
    is taken for the house number, so two flats in one building match each
    other instead of themselves.
    """
    raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    for line in raw.splitlines():
        line = " ".join(line.split())
        if not line:
            continue
        lot = guide = ""
        address = line
        if line.count("|") >= 2:
            lot, address, guide = (f.strip() for f in line.split("|", 2))
        pc = norm_postcode(address)
        if pc:
            yield {
                "postcode": pc,
                "leader": leader(address),
                "lot": lot,
                "address": address,
                "guide": guide,
                "line": line,
            }


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    lots_path = "lots.csv"
    if "--lots" in argv:
        lots_path = argv[argv.index("--lots") + 1]
        args = [a for a in args if a != lots_path]

    if not args:
        print(__doc__)
        return 1

    lots = load_lots(lots_path)

    # postcode -> list of (status, leader, line)
    site = defaultdict(list)
    for dump in args:
        status = pathlib.Path(dump).stem
        n = 0
        for rec in parse_dump(dump):
            rec["status"] = status
            site[rec["postcode"]].append(rec)
            n += 1
        print(f"# loaded {n} site entries from {dump} (status: {status})",
              file=sys.stderr)

    out = csv.writer(sys.stdout)
    out.writerow(
        ["lot", "address", "guide_price", "hometrack", "serco_status",
         "accepted_offer", "status", "confidence", "site_lot", "site_guide",
         "site_entry"]
    )

    counts = defaultdict(int)
    for row in lots:
        pc = norm_postcode(row["address"])
        hits = site.get(pc, []) if pc else []

        site_guide = site_lot = ""
        if not pc:
            status, conf, entry = "CHECK MANUALLY", "no postcode in our address", ""
        elif not hits:
            status, conf, entry = "NOT LISTED", "postcode absent from dumps", ""
        else:
            ours = leader(row["address"])
            exact = [h for h in hits if ours and h["leader"] == ours]
            chosen = exact or hits
            status = chosen[0]["status"]
            entry = chosen[0]["line"]
            site_guide = chosen[0]["guide"]
            site_lot = chosen[0]["lot"]
            # The catalogue marks withdrawn-before-sale lots inline; those are
            # gone, not available, whatever the dump's filename says.
            if "sold prior" in entry.lower():
                status = "SOLD PRIOR"
            numbered = [h for h in hits if h["leader"]]
            if exact:
                conf = "postcode + number"
            elif ours and numbered and len(numbered) == len(hits):
                status, entry, site_guide, site_lot = "NOT LISTED", "", "", ""
                conf = f"different unit at {pc} ({ours} not offered)"
            elif len(hits) == 1:
                conf = "postcode only"
            else:
                conf = f"AMBIGUOUS - {len(hits)} lots share {pc}"

        counts[status] += 1
        out.writerow([
            row["lot"], row["address"], row["guide_price"], row["hometrack"],
            row["serco_status"], row["accepted_offer"], status, conf,
            site_lot, site_guide, entry,
        ])

    print("\n# summary", file=sys.stderr)
    for status, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"#   {status}: {n}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:  # piping into head/less
        sys.exit(0)
