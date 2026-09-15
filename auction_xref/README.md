# Auction lot cross-reference

Checks our tracked Auction House London lots against the auction house's own
pages, to see which are still available.

## What's here

- `lots.csv` — the 100 lots we track, transcribed from
  `Dropbox:/Clients/Vance/110 portfolio/October auction.xlsx`, with guide price,
  Hometrack AVM, Serco status and any accepted offer.
- `xref.py` — matches those lots against a saved copy of an auction house page.
- `example-dump.txt` — four made-up lines showing the input format. Not real data.

## Provenance of `lots.csv`

The source spreadsheet is named "October auction" but the lots are the
**2nd–3rd September 2026** sale, confirmed against two published lot records
(lot 99, 23 Selkirk Road, and lot 101, 49 Exmouth Road — both dated 02/09/2026).
The spreadsheet's own source note flagged this as unresolved; it is now resolved.
That auction has run, so "available" for these lots means *unsold and still
offered*, not *in the catalogue*.

Two addresses are corrected here against the site and kept as the site spells
them, so matching works:

| Sheet | Corrected |
| --- | --- |
| 4 Narin Court, Tilbury | 4 Nairn Court |
| 3 Jane Court, St Albans | 3 Dane Court |
| 104 Graveney Road, SW17 0DH | SW17 0EH |

## Usage

Save the auction house page as text — copy-paste, or print-to-PDF then extract —
naming each file after the status it represents:

```
python3 xref.py still-available.txt october-catalogue.txt
```

The filename stem becomes the reported status, so `still-available.txt` yields
`still-available`. Lots whose postcode appears in no dump come back `NOT LISTED`.
Results go to stdout as CSV; the summary goes to stderr.

```
python3 xref.py still-available.txt > results.csv
```

## Why matching is on postcode

Lot numbers and property names drift between our sheet and the site — our lot 39
"Holmshill House" is the site's lot 40 "Holmshill Farm". Postcode is the only
stable key. Where several lots share a postcode (2 Moorfields, Regatta Point),
the leading flat/house number separates them; where it can't, the row is marked
`AMBIGUOUS` for a human to settle rather than guessed at.
