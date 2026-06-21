import sys, os, gzip, json, urllib.request
import rasterio, numpy as np
from rasterio import features
from shapely.geometry import shape, mapping

DATE = sys.argv[1]
KEY = os.environ['STORM_KEY']
INGEST = os.environ['INGEST_URL']
d = DATE.replace('-', '')
base = "https://noaa-mrms-pds.s3.amazonaws.com/CONUS/MESH_Max_1440min_00.50/%s/" % d
fname = "MRMS_MESH_Max_1440min_00.50_%s-233000.grib2.gz" % d
tmp = "/tmp/mesh/_w_%s.grib2" % d
try:
    raw = urllib.request.urlopen(base + fname, timeout=90).read()
    open(tmp + '.gz', 'wb').write(raw)
    open(tmp, 'wb').write(gzip.open(tmp + '.gz', 'rb').read())
except Exception as e:
    print(DATE, "download-fail", e); sys.exit(0)

src = rasterio.open(tmp)
a = src.read(1).astype('float32')
a = np.where(a < 0, 0, a)
t = src.transform
polys = []
for mm in (19, 25, 32, 38, 45, 51, 64):
    mask = (a >= mm).astype('uint8')
    for geom, _ in features.shapes(mask, mask=mask > 0, transform=t):
        g = shape(geom)
        if g.area < 0.0004:
            continue
        g = g.simplify(0.01)
        if g.is_empty:
            continue
        mnx, mny, mxx, mxy = g.bounds
        polys.append({"mm": mm, "geojson": mapping(g),
                      "minlat": round(mny, 5), "maxlat": round(mxy, 5),
                      "minlng": round(mnx, 5), "maxlng": round(mxx, 5)})
for f in (tmp, tmp + '.gz'):
    try: os.remove(f)
    except Exception: pass

url2 = INGEST + ("&" if "?" in INGEST else "?") + "key=" + KEY
body = json.dumps({"date": DATE, "polys": polys}).encode()
req = urllib.request.Request(url2, data=body, method="POST",
        headers={"Content-Type": "application/json", "X-KN-Storm-Key": KEY, "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"})
try:
    r = urllib.request.urlopen(req, timeout=180).read().decode()
    print(DATE, "ok", len(polys), "polys", r[:160])
except Exception as e:
    eb = getattr(e, "read", lambda: b"")()
    print(DATE, "ingest-fail", e, eb[:200])
