"""Branded image set for the CFB Gagetown fire, Oct. 28, 2026 (Prime Rogue house style, pr.py).
Free sources only: NASA FIRMS VIIRS, Copernicus Sentinel-2 (Oct. 27), Copernicus DEM GLO-30.
usage: python3 build_brand.py <detections.csv> <out_dir>
"""
import sys, os, glob, numpy as np, pandas as pd, rasterio
from rasterio.windows import from_bounds
from rasterio.warp import reproject, Resampling
from pyproj import Transformer
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/cfb-wainwright-fire-archive/scripts/maps"); import pr
S = "/tmp/claude-0/-home-claude/11d4f8cb-573a-58d8-9723-d23e8fe40496/scratchpad/"
_L = Image.open(S + "sat_page/logo_transparent.png").convert("RGBA").resize((84, 84), Image.LANCZOS)
_bg = Image.new("RGBA", (84, 84), pr.NAVY + (255,)); pr._LOGO = Image.alpha_composite(_bg, _L)

DET = pd.read_csv(sys.argv[1]); DET = DET[DET.source.str.startswith("VIIRS")].copy()
DET["hm"] = DET["local"].str[11:16]
OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
KICK = "CFB GAGETOWN FIRE  ·  PRIME ROGUE  ·  BREAKING, UNCONFIRMED  ·  OCT. 28, 2026"
CRED = ("Fire detections: NASA FIRMS (VIIRS, NOAA-21, NOAA-20, Suomi NPP), Oct. 28, 2026. Base image: contains modified "
        "Copernicus Sentinel data [2026] (Sentinel-2, Oct. 27, 2026, the day before the fire). Analysis: Prime Rogue Inc.")
CRED3D = CRED.replace("Analysis:", "Terrain: Copernicus DEM GLO-30 (© DLR/Airbus, ESA). Analysis:")
PASS = {"13:22": ((255, 70, 50), "1:22 p.m. NOAA-21"), "14:00": ((255, 150, 0), "2:00 p.m. Suomi NPP"),
        "14:20": ((255, 225, 0), "2:20 p.m. NOAA-20"), "15:04": ((255, 0, 200), "3:04 p.m. NOAA-21"),
        "15:41": ((0, 225, 255), "3:41 p.m. Suomi NPP")}
T = Transformer.from_crs(4326, 32619, always_xy=True)
TILES = {k: f"https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/19/T/{k}/2026/10/S2C_19T{k}_20261027_0_L2A/"
         for k in ("GL", "FL", "GM", "FM")}
FIRE = (-66.257, 45.749)


def s2(bounds, px, band="TCI", tiles=("GL",)):
    """Mosaic Sentinel-2 bands for UTM-19 bounds into a px x px array."""
    W, S_, E, N = bounds; out = np.zeros((3 if band == "TCI" else 1, px, px), np.float32)
    tf = rasterio.transform.from_bounds(W, S_, E, N, px, px)
    for t in tiles:
        with rasterio.open(TILES[t] + band + ".tif") as src:
            for b in range(out.shape[0]):
                tmp = np.zeros((px, px), np.float32)
                reproject(rasterio.band(src, b + 1), tmp, dst_transform=tf, dst_crs="EPSG:32619",
                          resampling=Resampling.average, src_nodata=0, dst_nodata=0)
                out[b] = np.where(out[b] == 0, tmp, out[b])
    return out


def stretch(a, lo=2, hi=98, g=1.0):
    v = a[a > 0]; l, h = np.percentile(v, (lo, hi)); return (np.clip((a - l) / (h - l), 0, 1) ** g * 255).astype(np.uint8)


def tci(bounds, px, tiles=("GL",), boost=1.35):
    a = s2(bounds, px, "TCI", tiles); return np.clip(a * boost, 0, 255).astype(np.uint8).transpose(1, 2, 0)


def P(bounds, px, lon, lat):
    E, N = T.transform(lon, lat); W, S_, Ea, Nn = bounds; s = px / (Ea - W); return ((E - W) * s, (Nn - N) * s)


def boxes(d, bounds, px, w=3, fill=False):
    s = px / (bounds[2] - bounds[0]); hp = max(187.5 * s, 3)
    for _, r in DET.iterrows():
        x, y = P(bounds, px, r.longitude, r.latitude); c = PASS[r.hm][0]
        if fill: d.rectangle([x - hp, y - hp, x + hp, y + hp], fill=c + (70,))
        d.rectangle([x - hp, y - hp, x + hp, y + hp], outline=c + (255,), width=w)


def legend(d, x, y, counts=True):
    d.rectangle([x, y, x + 470, y + 40 + 32 * len(PASS)], fill=pr.INK + (215,))
    d.text((x + 14, y + 10), "VIIRS FIRE DETECTIONS, OCT. 28 (ADT)", font=pr.B(17), fill=pr.GOLD)
    for i, (k, (c, lab)) in enumerate(PASS.items()):
        sub = DET[DET.hm == k]; yy = y + 42 + 32 * i
        d.rectangle([x + 16, yy, x + 38, yy + 20], outline=c, width=4)
        d.text((x + 50, yy - 1), f"{lab}: {len(sub)} · peak {sub.frp.max():.0f} MW", font=pr.M(18), fill=pr.CREAM)


def scalebar(d, bounds, px, x, y, m, lab):
    L = m * px / (bounds[2] - bounds[0]); d.rectangle([x - 10, y - 40, x + L + 10, y + 16], fill=pr.INK + (200,))
    d.rectangle([x, y, x + L, y + 8], fill=pr.CREAM); d.text((x, y - 32), lab, font=pr.B(18), fill=pr.CREAM)


def north(d, x, y):
    d.rectangle([x - 26, y - 8, x + 26, y + 84], fill=pr.INK + (200,))
    d.polygon([(x, y), (x - 14, y + 44), (x + 14, y + 44)], fill=pr.CREAM); d.text((x, y + 64), "N", font=pr.B(20), fill=pr.CREAM, anchor="mm")


def lbl(d, xy, t, col=pr.CREAM, dot=True, size=20, side="r"):
    x, y = xy
    if dot: d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=col, outline=pr.INK, width=3)
    pr.label(d, (x + 14, y - 15) if side == "r" else (x - 14, y - 15), t, col=col, size=size, anchor="la" if side == "r" else "ra")


def wrap(t, f, w):
    out, line = [], ""
    for word in t.split():
        test = (line + " " + word).strip()
        if ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(test, font=f) > w and line: out.append(line); line = word
        else: line = test
    return out + [line]


def panel(img, title, sub, notes, name, credit=CRED):
    W = img.width + 108
    subl = wrap(sub, pr.M(19), W - 120); notes = sum([wrap(n, pr.M(16.5), W - 230) for n in notes], [])
    cl = wrap(credit, pr.M(16.5), W - 230); notes = notes + cl[:-1]
    topH = 134 + 28 * len(subl) + 18; fh = 40 + 25 * (len(notes) + 1) + 44
    im, d = pr.canvas(W, img.height + topH + fh, KICK, title, "\n".join(subl))
    im.paste(img, (54, topH)); d = ImageDraw.Draw(im)
    d.rectangle([54, topH, 54 + img.width, topH + img.height], outline=pr.GOLD, width=2)
    pr.footer(im, notes + [cl[-1]], fh=fh)
    im.convert("RGB").save(f"{OUT}/{name}.jpg", quality=88); print(name, im.size)


if os.environ.get("ONLY")!="late":
  pass
# 1. Region: New Brunswick context
fE, fN = T.transform(*FIRE); b = (fE - 42000, fN - 30000, fE + 42000, fN + 44000)
px = 1400; b = (b[0], b[3] - (b[2] - b[0]), b[2], b[3])
im = Image.fromarray(tci(b, px, ("GL", "FL", "GM", "FM"), 1.5)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
x, y = P(b, px, *FIRE); d.ellipse([x - 26, y - 26, x + 26, y + 26], outline=pr.RED, width=6); d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=pr.RED)
pr.label(d, (x + 34, y - 18), "FIRE DETECTED OCT. 28", col=pr.RED, size=22)
for nm, la, lo, side in [("Fredericton", 45.9636, -66.6431, "r"), ("Oromocto (CFB Gagetown main base)", 45.8467, -66.4792, "r"),
                         ("Gagetown village", 45.7790, -66.1460, "r"), ("Saint John River", 45.88, -66.30, "r")]:
    if nm == "Saint John River": pr.label(d, P(b, px, lo, la), nm, col=pr.BLUE, size=17); continue
    lbl(d, P(b, px, lo, la), nm, side=side)
north(d, px - 60, 30); scalebar(d, b, px, 40, px - 40, 10000, "10 km")
panel(im, "A fire in the CFB Gagetown training area", "NASA satellites detected an active fire on the afternoon of Oct. 28, 2026, "
      "in the training area about 20 km south-east of Oromocto and 9–10 km west-south-west of Gagetown village, N.B.",
      ["Cause and status unconfirmed. Prime Rogue has asked the Department of National Defence for comment.",
       "The fire point is the centre of 35 VIIRS satellite detections (about 45.749 N, 66.260 W)."], "01-cfb-gagetown-fire-region")

# 2. Locator in the training area
b = (fE - 14000, fN - 11000, fE + 14000, fN + 17000); px = 1400
im = Image.fromarray(tci(b, px, ("GL", "FL"))).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA"); boxes(d, b, px, 3)
lbl(d, P(b, px, -66.1460, 45.7790), "Gagetown village", side="l")
d.rectangle([20, 20, 560, 62], fill=pr.INK + (215,)); d.text((34, 28), "← Oromocto and the main base: ~20 km WNW", font=pr.B(20), fill=pr.CREAM)
legend(d, 20, px - 230); north(d, px - 60, 30); scalebar(d, b, px, px - 300, px - 40, 5000, "5 km")
panel(im, "Where the fire was detected", "The detections fall in a large open clearing in the training area's forest, south-west of the Saint John River.",
      ["Boxes are VIIRS pixels (about 375 m across), coloured by satellite pass. Positions can shift a few hundred metres between passes."], "02-cfb-gagetown-fire-locator")

# 3, 4. Close-ups
b = (fE - 2500, fN - 2500, fE + 2500, fN + 2500); px = 1400
im = Image.fromarray(tci(b, 1400, ("GL",), 1.45)).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA"); boxes(d, b, px, 4)
legend(d, 20, px - 230); north(d, px - 60, 30); scalebar(d, b, px, px - 340, px - 40, 1000, "1 km")
panel(im, "Close-up: 35 detections in five passes", "Heat was detected across about 2.6 × 1.2 km of open ground, in a western group and a second group about 1.5 km east.",
      ["Image: Sentinel-2, Oct. 27, the day before the fire. It shows the ground, not the fire."], "03-cfb-gagetown-fire-closeup")
sw = np.dstack([stretch(s2(b, 700, k)[0]) for k in ("B12", "B8A", "B04")])
im = Image.fromarray(sw).resize((px, px), Image.LANCZOS).convert("RGBA"); d = ImageDraw.Draw(im, "RGBA"); boxes(d, b, px, 4)
legend(d, 20, px - 230); north(d, px - 60, 30); scalebar(d, b, px, px - 340, px - 40, 1000, "1 km")
panel(im, "The same ground in short-wave infrared", "In this false-colour view (bands 12, 8A, 4), dry, sparse vegetation shows pink and healthy forest green: "
      "the detections sit on the dry open ground.", ["Image: Sentinel-2, Oct. 27, 2026, the day before the fire."], "04-cfb-gagetown-fire-swir")

# 5. Pass-by-pass strip
b = (fE - 2200, fN - 1800, fE + 2200, fN + 2600); cell = 520
base = Image.fromarray(tci(b, cell, ("GL",), 1.45)).convert("RGBA")
strip = Image.new("RGBA", (cell * 3 + 2 * 14, 2 * (cell + 70) + 14), pr.BG + (255,))
for i, (k, (c, lab)) in enumerate(PASS.items()):
    t = base.copy(); dd = ImageDraw.Draw(t, "RGBA"); s = cell / (b[2] - b[0]); hp = 187.5 * s
    for _, r in DET[DET.hm == k].iterrows():
        x, y = P(b, cell, r.longitude, r.latitude); dd.rectangle([x - hp, y - hp, x + hp, y + hp], fill=c + (90,), outline=c + (255,), width=4)
    cx = (i % 3) * (cell + 14); cy = (i // 3) * (cell + 84)
    strip.paste(t, (cx, cy + 70)); sd = ImageDraw.Draw(strip)
    sub = DET[DET.hm == k]
    sd.text((cx + 6, cy + 4), lab, font=pr.B(24), fill=c); sd.text((cx + 6, cy + 36), f"{len(sub)} detections · peak {sub.frp.max():.1f} MW", font=pr.M(19), fill=pr.CREAM)
sd = ImageDraw.Draw(strip); cx, cy = 2 * (cell + 14), cell + 84
for j, line in enumerate(["Same 4.4 × 4.4 km box in each panel.", "Each square is one VIIRS pixel", "(about 375 m across).", "", "No satellite has passed since", "3:41 p.m. ADT. Next passes:", "overnight, about 1–3 a.m."]):
    sd.text((cx + 20, cy + 90 + 34 * j), line, font=pr.M(22), fill=pr.CREAM)
panel(strip, "Pass by pass: still going strong at 3 p.m.", "Each panel shows one satellite pass. The 3:04 p.m. NOAA-21 pass found more fire pixels than the same satellite's 1:22 p.m. pass, with a slightly higher peak.",
      ["The 3:41 p.m. Suomi NPP pass viewed the area at a steep angle and probably undercounts. No satellite has passed since; the next passes are overnight."], "05-cfb-gagetown-fire-passes")

# 6. Fire power by pass
from matplotlib import pyplot as plt
fig, ax = plt.subplots(figsize=(13, 6), dpi=110); fig.patch.set_facecolor(np.array(pr.BG) / 255); ax.set_facecolor(np.array(pr.PANEL) / 255)
xs = list(PASS)
ax.bar(range(5), [DET[DET.hm == k].frp.sum() for k in xs], color=[np.array(PASS[k][0]) / 255 for k in xs], width=0.6, label="total")
ax.plot(range(5), [DET[DET.hm == k].frp.max() for k in xs], "o-", color=np.array(pr.CREAM) / 255, lw=2.5, ms=10, label="peak pixel")
for i, k in enumerate(xs):
    ax.text(i, DET[DET.hm == k].frp.sum() + 4, f"{DET[DET.hm == k].frp.sum():.0f} MW\n({len(DET[DET.hm == k])} px)", ha="center", color=np.array(pr.CREAM) / 255, fontsize=13)
ax.set_xticks(range(5)); ax.set_xticklabels([PASS[k][1].replace(" ", "\n", 2) for k in xs], color=np.array(pr.CREAM) / 255, fontsize=12)
ax.tick_params(colors=np.array(pr.CREAM) / 255); [s.set_color(np.array(pr.MUTED) / 255) for s in ax.spines.values()]
ax.set_ylabel("Fire radiative power (MW)", color=np.array(pr.CREAM) / 255, fontsize=13); ax.set_ylim(0, 230)
h,l=ax.get_legend_handles_labels(); ax.legend(h,["sum of all pixels" if x=="total" else x for x in l], facecolor=tuple(np.array(pr.PANEL) / 255), labelcolor=tuple(np.array(pr.CREAM) / 255), fontsize=12)
fig.tight_layout(); fig.savefig(OUT + "/_chart.png", facecolor=fig.get_facecolor()); plt.close(fig)
panel(Image.open(OUT + "/_chart.png").convert("RGBA"), "Heat output by satellite pass", "Bars: total fire radiative power across all detected pixels. Line: the hottest single pixel.",
      ["Different satellites view at different angles, so totals are not strictly comparable between passes. Comparable pair: NOAA-21 at 1:22 and 3:04 p.m."], "06-cfb-gagetown-fire-power-chart",
      credit="Fire detections: NASA FIRMS (VIIRS), Oct. 28, 2026. Analysis: Prime Rogue Inc.")
os.remove(OUT + "/_chart.png")

# 7, 8. 3D views (Copernicus DEM + Sentinel-2 drape)
b = (fE - 4000, fN - 3500, fE + 4000, fN + 4500); n = 320
dem = np.zeros((n, n), np.float32); tf = rasterio.transform.from_bounds(*b, n, n)
with rasterio.open("https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N45_00_W067_00_DEM/Copernicus_DSM_COG_10_N45_00_W067_00_DEM.tif") as src:
    reproject(rasterio.band(src, 1), dem, dst_transform=tf, dst_crs="EPSG:32619", resampling=Resampling.bilinear)
tex = tci(b, n, ("GL",), 1.5).astype(float) / 255
xx = np.linspace(b[0], b[2], n) - fE; yy = np.linspace(b[3], b[1], n) - fN; X, Y = np.meshgrid(xx, yy)
from mpl_toolkits.mplot3d import Axes3D  # noqa
for name, az, ttl in [("07-cfb-gagetown-fire-3d-from-southwest", 225, "3D view from the south-west"), ("08-cfb-gagetown-fire-3d-from-north", 10, "3D view from the north")]:
    fig = plt.figure(figsize=(14, 9), dpi=110); fig.patch.set_facecolor(np.array(pr.BG) / 255)
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False); ax.set_facecolor(np.array(pr.BG) / 255)
    ax.plot_surface(X, Y, dem * 5, zorder=1, facecolors=tex, rstride=1, cstride=1, linewidth=0, antialiased=False, shade=False)
    for _, r in DET.iterrows():
        e, nn = T.transform(r.longitude, r.latitude); e -= fE; nn -= fN
        i = int(np.clip((b[3] - (nn + fN)) / (b[3] - b[1]) * n, 0, n - 1)); j = int(np.clip((e + fE - b[0]) / (b[2] - b[0]) * n, 0, n - 1))
        z0 = dem[i, j] * 5; ax.plot([e, e], [nn, nn], [z0, z0 + 150 + r.frp * 30], color=np.array(PASS[r.hm][0]) / 255, lw=5, zorder=10, solid_capstyle='round'); ax.scatter([e], [nn], [z0 + 150 + r.frp * 30], color=np.array(PASS[r.hm][0]) / 255, s=40, zorder=11, depthshade=False)
    ax.view_init(elev=30, azim=az); ax.set_axis_off(); ax.set_box_aspect((1, 1, 0.35), zoom=1.45)
    fig.subplots_adjust(0, 0, 1, 1); fig.savefig(OUT + "/_3d.png", facecolor=fig.get_facecolor()); plt.close(fig)
    im = Image.open(OUT + "/_3d.png").convert("RGBA"); w, h = im.size; im = im.crop((int(w * .04), int(h * .04), int(w * .96), int(h * .96)))
    d = ImageDraw.Draw(im, "RGBA"); legend(d, 16, 16)
    panel(im, ttl, "Satellite image of the day before draped over terrain (height exaggerated 5x). Each spike is one VIIRS detection; spike height shows its heat output.",
          ["About 8 × 8 km around the detections. The open clearing where the fire was detected is surrounded by forest."], name, credit=CRED3D)
    os.remove(OUT + "/_3d.png")
