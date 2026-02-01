import os
import zipfile
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO_ROOT, "dist")

INCLUDE = [
    "index.html",
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_zip = os.path.join(OUT_DIR, f"btc-receive-{ts}.zip")

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in INCLUDE:
            src = os.path.join(REPO_ROOT, rel)
            if not os.path.isfile(src):
                raise FileNotFoundError(src)
            z.write(src, arcname=rel)

    print(out_zip)


if __name__ == "__main__":
    main()
