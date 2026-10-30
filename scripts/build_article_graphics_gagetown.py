"""Two more branded graphics for the CFB Gagetown article (Prime Rogue house style, matched to maps/branded/01–08):
  09  The full sequence, Oct. 28–29: fire power from GOES-19 (every 5 min) and VIIRS (each pass), with the reported times.
  10  Day two: every VIIRS detection of Oct. 28 (outlines), the night of Oct. 29 and the afternoon of Oct. 29, on Sentinel-2 of Oct. 27.
Free sources only. usage: python3 scripts/build_article_graphics_gagetown.py <out_dir>
Logo: drawn from LOGO_PATH if it exists (the house logo is not in this repo); otherwise a placeholder roundel.
"""
import datetime as dt
import os
import sys

import numpy as np
import pandas as pd
import rasterio
from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer
from rasterio.warp import Resampling, reproject

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "cfb-gagetown/2026-10-29/maps/branded")
os.makedirs(OUT, exist_ok=True)
LOGO_PATH = os.environ.get("LOGO_PATH", os.path.join(ROOT, "brand/logo.png"))
INK, GOLD, CREAM, NAVY, PANEL, MUTED = (28, 21, 15), (207, 177, 104), (231, 223, 210), (30, 52, 84), (40, 31, 24), (160, 150, 135)
FD = "/usr/share/fonts/opentype/inter/"
B = lambda s: ImageFont.truetype(FD + "Inter-Bold.otf", int(s))      # noqa: E731
M = lambda s: ImageFont.truetype(FD + "Inter-Medium.otf", int(s))    # noqa: E731
H = lambda s: ImageFont.truetype(FD + "Inter-Black.otf", int(s))     # noqa: E731
KICK = "CFB GAGETOWN FIRE  ·  PRIME ROGUE  ·  OCT. 28–29, 2026"
ADT = dt.timezone(dt.timedelta(hours=-3))
UTC = dt.timezone.utc
T = Transformer.from_crs(4326, 32619, always_xy=True)
TILE = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/19/T/GL/2026/10/S2C_19TGL_20261027_0_L2A/"
FIRE = (-66.257, 45.749)
D28 = pd.read_csv(os.path.join(ROOT, "cfb-gagetown/2026-10-28/firms/detections_2026-10-28T2357Z.csv"))
D29 = pd.read_csv(os.path.join(ROOT, "cfb-gagetown/2026-10-29/firms/detections_2026-10-29T2046Z.csv"))
GOES = pd.read_csv(os.path.join(ROOT, "cfb-gagetown/goes/goes_fire_2026-10-28_29.csv"))


def wrap(t, f, w):
    out, line = [], ""
    for word in t.split():
        test = (line + " " + word).strip()
        if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(test, font=f) > w and line:
            out.append(line); line = word
        else:
            line = test
    return out + [line]


def logo(size):
    if os.path.exists(LOGO_PATH):
        return Image.open(LOGO_PATH).convert("RGBA").resize((size, size), Image.LANCZOS)
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([2, 2, size - 3, size - 3], fill=NAVY, outline=GOLD, width=3)
    d.text((size / 2, size / 2), "PR", font=B(size * 0.34), fill=GOLD, anchor="mm")
    return im


def panel(img, title, sub, notes, credit, name):
    W = img.width + 108
    subl = wrap(sub, M(19), W - 120)
    nl = sum([wrap(n, M(16.5), W - 230) for n in notes + [credit]], [])
    topH = 134 + 28 * len(subl) + 18
    fh = 40 + 25 * len(nl) + 70
    im = Image.new("RGB", (W, img.height + topH + fh), INK); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 12, im.height], fill=GOLD)
    d.text((54, 44), KICK, font=B(20), fill=GOLD)
    d.text((54, 78), title, font=H(44), fill=CREAM)
    for i, l in enumerate(subl):
        d.text((54, 134 + 28 * i), l, font=M(19), fill=MUTED)
    im.paste(img, (54, topH)); d.rectangle([54, topH, 54 + img.width, topH + img.height], outline=GOLD, width=2)
    fy = topH + img.height + 6
    d.rectangle([0, fy, W, im.height], fill=NAVY); d.rectangle([0, fy, W, fy + 5], fill=GOLD)
    for i, l in enumerate(nl):
        d.text((54, fy + 30 + 25 * i), l, font=M(16.5), fill=CREAM)
    d.text((54, im.height - 46), "PRIME ROGUE", font=B(19), fill=GOLD)
    lg = logo(96); im.paste(lg, (W - 140, fy + (im.height - fy - 96) // 2), lg)
    im.save(os.path.join(OUT, name + ".jpg"), quality=88); print(name, im.size)


def s2(bounds, px, band):
    W, S, E, N = bounds
    tf = rasterio.transform.from_bounds(W, S, E, N, px, px)
    with rasterio.open(TILE + band + ".tif") as src:
        out = np.zeros((src.count, px, px), np.float32)
        for b in range(src.count):
            reproject(rasterio.band(src, b + 1), out[b], dst_transform=tf, dst_crs="EPSG:32619", resampling=Resampling.average, src_nodata=0, dst_nodata=0)
    return out


def P(bounds, px, lon, lat):
    E, N = T.transform(lon, lat); W, S, Ea, Nn = bounds; s = px / (Ea - W); return ((E - W) * s, (Nn - N) * s)


# ------------------------------------------------------------------ 09: the full sequence
def timeline():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as md
    import matplotlib.pyplot as plt
    c = lambda x: tuple(np.array(x) / 255)  # noqa: E731
    g = GOES[GOES.satellite.str.startswith("GOES-19") & (GOES["product"] == "ABI-L2-FDCC") & (GOES.status == "ok")].copy()
    g["t"] = pd.to_datetime(g.scan_utc, utc=True).dt.tz_convert(ADT)
    v = pd.concat([D28, D29])
    v = v[v.source.str.startswith("VIIRS")].copy()
    v["t"] = pd.to_datetime(v.utc).dt.tz_localize(UTC).dt.tz_convert(ADT)
    passes = v.groupby("t").frp.agg(["sum", "count"]).reset_index()
    lo, hi = dt.datetime(2026, 10, 28, 11, tzinfo=ADT), dt.datetime(2026, 10, 29, 18, tzinfo=ADT)
    fig, ax = plt.subplots(figsize=(14, 6.4), dpi=100)
    fig.patch.set_facecolor(c(PANEL)); ax.set_facecolor(c(PANEL))
    gf = g[g.frp_total_mw > 0]
    ax.vlines(gf.t, 0, gf.frp_total_mw, color=c((255, 110, 60)), lw=2.2, label="GOES-19 fire power, each 5-minute scan")
    ax.plot(passes.t, passes["sum"], "D", color=c(GOLD), ms=9, label="VIIRS pass: fire power of all pixels")
    ev = [(dt.datetime(2026, 10, 28, 12, 15, tzinfo=ADT), "12:15  training restrictions (base)", 262),
          (dt.datetime(2026, 10, 28, 12, 22, tzinfo=ADT), "12:22  reported to Range Control (base)", 247),
          (dt.datetime(2026, 10, 28, 12, 46, tzinfo=ADT), "12:46  first heat seen from orbit (GOES-19)", 232),
          (dt.datetime(2026, 10, 28, 21, 49, tzinfo=ADT), "9:49 p.m.  base statement on Instagram", 150),
          (dt.datetime(2026, 10, 29, 3, 57, tzinfo=ADT), "3:57–4:15 a.m.  still burning, 1–2 MW", 70),
          (dt.datetime(2026, 10, 29, 12, 11, tzinfo=ADT), "Oct. 29 midday: flares up again", 95)]
    for t, lab, y in ev:
        ax.axvline(t, color=c(MUTED), lw=0.8, ls=":")
        ax.text(t, y, " " + lab, color=c(CREAM), fontsize=11, va="center")
    ax.set_xlim(lo, hi); ax.set_ylim(0, 275); ax.set_yticks(range(0, 201, 50))
    ax.set_ylabel("Fire radiative power (MW)", color=c(CREAM), fontsize=12)
    ax.xaxis.set_major_formatter(md.DateFormatter("%b %d\n%-I %p", tz=ADT))
    ax.xaxis.set_major_locator(md.HourLocator(byhour=range(0, 24, 4), tz=ADT))
    ax.tick_params(colors=c(CREAM), labelsize=11)
    for s in ax.spines.values():
        s.set_color(c(MUTED))
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.legend(loc="upper right", facecolor=c(INK), edgecolor=c(MUTED), labelcolor=c(CREAM), fontsize=11)
    fig.tight_layout()
    tmp = os.path.join(OUT, "_tl.png"); fig.savefig(tmp, facecolor=fig.get_facecolor()); plt.close(fig)
    img = Image.open(tmp).convert("RGB"); os.remove(tmp)
    panel(img, "Two days of fire, seen from orbit",
          "GOES-19 watches the area every five minutes; three VIIRS satellites pass a few times a day. The base's reported times are marked. Times ADT.",
          ["GOES pixels are about 3 km across here and the area was mostly cloudy on Oct. 28, so GOES saw the fire through gaps; VIIRS pixels are about 375 m.",
           "Bars and diamonds measure heat output, not area burned. Base times: CFB Gagetown public affairs, Oct. 29."],
          "Fire detections: NOAA GOES-19 ABI fire product (via NOAA Open Data on AWS; series by Roger Wilco Media) and NASA FIRMS (VIIRS NOAA-21, NOAA-20, "
          "Suomi NPP), Oct. 28–29, 2026. Analysis: Prime Rogue Inc.", "09-cfb-gagetown-fire-timeline")


# ------------------------------------------------------------------ 10: day two
def day_two():
    fE, fN = T.transform(*FIRE)
    b = (fE - 2500, fN - 2500, fE + 2500, fN + 2500); px = 1400
    a = s2(b, px, "TCI")
    im = Image.fromarray(np.clip(a * 1.45, 0, 255).astype(np.uint8).transpose(1, 2, 0)).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    s = px / (b[2] - b[0]); hp = 187.5 * s
    groups = [(D28[D28.source.str.startswith("VIIRS")], (200, 200, 200), 2, "Oct. 28, 1:22–3:41 p.m.: 35 detections"),
              (D29[D29.daynight == "N"], (255, 225, 0), 4, "Oct. 29, 3:57–4:15 a.m.: 4 (night)"),
              (D29[D29.daynight == "D"], (0, 225, 255), 4, "Oct. 29, 1:05–3:21 p.m.: 13")]
    for df, col, w, _ in groups:
        for _, r in df.iterrows():
            x, y = P(b, px, r.longitude, r.latitude)
            d.rectangle([x - hp, y - hp, x + hp, y + hp], outline=col + (255,), width=w)
    x0, y0 = 20, px - 170
    d.rectangle([x0, y0, x0 + 520, y0 + 150], fill=INK + (215,))
    d.text((x0 + 14, y0 + 10), "VIIRS FIRE DETECTIONS (ADT)", font=B(17), fill=GOLD)
    for i, (df, col, w, lab) in enumerate(groups):
        yy = y0 + 46 + 32 * i
        d.rectangle([x0 + 16, yy, x0 + 38, yy + 20], outline=col, width=4)
        d.text((x0 + 50, yy - 1), lab + (f" · peak {df.frp.max():.0f} MW" if len(df) else ""), font=M(18), fill=CREAM)
    L = 1000 * s
    d.rectangle([px - 350, px - 80, px - 330 + L, px - 24], fill=INK + (200,))
    d.rectangle([px - 340, px - 40, px - 340 + L, px - 32], fill=CREAM); d.text((px - 340, px - 72), "1 km", font=B(18), fill=CREAM)
    d.rectangle([px - 86, 22, px - 34, 114], fill=INK + (200,))
    d.polygon([(px - 60, 30), (px - 74, 74), (px - 46, 74)], fill=CREAM); d.text((px - 60, 94), "N", font=B(20), fill=CREAM, anchor="mm")
    panel(im.convert("RGB"), "Day two: the heat moved south",
          "On Oct. 29 every detection sat on the southern side of the first day's area, up to about 0.8 km beyond it. The base put the burned area at about 25 ha.",
          ["Boxes are VIIRS pixels (about 375 m across); positions shift a few hundred metres between passes, so treat the southward move as an indication.",
           "Image: Sentinel-2, Oct. 27, the day before the fire. It shows the ground, not the burn."],
          "Fire detections: NASA FIRMS (VIIRS NOAA-21, NOAA-20, Suomi NPP), Oct. 28–29, 2026. Base image: contains modified Copernicus Sentinel data [2026] "
          "(Sentinel-2, Oct. 27, 2026). Analysis: Prime Rogue Inc.", "10-cfb-gagetown-fire-day-two")


if __name__ == "__main__":
    timeline()
    day_two()
