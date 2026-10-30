# CFB Gagetown (5th Canadian Division Support Base Gagetown), N.B.: fire on Oct. 28, 2026

Prime Rogue Inc. · first pull Oct. 28, 2026, 23:57 UTC (8:57 p.m. ADT) · times ADT (UTC−3) unless marked

## What the satellites show

On Oct. 28, NASA FIRMS has **35 VIIRS fire detections from five satellite passes**, all within about 1.7 km of **45.749 N, 66.260 W**. That's in the training area, about 9–10 km WSW of Gagetown village and about 20 km SE of Oromocto. There were no detections in the area on Oct. 27, and the MODIS and Landsat feeds have none on either day.

| Pass (ADT) | UTC | Satellite | Detections | Peak fire radiative power |
|---|---|---|---|---|
| 1:22 p.m. | 16:22 | NOAA-21 | 6 | 30.5 MW |
| 2:00 p.m. | 17:00 | Suomi NPP | 7 | 7.4 MW |
| 2:20 p.m. | 17:20 | NOAA-20 | 9 | 16.6 MW |
| 3:04 p.m. | 18:04 | NOAA-21 | 12 | 31.5 MW (two detections at high confidence) |
| 3:41 p.m. | 18:41 | Suomi NPP | 1 | 19.1 MW (wide view angle, so probably undercounted) |

- **How big:** the detections span about 2.6 km east to west (66.237–66.272 W) and about 1.2 km north to south (45.743–45.755 N). VIIRS pixels are about 375 m across, so this is the area where heat was detected, not a burn outline.
- **How it changed:** the fire was at least as strong at 3:04 p.m. as at 1:22 p.m., so it had not died down. A second group of detections at the east end (around 66.24 W) appears in every pass from 1:22 p.m. on. Treat any apparent spread with caution: each pass views the ground from a different angle, and pixel positions shift by a few hundred metres.
- **What kind of ground:** the Sentinel-2 image from the day before (Oct. 27, clear) shows the detections inside a large open, cleared area of heath and brush with tracks across it, surrounded by forest. In the SWIR (short-wave infrared) image it shows as bright, dry, sparsely vegetated ground.
- **Not established:** whether this was a planned (prescribed) burn or a fire started by training, and whether it is still burning. See the next section.

> **Correction, Oct. 30.** The paragraph below says GOES-19 never flagged the site. That is wrong. A five-minute GOES-19 series built by Roger Wilco Media from the same NOAA fire product (CONUS scans) shows fire pixels from **12:46 p.m. to 3:41 p.m. ADT**, peaking at **112 MW at 3:26 p.m.** The area was mostly cloud-coded, so GOES saw the fire through gaps. The series is in [`../goes/goes_fire_2026-10-28_29.csv`](../goes/goes_fire_2026-10-28_29.csv). The base later said the fire was reported to Range Control at 12:22 p.m.

## Is it still burning?

**Unknown as of the first pull.** The last detection was at 3:41 p.m. ADT. No polar-orbiting satellite has passed over since. The next VIIRS passes are at night, around 1–3 a.m. ADT, and FIRMS usually posts them within about three hours.

GOES-East cannot answer this question. GOES-19's fire product (CONUS, every 5 min) never flagged the site from noon to 8:41 p.m. ADT, even when VIIRS was measuring about 30 MW. It recorded the site as clear and processed, with no fire. The fire is too small for GOES's roughly 2 km pixels, so the absence of a GOES detection says nothing about whether the fire is out.

## Files

| Path | What |
|---|---|
| `firms/raw/` | Unaltered NASA FIRMS area-API responses (VIIRS NOAA-21, NOAA-20, S-NPP, MODIS, Landsat) for the box 66.6–65.9 W, 45.55–46.0 N, last 2 days. The `_2026-10-28_2d` files are the first pull (about 23:45 UTC); the `_2026-10-28T2357Z_2d` files are the re-pull by `scripts/pull_firms.py`. |
| `firms/detections_2026-10-28T2357Z.csv` | All detections merged, with UTC and ADT times and the distance from 45.749 N, 66.260 W |
| `maps/cfb-gagetown-fire-2026-10-28-locator.jpg` | Where it is: the training area, Gagetown village, Oromocto (off map) |
| `maps/cfb-gagetown-fire-2026-10-28-closeup-truecolour.jpg` | Close-up, true colour, with every detection by pass |
| `maps/cfb-gagetown-fire-2026-10-28-closeup-swir.jpg` | Same, SWIR false colour (B12/B8A/B4) |
| `maps/branded/01–08` | Branded set for publication: region, locator, close-up, SWIR, pass by pass, heat-output chart, two 3D views (Copernicus DEM GLO-30 terrain). Code: `scripts/build_brand_gagetown_2026-10-28.py` |
| `maps/sentinel2_2026-10-27_assets.txt` | Source scene: S2C_19TGL_20261027_0_L2A (Element 84 Earth Search, AWS open data), 0.08% cloud |

Code: `scripts/pull_firms.py` (needs `FIRMS_MAP_KEY` in the environment; the key is never stored) and `scripts/make_maps_gagetown_2026-10-28.py`.

## Imagery available

- **Sentinel-2:** Oct. 27 is clear (pre-fire). Oct. 22 and Oct. 17 are cloudy. The next pass could give the first post-fire picture.
- **Landsat:** Landsat 9 on Oct. 23 (31% cloud) and Landsat 8 on Oct. 15 (24% cloud) are pre-fire scenes. No post-fire scene yet.

## To do

1. Re-pull FIRMS after the night passes (1–3 a.m. ADT) and on Oct. 29.
2. Check the next clear Sentinel-2 or Landsat pass for a burn scar, and map it.
3. Check the place name "Petersville" against official mapping; it isn't verified here.
4. Look for a planned burn or range notice from 5th Canadian Division Support Base Gagetown, and check New Brunswick's fire information.
5. Request for comment to DND / Base Gagetown: was this a planned burn or a training fire, was anyone hurt, and was it contained?

## Licences and credits

NASA FIRMS (LANCE) data: NASA open data. Sentinel-2: "Contains modified Copernicus Sentinel data [2026]". Terrain: Copernicus DEM GLO-30 (© DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018, provided under COPERNICUS by the European Union and ESA). Prime Rogue's tables, maps and text: CC BY-NC 4.0, credit "Prime Rogue Inc." Code: MIT.
