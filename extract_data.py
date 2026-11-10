
import csv
import datetime as dt
import os
import sys

from pptx import Presentation


def main(pptx_path: str, out_path: str = "data/kghm.csv") -> None:
    if not os.path.isfile(pptx_path):
        raise SystemExit(
            f"File not found: {os.path.abspath(pptx_path)}\n"
            "Put Futures.pptx next to this script or pass its full path as an argument."
        )

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

    prs = Presentation(pptx_path)
    for shape in prs.slides[3].shapes:
        if shape.has_chart:
            plot = shape.chart.plots[0]
            dates = list(plot.categories)
            spot, fut = [list(s.values) for s in plot.series]
            with open(out_path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["date", "spot", "src"])
                for c, s, ft in zip(dates, spot, fut):
                    # Excel serial date -> ISO date
                    d = dt.date(1899, 12, 30) + dt.timedelta(days=int(float(c)))
                    w.writerow([d.isoformat(), s, ft])
            print(f"Wrote {len(dates)} rows to {out_path}")
            return
    raise SystemExit("No chart found on slide 4")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\YourName\Downloads\Futures.pptx")