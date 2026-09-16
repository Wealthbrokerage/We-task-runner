#!/usr/bin/env python3
"""Rank lots by discount to Hometrack and write the top 30 to a workbook.

Only lots with BOTH a numeric guide and a numeric Hometrack figure can be
ranked, which is 69 of the 100 tracked. The other 31 are land, garages,
parking, commercial and units the AVM could not isolate.
"""
import csv
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

OUT = "Auction - top 30 by discount.xlsx"
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

# Valuation caveats recorded in the source spreadsheet. A lot named here has an
# AVM that is not cleanly for the lot being sold, so its discount may be fiction.
CAUTION = {
 "21A": "AVM may be whole building (Flat A of 2)",
 "29":  "AVM is 174 Bravington Rd whole property; lot is a 60-yr-lease flat",
 "37":  "Lot is 37 + 37A; AVM covers 37 only",
 "39":  "AVM matched WD6 5PJ vs catalogue WD6 5PG - verify",
 "46":  "Flat 1 used as proxy for Ground/Basement flat",
 "64":  "Indexed as Crook Rotary Club - commercial building",
 "65":  "102-106 High St indexed as one commercial parade",
 "66":  "AVM is 396a flat only; lot is mixed-use with retail",
 "73":  "Part of the 102-106 commercial parade",
 "76":  "Part of the 102-106 commercial parade",
 "82":  "Representative apartment; Apt 43 not isolatable",
 "85":  "Representative Maple Court unit; Flat 4 not isolatable",
 "90":  "AVM likely whole building, not one unit - verify",
 "98":  "AVM is 196 whole building; lot is flat 196A, worth less",
 "102": "Building indexed as one; flat 3 not separable",
 "105": "No.2 not indexed; value is neighbouring 1 Garfield St",
 "112": "Representative unit at 2 Moorfields",
 "113": "Representative unit at 2 Moorfields",
 "119": "Building indexed as one; Flat 29 not separable",
 "152": "Flats 1-4 are a grouped entry",
 "160A": "Representative Farringford Court unit",
 "163": "AVM is the whole house; lot is Flat 3, worth less",
 "164": "Very low AVM - likely small retail/commercial",
 "166": "Building indexed as one; Apt 006 not separable",
 "169": "No.4 not indexed; value is No.5 - AVM UNRELIABLE",
}
STATUS = {"october-catalogue": "In October catalogue",
          "SOLD PRIOR": "Sold prior to auction",
          "NOT LISTED": "Not in October catalogue - availability unconfirmed"}


def low(s):
    m = re.search(r"£\s*([\d,]+)", s or "")
    return int(m.group(1).replace(",", "")) if m else None


def main():
    rows = list(csv.DictReader(open("results.csv")))
    pool = []
    for r in rows:
        ht = low(r["hometrack"])
        guide = low(r["site_guide"]) if r["site_lot"] else low(r["guide_price"])
        if guide is None:
            guide = low(r["guide_price"])
        if ht and guide:
            pool.append({"addr": r["address"],
                         "lot": (r["site_lot"] or f'Sept {r["lot"]}'),
                         "sep_lot": r["lot"], "guide": guide, "ht": ht,
                         "ratio": guide / ht, "status": STATUS[r["status"]],
                         "caution": CAUTION.get(r["lot"], "")})
    pool.sort(key=lambda x: x["ratio"])
    top = pool[:30]

    wb = Workbook()
    ws = wb.active
    ws.title = "Top 30 by discount"
    ARIAL = "Arial"
    hdr = PatternFill("solid", fgColor="1F3864")
    live = PatternFill("solid", fgColor="E2EFDA")
    warn = PatternFill("solid", fgColor="FFF2CC")
    hf = Font(name=ARIAL, size=10, bold=True, color="FFFFFF")
    t = Side(style="thin", color="BFBFBF")
    bd = Border(left=t, right=t, top=t, bottom=t)

    heads = ["Rank", "Address", "Lot number", "Guide price", "Guide +10%",
             "Hometrack valuation", "% guide of valuation", "Discount to valuation",
             "Status", "Valuation check"]
    ws.append(heads)
    for i in range(1, len(heads) + 1):
        c = ws.cell(row=1, column=i)
        c.fill, c.font, c.border = hdr, hf, bd
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for i, p in enumerate(top, start=2):
        ws.cell(row=i, column=1, value=i - 1)
        ws.cell(row=i, column=2, value=p["addr"])
        ws.cell(row=i, column=3, value=p["lot"])
        ws.cell(row=i, column=4, value=p["guide"])
        ws.cell(row=i, column=5, value=f"=D{i}*1.1")
        ws.cell(row=i, column=6, value=p["ht"])
        ws.cell(row=i, column=7, value=f"=D{i}/F{i}")
        ws.cell(row=i, column=8, value=f"=1-G{i}")
        ws.cell(row=i, column=9, value=p["status"])
        ws.cell(row=i, column=10, value=p["caution"])
        fill = live if p["status"].startswith("In October") else None
        if p["caution"]:
            fill = warn
        for c in range(1, len(heads) + 1):
            cell = ws.cell(row=i, column=c)
            cell.font = Font(name=ARIAL, size=10)
            cell.border = bd
            cell.alignment = Alignment(vertical="top", wrap_text=(c in (2, 9, 10)))
            if fill:
                cell.fill = fill
        for c in (4, 5, 6):
            ws.cell(row=i, column=c).number_format = '£#,##0;(£#,##0);-'
        for c in (7, 8):
            ws.cell(row=i, column=c).number_format = '0.0%;(0.0%);-'

    for i, w in enumerate([6, 54, 12, 14, 14, 18, 14, 14, 30, 44], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:J{len(top) + 1}"

    nt = wb.create_sheet("Notes")
    nt.column_dimensions["A"].width = 112
    in_oct = sum(1 for p in top if p["status"].startswith("In October"))
    flagged = sum(1 for p in top if p["caution"])
    lines = [
     ("Top 30 by discount to Hometrack valuation", True), ("", False),
     ("Ranking", True),
     ("Sorted by '% guide of valuation' ascending - the guide as a proportion of assessed value,",False),
     ("so the largest discounts are at the top. 'Discount to valuation' is 1 minus that.",False),
     ("Guide +10% is the guide times 1.1, as requested. Range guides use the LOW end.",False),("",False),
     ("What could be ranked", True),
     (f"Only lots with BOTH a guide and a numeric Hometrack figure can be ranked: 69 of the 100",False),
     ("we track. The other 31 are land, garages, parking spaces, commercial units and flats the",False),
     ("AVM could not isolate, so no discount can be computed for them.",False),("",False),
     ("AVAILABILITY - READ BEFORE ACTING", True),
     (f"Only {in_oct} of these 30 are confirmed in the 7-8 October catalogue (shaded green).",False),
     ("The rest come from our September tracked list. That auction has run, so they may have sold,",False),
     ("been withdrawn, or remain unsold and available - we cannot tell from what we hold. Checking",False),
     ("needs the auction house's 'lots still available' page, which has not been captured.",False),
     ("Only 11 of the 107 October lots have a Hometrack valuation at all, which is why a top 30",False),
     ("cannot be drawn from the October sale alone.",False),("",False),
     ("VALUATION CHECK COLUMN", True),
     (f"{flagged} of these 30 are shaded amber because the Hometrack figure is not cleanly for the",False),
     ("lot being sold - it is the whole building, a representative unit, or a neighbouring property.",False),
     ("Their discounts may be fiction. The caveats come from the source spreadsheet's own notes.",False),
     ("A very large discount on an amber row is a reason to check the valuation, not to bid.",False),("",False),
     ("Sources", True),
     ("Guides: auctionhouselondon.co.uk/current-auction, fetched 16 September 2026, for lots in the",False),
     ("October sale; the September catalogue otherwise. Hometrack valuations: from the source",False),
     ("spreadsheet, Dropbox /Clients/Vance/110 portfolio/October auction.xlsx.",False),
    ]
    for i, (text, b) in enumerate(lines, start=1):
        c = nt.cell(row=i, column=1, value=text)
        c.font = Font(name=ARIAL, size=10, bold=b)
        c.alignment = Alignment(vertical="top")

    wb.save(OUT)

    # Patch cached values (openpyxl writes formulas without them).
    ET.register_namespace("", NS)
    wb = load_workbook(OUT)
    ws = wb["Top 30 by discount"]
    want = {}
    for r in range(2, ws.max_row + 1):
        g = ws.cell(row=r, column=4).value
        h = ws.cell(row=r, column=6).value
        want[f"E{r}"] = g * 1.1
        want[f"G{r}"] = g / h
        want[f"H{r}"] = 1 - g / h
    with zipfile.ZipFile(OUT) as z:
        names = z.namelist(); data = {n: z.read(n) for n in names}
    path = f"xl/worksheets/sheet{wb.sheetnames.index('Top 30 by discount') + 1}.xml"
    root = ET.fromstring(data[path]); n = 0
    for c in root.iter(f"{{{NS}}}c"):
        ref = c.get("r")
        if ref in want and c.find(f"{{{NS}}}f") is not None:
            for old in c.findall(f"{{{NS}}}v"):
                c.remove(old)
            ET.SubElement(c, f"{{{NS}}}v").text = repr(round(want[ref], 10))
            c.attrib.pop("t", None); n += 1
    data[path] = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for name in names:
            z.writestr(name, data[name])
    chk = load_workbook(OUT, data_only=True)["Top 30 by discount"]
    bad = sum(1 for ref, e in want.items()
              if chk[ref].value is None or abs(chk[ref].value - e) > 1e-9)
    print(f"cached values: patched {n}, verified {n - bad}, mismatches {bad}")
    if bad:
        sys.exit(1)
    print(f"pool {len(pool)} rankable | top 30 written | in October: {in_oct} | flagged: {flagged}")
    return top


if __name__ == "__main__":
    top = main()
    print(f"\n{'#':>3} {'Address':<46}{'Lot':>9}{'Guide':>10}{'+10%':>10}{'Hometrack':>11}{'%':>6}  flag")
    for i, p in enumerate(top, 1):
        print(f"{i:>3} {p['addr'][:44]:<46}{p['lot']:>9}£{p['guide']:>9,}£{p['guide']*1.1:>9,.0f}"
              f"£{p['ht']:>10,}{p['ratio']:>6.0%}  {'!' if p['caution'] else ''}")
