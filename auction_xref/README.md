# Auction lot cross-reference

Checks our tracked Auction House London lots against the auction house's live
catalogue, and builds the deliverable workbook.

## Files

- `lots.csv` — the 100 lots we track, transcribed from
  `Dropbox:/Clients/Vance/110 portfolio/October auction.xlsx`.
- `october-catalogue.txt` — the auction house's current catalogue, one lot per
  line as `site id | address | guide`.
- `fetch_catalogue.py` — regenerates that file from a fetched copy of the page.
- `xref.py` — matches our lots against the catalogue, writing `results.csv`.
- `build_workbook.py` — builds `Auction lots - checked list.xlsx` from the above.

## Refreshing

This container cannot reach `auctionhouselondon.co.uk`; the egress proxy refuses
the domain. The page is fetched instead through Zapier's "Webhooks by Zapier"
GET action, which runs on Zapier's infrastructure:

    selected_api: WebHookCLIAPI, action: get
    params: {"url": "https://auctionhouselondon.co.uk/current-auction",
             "data": {}, "as_json": "no"}

The ~800KB response is saved to a file. Then:

    python3 fetch_catalogue.py <saved-response.txt>
    python3 xref.py october-catalogue.txt --lots lots.csv > results.csv
    python3 build_workbook.py

Do this again nearer 7-8 October: the sale was still taking entries when it was
last captured, so lots will have been added.

## Two things that caused wrong answers, now fixed

**A browser copy-paste of the catalogue silently dropped lots.** It yielded 93
where the page holds 107, and several of our lots were reported as absent from
the October sale when they were in it. Always regenerate from a fetch, never a
paste.

**openpyxl discards cached formula values on every save.** Each edit pass wiped
the values written by the one before, so computed columns read blank outside
Excel. `build_workbook.py` regenerates all sheets in one pass and patches the
values as its last step. Prefer re-running it over editing the workbook in place.

## Matching

On postcode, then flat/house number. Lot numbers and property names differ
between sales — our lot 39 "Holmshill House" is the site's "Holmshill Farm" — so
neither is a safe key. Where lots share a postcode the leading unit number
separates them; anything unresolved is reported rather than guessed.

## Known limit

"Not in October catalogue" does not mean sold. Separating sold from withdrawn
from unsold-and-still-available needs the auction house's "lots still available"
page, which is not yet captured.
