from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source-prepped.png"
DATA = ROOT / "data"

def make_placeholder(path):
    im = Image.new("RGB", (220, 300), "white")
    d = ImageDraw.Draw(im)
    ink, light, gray = "#20252a", "#e0e4e7", "#777f87"
    d.ellipse((25,170,195,340), fill=light, outline=ink, width=4)
    d.rounded_rectangle((83,145,137,220), radius=12, fill="#eeeeee", outline=ink, width=3)
    d.ellipse((48,28,172,190), fill="#eeeeee", outline=ink, width=4)
    d.pieslice((43,12,177,145), 180, 360, fill=ink)
    d.polygon([(48,90),(70,45),(91,70),(112,39),(139,70),(169,47),(175,100),(150,113),(128,94),(105,113),(80,93),(61,111)], fill=ink)
    d.line((77,122,91,122), fill=ink, width=3)
    d.line((130,122,144,122), fill=ink, width=3)
    d.arc((91,125,130,158), 10, 170, fill=gray, width=3)
    im.save(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", help="Optional portrait image path")
    args = parser.parse_args()
    DATA.mkdir(exist_ok=True)
    if args.image:
        src = Path(args.image).expanduser()
        if not src.is_file():
            raise SystemExit(f"Image not found: {src}")
        im = Image.open(src).convert("RGB")
    else:
        make_placeholder(DATA / "placeholder-portrait.png")
        im = Image.open(DATA / "placeholder-portrait.png").convert("RGB")
    im = ImageOps.exif_transpose(im)
    im.thumbnail((220,300))
    canvas = Image.new("RGB", (220,300), "white")
    canvas.paste(im, ((220-im.width)//2, (300-im.height)//2))
    canvas = ImageOps.autocontrast(ImageOps.grayscale(canvas), cutoff=1)
    canvas = canvas.filter(ImageFilter.UnsharpMask(radius=2, percent=140, threshold=3))
    canvas.save(OUT)
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
