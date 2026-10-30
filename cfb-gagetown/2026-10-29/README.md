# CFB Gagetown fire: Oct. 29, 2026 (overnight and daytime checks)

Pulled 07:30 UTC (4:30 a.m. ADT) with `scripts/pull_firms.py`, covering the last 2 days. All times ADT (UTC−3).

**Still burning overnight, at a much lower level.** NOAA-20's night pass at **4:15 a.m. ADT** detected **2 fire pixels** at 45.742–45.745 N, 66.257–66.259 W. Peak fire radiative power was **1.7 MW** (nominal confidence). Both pixels are inside the area that burned on the afternoon of Oct. 28, about 0.5–0.75 km from the reference point (45.749 N, 66.260 W), at its southern side. That compares with peaks of 30–31.5 MW the previous afternoon: smouldering or a small residual front, not an active run. No other overnight VIIRS detections (Suomi NPP, NOAA-21) are in the feed so far.

The re-pull also returns all 35 detections from Oct. 28 (1:22–3:41 p.m. ADT), unchanged.

**Base statement.** CFB Gagetown posted a statement on Instagram on the evening of Oct. 28, about 9:49 p.m. ADT. It said a wildfire is burning in the northeastern sector of the training area, actively monitored by Wildland Fire Management Service, with no threat to nearby communities, and that training in the vicinity was suspended. Contact: Capt. Robynn Still, GagePublicAffairs@forces.gc.ca.

Files: `firms/raw/` holds the unaltered FIRMS responses; `firms/detections_2026-10-29T0730Z.csv` is the merged table.

## Daytime check (pulled 20:46 UTC, 5:46 p.m. ADT)

Pulled with `scripts/pull_firms.py`, covering the last day. All times ADT.

**Still burning on the afternoon of Oct. 29, at roughly a third of Oct. 28's intensity.** Five VIIRS passes between 1:05 and 3:21 p.m. ADT detected fire every time: **13 daytime fire pixels** (corrected Oct. 30 from 15; the table below sums to 13), with a peak fire radiative power of **12.0 MW**.

| Pass (ADT) | Satellite | Pixels | Peak FRP (MW) |
| --- | --- | --- | --- |
| 1:05 p.m. | NOAA-21 | 2 | 12.0 |
| 1:39 p.m. | Suomi NPP | 2 | 9.0 |
| 2:00 p.m. | NOAA-20 | 3 | 8.1 |
| 2:43 p.m. | NOAA-21 | 5 | 11.5 |
| 3:21 p.m. | Suomi NPP | 1 | 4.8 |

For comparison: Oct. 28 afternoon, 35 pixels with a peak of 31.5 MW; overnight, 2 pixels with a peak of 1.7 MW.

**Where.** All of today's pixels sit at 45.738–45.745 N, 66.250–66.264 W, 0.5–1.2 km from the reference point (45.749 N, 66.260 W). That is at, and up to about 0.8 km south of, the southern edge of the Oct. 28 detections, which reached 45.743–45.755 N. This may be slow spread to the south, but VIIRS pixels are about 375 m across, so treat it as an indication only. It needs confirming against Sentinel-2 or Landsat.

**Correction to the overnight note.** The late-arriving Suomi NPP data adds 2 more night pixels, at 3:57 a.m. ADT (peak 1.1 MW), alongside NOAA-20's 2 pixels at 4:15 a.m.

Files: `firms/raw/*_2026-10-29T2046Z_1d.csv` (unaltered FIRMS responses) and `firms/detections_2026-10-29T2046Z.csv` (merged table).

## Base response (Oct. 29)

CFB Gagetown public affairs (Capt. Robynn Still) answered Prime Rogue's questions in writing:
- **Cause:** "The wildfire was started by artillery shooting into Lawfield Impact Area."
- **Timing:** reported to Range Control at 12:22 p.m. on Oct. 28; training restrictions from 12:15 p.m.
- **Training under way:** Royal Canadian Artillery School Forward Observation Officer course, 105 mm LG1 howitzer.
- **Conditions and size:** fire-danger rating Moderate; about 25 ha burned and about 12 ha active on Oct. 29.
- **Safety:** no injuries and no evacuations.
- **Response:** WFMS is leading, with helicopter bucketing and a 4 ESR armoured dozer. Unexploded ordnance limits some suppression methods.

National Defence declined to comment on an earlier set of questions. Article: [`../../article/`](../../article/cfb-gagetown-fire-artillery-lawfield-impact-area.md).
