#!/usr/bin/env python3
"""Notes on refreshing october-catalogue.txt.

This container cannot reach auctionhouselondon.co.uk - the egress proxy refuses
the domain - so the page is fetched through the Zapier "Webhooks by Zapier" GET
action, which runs on Zapier's own infrastructure. In Claude Code:

    mcp__Zapier__execute_zapier_write_action
      selected_api: WebHookCLIAPI
      action:       get
      params:       {"url": "https://auctionhouselondon.co.uk/current-auction",
                     "data": {}, "as_json": "no"}

The response is ~800KB and is written to a file rather than returned inline.
Run this script against that file to regenerate october-catalogue.txt, then
run build_workbook.py.

    python3 fetch_catalogue.py <saved-response.txt>
"""
import html
import re
import sys


def parse(path):
    raw = open(path).read()
    # The webhook response escapes the page; undo that before matching.
    txt = raw.replace('\\"', '"').replace('\\n', '\n').replace('\\/', '/')
    blocks = re.split(r'id="lot-(\d+)"', txt)
    out = []
    for i in range(1, len(blocks), 2):
        lot_id, body = blocks[i], blocks[i + 1]
        addr = (re.search(r'<img alt="([^"]+)"', body)
                or re.search(r'text-18 font-semibold leading-tight">([^<]+)<', body))
        if not addr:
            continue
        guide = re.search(r'Guide Price:\s*([^<]+)<', body)
        if guide:
            price = html.unescape(guide.group(1)).strip()
        else:
            # Lots sold before the sale carry a status in place of the guide.
            badge = re.findall(r'shadow-toast">([^<]{3,90})<', body)
            price = html.unescape(badge[0]).strip() if badge else "Unknown"
        out.append(f"{lot_id} | {html.unescape(addr.group(1)).strip()} | {price}")
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    lots = parse(sys.argv[1])
    with open("october-catalogue.txt", "w") as fh:
        fh.write("\n".join(lots) + "\n")
    print(f"wrote october-catalogue.txt with {len(lots)} lots")
