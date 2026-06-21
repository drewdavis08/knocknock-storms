# knocknock-storms

Daily worker that turns NOAA **MRMS MESH** (`MESH_Max_1440min`, radar-derived hail size)
into hail-swath polygons and posts them to KnocKnock's `/storm/swaths/ingest` endpoint.

- `process_mesh.py <YYYY-MM-DD>` — downloads that day's MESH GRIB2 from the NOAA open S3
  bucket, contours it at 1″/1.5″/2″ thresholds (GDAL/rasterio), and POSTs the polygons.
- `.github/workflows/daily.yml` — runs daily, processing the last few days (idempotent).

Secrets: `STORM_KEY` (ingest shared secret), `INGEST_URL`.
