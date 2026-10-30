"""More house-style graphics for the CFB Gagetown article (cards, a zoomed chart, a comparison), same look as maps/branded/.
  11  Social / featured card (1600 × 900)
  12  What the base told us (the written answers, Oct. 29)
  13  The first hours: GOES-19 every 5 minutes against the base's 12:15 and 12:22 times, Oct. 28
  14  How the story broke (who had what, when)
  15  Gagetown and Wainwright, side by side
usage: python3 scripts/build_article_cards_gagetown.py [out_dir]
"""
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_article_graphics_gagetown as g  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(g.ROOT, "cfb-gagetown/2026-10-29/maps/branded")
g.OUT = OUT
os.makedirs(OUT, exist_ok=True)
INK, GOLD, CREAM, NAVY, PANEL, MUTED, RED = g.INK, g.GOLD, g.CREAM, g.NAVY, g.PANEL, g.MUTED, (226, 92, 58)
B, M, H = g.B, g.M, g.H
ADT, UTC = g.ADT, g.UTC


def save(im, name):
    im.convert("RGB").save(os.path.join(OUT, name + ".jpg"), quality=90); print(name, im.size)


# ------------------------------------------------------------------ 11: social card
def social():
    W, Hh = 1600, 900
    im = Image.new("RGB", (W, Hh), INK); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 14, 745], fill=GOLD)
    for x in range(820, W, 60):                                     # faint grid, as on the house cards
        d.line([(x, 0), (x, 745)], fill=(44, 35, 27))
    for y in range(0, 745, 60):
        d.line([(820, y), (W, y)], fill=(44, 35, 27))
    d.text((64, 72), "CFB GAGETOWN FIRE  ·  FIRST REPORTED BY PRIME ROGUE", font=B(26), fill=GOLD)
    d.text((64, 130), "Artillery started it.", font=H(76), fill=CREAM)
    d.text((64, 222), "Orbit saw it", font=H(76), fill=GOLD)
    d.text((64, 314), "24 minutes later.", font=H(76), fill=GOLD)
    y = 440
    for line in g.wrap("Reported to Range Control at 12:22 p.m. on Oct. 28. GOES-19's first heat: 12:46. Still burning the next afternoon.", M(30), 690):
        d.text((64, y), line, font=M(30), fill=MUTED); y += 42
    # mini chart: GOES-19 fire power, 12:00–4:00 p.m.
    goes = g.GOES[g.GOES.satellite.str.startswith("GOES-19") & (g.GOES["product"] == "ABI-L2-FDCC") & (g.GOES.status == "ok")].copy()
    goes["t"] = pd.to_datetime(goes.scan_utc, utc=True).dt.tz_convert(ADT)
    t0 = dt.datetime(2026, 10, 28, 12, 0, tzinfo=ADT); t1 = dt.datetime(2026, 10, 28, 16, 0, tzinfo=ADT)
    x0, x1, yb, yt = 880, 1540, 640, 160
    X = lambda t: x0 + (t - t0).total_seconds() / (t1 - t0).total_seconds() * (x1 - x0)  # noqa: E731
    for _, r in goes[(goes.t >= t0) & (goes.t <= t1) & (goes.frp_total_mw > 0)].iterrows():
        h = r.frp_total_mw / 120 * (yb - yt); x = X(r.t); d.rectangle([x - 3, yb - h, x + 3, yb], fill=RED)
    for t, lab, col in [(dt.datetime(2026, 10, 28, 12, 22, tzinfo=ADT), "12:22 reported", GOLD), (dt.datetime(2026, 10, 28, 12, 46, tzinfo=ADT), "12:46 first heat", RED)]:
        x = X(t); d.line([(x, yt - 20), (x, yb)], fill=col, width=3)
    d.text((X(dt.datetime(2026, 10, 28, 12, 22, tzinfo=ADT)) - 6, yt - 64), "12:22 reported", font=B(22), fill=GOLD, anchor="ra")
    d.text((X(dt.datetime(2026, 10, 28, 12, 46, tzinfo=ADT)) + 8, yt - 64), "12:46 first heat", font=B(22), fill=RED)
    d.line([(x0, yb), (x1, yb)], fill=MUTED, width=2)
    for hh in (12, 13, 14, 15, 16):
        x = X(dt.datetime(2026, 10, 28, hh, 0, tzinfo=ADT)); d.text((x, yb + 12), f"{hh if hh <= 12 else hh - 12} p.m." if hh != 12 else "noon", font=M(20), fill=MUTED, anchor="ma")
    d.text((x0, yb + 50), "GOES-19 FIRE POWER, EVERY 5 MINUTES, OCT. 28 (ADT)", font=B(20), fill=MUTED)
    d.rectangle([0, 745, W, Hh], fill=NAVY); d.rectangle([0, 745, W, 751], fill=GOLD)
    d.text((64, 790), "PRIME ROGUE", font=H(44), fill=GOLD)
    d.text((64, 850), "By Kevin J.S. Duska Jr.  ·  Oct. 30, 2026", font=M(24), fill=CREAM)
    lg = g.logo(118); im.paste(lg, (W - 170, 763), lg)
    save(im, "11-cfb-gagetown-fire-social-card")


# ------------------------------------------------------------------ 12: what the base told us
def base_answers():
    rows = [("Cause", "“The wildfire was started by artillery shooting into Lawfield Impact Area.” Under investigation; it began inside an active impact area."),
            ("Reported", "To Range Control at 12:22 p.m. ADT, Oct. 28. Training restrictions from 12:15 p.m."),
            ("Training", "Royal Canadian Artillery School, Forward Observation Officer course, 105 mm LG1 howitzer."),
            ("Fire danger", "Moderate. Some pyrotechnic and illumination munitions restricted where they raise fire risk."),
            ("Size", "About 25 ha burned, about 12 ha still active (Oct. 29), northeastern part of the training area."),
            ("People", "No injuries. No one evacuated or moved. “No risk to the public, CAF members, or civilian employees.”"),
            ("Firefighting", "Wildland Fire Management Services leading; helicopter bucketing; a 4 ESR armoured dozer. Unexploded ordnance rules out some methods."),
            ("After Wainwright", "The CAF “continually reviews” range safety; CAF-wide questions referred to “the appropriate authorities.”")]
    W = 1400; y = 30
    im = Image.new("RGB", (W, 90 + 118 * len(rows)), PANEL); d = ImageDraw.Draw(im)
    for k, v in rows:
        d.text((36, y + 6), k.upper(), font=B(22), fill=GOLD)
        lines = g.wrap(v, M(26), W - 360)
        for i, l in enumerate(lines[:3]):
            d.text((320, y + 34 * i), l, font=M(26), fill=CREAM)
        y += 118
        d.line([(36, y - 22), (W - 36, y - 22)], fill=(64, 52, 40), width=1)
    g.panel(im, "What the base told us", "CFB Gagetown public affairs answered Prime Rogue's questions in writing on Oct. 29. National Defence did not "
            "reply to an earlier set of questions.", ["Quotes and figures: Capt. Robynn Still, Public Affairs Officer, Canadian Support Group (Atlantic), Oct. 29, 2026."],
            "Prime Rogue Inc.", "12-cfb-gagetown-fire-base-answers")


# ------------------------------------------------------------------ 13: the first hours
def first_hours():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as md
    import matplotlib.pyplot as plt
    c = lambda x: tuple(np.array(x) / 255)  # noqa: E731
    goes = g.GOES[g.GOES.satellite.str.startswith("GOES-19") & (g.GOES.status == "ok")].copy()
    goes["t"] = pd.to_datetime(goes.scan_utc, utc=True).dt.tz_convert(ADT)
    fd = goes[goes["product"] == "ABI-L2-FDCC"]
    v = g.D28[g.D28.source.str.startswith("VIIRS")].copy(); v["t"] = pd.to_datetime(v.utc).dt.tz_localize(UTC).dt.tz_convert(ADT)
    vp = v.groupby("t").frp.agg(["sum", "count"]).reset_index()
    lo, hi = dt.datetime(2026, 10, 28, 11, 45, tzinfo=ADT), dt.datetime(2026, 10, 28, 16, 15, tzinfo=ADT)
    fig, ax = plt.subplots(figsize=(14, 6.2), dpi=100); fig.patch.set_facecolor(c(PANEL)); ax.set_facecolor(c(PANEL))
    a2 = ax.twinx()
    a2.fill_between(fd.t, 0, fd.cloud_px / fd.px_in_box * 100, step="mid", color=c((90, 80, 70)), alpha=0.45, lw=0)
    a2.set_ylim(0, 300); a2.set_yticks([]); [s.set_visible(False) for s in a2.spines.values()]
    f = fd[fd.frp_total_mw > 0]
    ax.vlines(f.t, 0, f.frp_total_mw, color=c(RED), lw=3, label="GOES-19 fire power, each 5-minute scan")
    ax.plot(vp.t, vp["sum"], "D", color=c(GOLD), ms=10, label="VIIRS pass: fire power of all pixels")
    for _, r in vp.iterrows():
        ax.annotate(f'{r.t:%-I:%M} · {int(r["count"])} px', (r.t, r["sum"]), textcoords="offset points", xytext=(0, 12), ha="center", color=c(CREAM), fontsize=11)
    for t, lab, y, col in [(dt.datetime(2026, 10, 28, 12, 15, tzinfo=ADT), "12:15 training\nrestrictions", 175, MUTED),
                           (dt.datetime(2026, 10, 28, 12, 22, tzinfo=ADT), "12:22 reported to\nRange Control", 140, GOLD),
                           (dt.datetime(2026, 10, 28, 12, 46, tzinfo=ADT), "12:46 first heat\nfrom orbit", 105, RED)]:
        ax.axvline(t, color=c(col), lw=1.6, ls="--")
        ax.text(t, y, " " + lab, color=c(col), fontsize=12, va="center", fontweight="bold")
    ax.annotate("", xy=(dt.datetime(2026, 10, 28, 12, 46, tzinfo=ADT), 200), xytext=(dt.datetime(2026, 10, 28, 12, 22, tzinfo=ADT), 200),
                arrowprops=dict(arrowstyle="<->", color=c(CREAM), lw=1.4))
    ax.text(dt.datetime(2026, 10, 28, 12, 34, tzinfo=ADT), 207, "24 min", color=c(CREAM), ha="center", fontsize=12, fontweight="bold")
    ax.set_xlim(lo, hi); ax.set_ylim(0, 220)
    ax.set_ylabel("Fire radiative power (MW)", color=c(CREAM), fontsize=12)
    ax.xaxis.set_major_formatter(md.DateFormatter("%-I:%M %p", tz=ADT)); ax.xaxis.set_major_locator(md.MinuteLocator(byminute=[0, 30], tz=ADT))
    ax.tick_params(colors=c(CREAM), labelsize=11)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(c(MUTED))
    ax.legend(loc="upper right", facecolor=c(INK), edgecolor=c(MUTED), labelcolor=c(CREAM), fontsize=11)
    fig.tight_layout(); tmp = os.path.join(OUT, "_fh.png"); fig.savefig(tmp, facecolor=fig.get_facecolor()); plt.close(fig)
    img = Image.open(tmp).convert("RGB"); os.remove(tmp)
    g.panel(img, "The first hours, minute by minute", "GOES-19 images the area every five minutes. Its first heat came 24 minutes after the base's reported time; "
            "VIIRS passed five times that afternoon. Grey shading: share of the GOES box coded cloud. Times ADT, Oct. 28.",
            ["GOES's first flag (12:46) was a low-probability code; its first measured fire power came at 12:50–12:51 p.m. Gaps between bars are mostly cloud, not the fire stopping.",
             "Base times: CFB Gagetown public affairs, Oct. 29."],
            "Fire detections: NOAA GOES-19 ABI fire product, CONUS scans (NOAA Open Data on AWS; series by Roger Wilco Imagery) and NASA FIRMS (VIIRS), Oct. 28, 2026. "
            "Analysis: Prime Rogue Inc.", "13-cfb-gagetown-fire-first-hours")


# ------------------------------------------------------------------ 14: how the story broke
def story():
    ev = [("OCT. 28 · 12:22 P.M.", "Fire reported to Range Control", "CFB Gagetown (stated Oct. 29)", GOLD),
          ("12:46 P.M.", "First heat from orbit", "GOES-19 (NOAA)", RED),
          ("1:22–3:41 P.M.", "35 detections, five satellite passes", "NASA FIRMS (VIIRS)", RED),
          ("5:21 P.M.", "Flagged as new heat on a military base", "Roger Wilco Imagery (Prime Rogue), automated satellite watch", CREAM),
          ("8:45 P.M.", "First data pull and maps", "Prime Rogue Inc.", CREAM),
          ("9:13 P.M.", "FIRST PUBLIC REPORT, on X", "Prime Rogue, from Roger Wilco Imagery data", RED),
          ("ABOUT 9:49 P.M.", "Base statement on Instagram: fire burning, no threat", "CFB Gagetown", GOLD),
          ("LATE OCT. 28", "First wire story", "The Canadian Press", MUTED),
          ("OCT. 29, MORNING", "Satellite timeline: SITREP 017", "Roger Wilco Imagery (Prime Rogue)", CREAM),
          ("OCT. 29, DAY", "Cause and size: artillery into Lawfield Impact Area, ~25 ha", "CFB Gagetown via CBC, Fredericton Independent", GOLD),
          ("OCT. 29", "Written answers to Prime Rogue's questions", "CFB Gagetown public affairs", GOLD),
          ("OCT. 29, 1:05–3:21 P.M.", "Burning again: 13 detections", "NASA FIRMS (VIIRS)", RED)]
    W = 1400; rh = 96
    im = Image.new("RGB", (W, 40 + rh * len(ev)), PANEL); d = ImageDraw.Draw(im)
    xL = 330
    d.line([(xL, 30), (xL, 30 + rh * len(ev) - 40)], fill=(90, 76, 60), width=3)
    for i, (t, what, who, col) in enumerate(ev):
        y = 30 + rh * i
        d.text((xL - 30, y + 2), t, font=B(20), fill=GOLD, anchor="ra")
        d.ellipse([xL - 11, y + 2, xL + 11, y + 24], fill=col, outline=INK, width=3)
        d.text((xL + 34, y - 2), what, font=B(27), fill=CREAM)
        d.text((xL + 34, y + 36), who, font=M(21), fill=MUTED)
    g.panel(im, "How the story broke", "From the first report to Range Control to the first answers. Prime Rogue reported it first, on X, 36 minutes before "
            "the base's public statement; the cause came the next day. Times ADT.",
            ["Prime Rogue's X post at 9:13 p.m. ADT was, as far as we can find, the first public report of the fire.",
             "Disclosure: Roger Wilco Imagery is Prime Rogue's satellite-monitoring dashboard, owned by Prime Rogue Inc. and not yet launched."],
            "Sources: CFB Gagetown public affairs; NOAA GOES-19; NASA FIRMS; The Canadian Press; CBC News; Fredericton Independent; Roger Wilco Imagery. "
            "Analysis: Prime Rogue Inc.", "14-cfb-gagetown-fire-how-the-story-broke")


# ------------------------------------------------------------------ 15: Gagetown and Wainwright
def compare():
    rows = [("Date", "Oct. 17, 2026", "Oct. 28, 2026"),
            ("Where it started", "Automatic grenade launcher range", "Lawfield Impact Area (artillery)"),
            ("Firing at the time", "Live-fire training", "RCAS Forward Observation Officer course, 105 mm LG1"),
            ("Wind", "Gust 82 km/h at 3:16 p.m. drove it onto troops", "Light winds forecast (base)"),
            ("People in its path", "Soldiers on a nearby range", "None (base)"),
            ("Casualties", "4 killed, 39 injured", "None"),
            ("Area burned", "About 10.7 km² (satellite estimate)", "About 25 ha (base, Oct. 29)"),
            ("First satellite heat", "About 70 min before the first stated time", "24 min after the stated report")]
    W = 1400; rh = 92
    im = Image.new("RGB", (W, 110 + rh * len(rows)), PANEL); d = ImageDraw.Draw(im)
    c1, c2 = 380, 900
    d.text((c1, 34), "CFB WAINWRIGHT", font=B(26), fill=RED); d.text((c2, 34), "CFB GAGETOWN", font=B(26), fill=GOLD)
    for i, (k, a, b) in enumerate(rows):
        y = 100 + rh * i
        d.line([(36, y - 14), (W - 36, y - 14)], fill=(64, 52, 40))
        d.text((36, y), k.upper(), font=B(20), fill=MUTED)
        for x, txt in ((c1, a), (c2, b)):
            for j, l in enumerate(g.wrap(txt, M(25), 470)[:2]):
                d.text((x, y - 2 + 32 * j), l, font=M(25), fill=CREAM)
    g.panel(im, "Two range fires, eleven days apart", "Both started during live-fire training. At Wainwright, wind drove the fire onto soldiers; at Gagetown, "
            "it stayed in the impact area and no one was hurt.",
            ["Wainwright: DND and published reporting; satellite figures from Roger Wilco Imagery's analysis (RWI-HC-001). Gagetown: CFB Gagetown public affairs, Oct. 29.",
             "Areas are not comparable estimates: Wainwright from imagery, Gagetown the base's figure."],
            "Prime Rogue Inc.", "15-cfb-gagetown-wainwright-compared")


if __name__ == "__main__":
    social(); base_answers(); first_hours(); story(); compare()
