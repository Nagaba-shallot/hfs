import argparse
import sys

import qrcode

from hospital_feedback_system.database import SessionLocal
from hospital_feedback_system.models.department import Department


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("department_name", help="Exact department name, e.g. 'Cardiology'")
    parser.add_argument(
        "--base-url",
        default="http://localhost:5173",
        help="Frontend base URL that will handle the scan (default: %(default)s)",
    )
    parser.add_argument("--out", default=None, help="Output PNG path (default: <name>_qr.png)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        department = db.query(Department).filter_by(name=args.department_name).first()
        if department is None:
            print(f"No department named {args.department_name!r} found.", file=sys.stderr)
            return 1

        scan_url = f"{args.base_url.rstrip('/')}/qr-scan/{department.qr_code_token}"
        img = qrcode.make(scan_url)
        out_path = args.out or f"{args.department_name.lower().replace(' ', '_')}_qr.png"
        img.save(out_path)
        print(f"Saved {out_path}")
        print(f"Encodes: {scan_url}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())