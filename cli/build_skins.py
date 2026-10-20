"""Build the Pantheon skins for Hermes in the terminal (the `hermes` CLI and TUI).

Reads the eighteen themes packed into desktop/plugin.js and writes one skin per
god to cli/skins/<name>.yaml:

- banner_hero: the god's bust from the top of the Desktop sidebar, in braille,
  in the start panel's left column. The panel is already as tall as its tool
  and skill lists, so the bust costs no extra rows; above the panel there is
  only room for the lettering before art would scroll away. The bust, not the
  wide new-session scene: a terminal has too few cells for the scene's figures.
- banner_logo: the HERMES AGENT lettering of the stock banner in the god's colours.
- colors / light_colors: the god's palette for dark and for light terminals,
  every colour checked for readable contrast against that terminal ground.

The TUI draws each `[#colour]...[/]` run on a line of its own, so every row of
art carries exactly one colour; the dithered marble survives as braille dots.

Usage: python3 cli/build_skins.py  (needs Pillow)
"""

import base64
import colorsys
import io
import json
import re
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "cli" / "skins"

# Nominal terminal grounds the palettes are checked against.
DARK_GROUND = "#1c1c1c"
LIGHT_GROUND = "#ffffff"

# Bust size in terminal cells (one braille cell is 2x4 dots). The TUI gives the
# hero column at most 40% of the width, so 44 columns stay whole from 120 up.
HERO_MAX = (44, 17)

BLANK = "⠀"  # empty braille cell: keeps spacing, never trimmed as whitespace

# The HERMES AGENT lettering of the stock banner, recoloured per god.
LETTERING = [
    "██╗  ██╗███████╗██████╗ ███╗   ███╗███████╗███████╗       █████╗  ██████╗ ███████╗███╗   ██╗████████╗",
    "██║  ██║██╔════╝██╔══██╗████╗ ████║██╔════╝██╔════╝      ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝",
    "███████║█████╗  ██████╔╝██╔████╔██║█████╗  ███████╗█████╗███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║",
    "██╔══██║██╔══╝  ██╔══██╗██║╚██╔╝██║██╔══╝  ╚════██║╚════╝██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║",
    "██║  ██║███████╗██║  ██║██║ ╚═╝ ██║███████╗███████║      ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║",
    "╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝╚══════╝      ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝",
]

# Braille dot bit for each (x, y) inside a 2x4 cell.
DOTS = {(0, 0): 0x01, (0, 1): 0x02, (0, 2): 0x04, (0, 3): 0x40,
        (1, 0): 0x08, (1, 1): 0x10, (1, 2): 0x20, (1, 3): 0x80}


# ── Colour helpers ──────────────────────────────────────────────────────────

def rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c[:3])


def luminance(c):
    def channel(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def readable(hex_color, ground, ratio):
    """Nudge a colour's lightness, keeping its hue, until it reads on `ground`."""
    c, g = rgb(hex_color), rgb(ground)
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    step = 0.02 if luminance(g) < 0.5 else -0.02
    while contrast(c, g) < ratio and 0 <= l <= 1:
        l = min(1, max(0, l + step))
        c = tuple(v * 255 for v in colorsys.hls_to_rgb(h, l, s))
        if l in (0, 1):
            break
    return hexc(c)


def mix(a, b, t):
    ca, cb = rgb(a), rgb(b)
    return hexc(tuple(x + (y - x) * t for x, y in zip(ca, cb)))


def stop(value):
    """`#rrggbb 45%` (a wordmark gradient stop) -> `#rrggbb`."""
    return value.split()[0]


# ── Palettes ────────────────────────────────────────────────────────────────

def palette(theme, ground):
    """Skin colours for one terminal polarity, built from the god's Desktop palette."""
    c, v = theme["colors"], theme["vars"]
    dark_terminal = luminance(rgb(ground)) < 0.5
    # On a dark terminal text takes the god's lightest tone and fills its darkest; reversed on light.
    pick, shade = (max, min) if dark_terminal else (min, max)
    lum = lambda x: luminance(rgb(x))  # noqa: E731

    text = pick(c["background"], c["foreground"], key=lum)
    fill = shade(c["background"], c["foreground"], key=lum)
    title = pick((stop(s) for s in v["wordmark"]), key=lum)
    accent, rule = c["ring"], v["rule"]

    fg = lambda color, ratio=4.5: readable(color, ground, ratio)  # noqa: E731
    return {
        "banner_border": fg(rule, 3), "banner_title": fg(title), "banner_accent": fg(accent),
        "banner_dim": fg(v["dim"], 3), "banner_text": fg(text), "ui_accent": fg(accent),
        "ui_label": fg(mix(title, accent, 0.35)), "ui_ok": fg("#4caf50"), "ui_error": fg(c["destructive"]),
        "ui_warn": fg("#e0a030"), "prompt": fg(text), "input_rule": fg(rule, 3),
        "response_border": fg(title, 3),
        # Fills: the status bar and menus sit on the god's own ground.
        "status_bar_bg": fill, "status_bar_text": readable(text, fill, 4.5),
        "status_bar_strong": readable(title, fill, 4.5), "status_bar_dim": readable(v["dim"], fill, 3),
        "status_bar_good": readable("#4caf50", fill, 3), "status_bar_warn": readable("#e0a030", fill, 3),
        "status_bar_bad": readable(c["destructive"], fill, 3), "status_bar_critical": readable("#ef5350", fill, 3),
        "session_label": fg(accent), "session_border": fg(rule, 2),
        "completion_menu_bg": fill, "completion_menu_current_bg": mix(fill, accent, 0.3),
        "selection_bg": mix(fill, text, 0.25), "shell_dollar": fg(accent), "voice_status_bg": fill,
    }


# ── Braille art ─────────────────────────────────────────────────────────────

def decode(data_uri):
    return Image.open(io.BytesIO(base64.b64decode(data_uri.split(",", 1)[1]))).convert("RGBA")


def tone_map(img):
    """Grey map: 255 where the marble is brightest, 0 where it is empty.

    Dot density follows the marble's light, so highlights stay dense and the
    shadows of light themes (dark ink meant for a pale page) thin out instead
    of turning into bright dots on a dark terminal.
    """
    alpha = img.getchannel("A")
    inks = [luminance(px) for _, px in (img.getcolors(1 << 16) or []) if px[3]]
    top = max(inks) if inks else 1
    grey = Image.new("L", img.size)
    src, out = img.load(), grey.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = src[x, y]
            out[x, y] = round(a * (luminance((r, g, b)) / top) ** 0.6) if a else 0
    return grey, alpha


def continuous(grey):
    """Undo the source dithering: soften it into tone, then stretch to the full range."""
    grey = grey.filter(ImageFilter.GaussianBlur(1.2))
    values = sorted(v for v in grey.get_flattened_data() if v > 8)
    top = values[int(len(values) * 0.9)] if values else 255
    return grey.point(lambda v: 0 if v <= 8 else min(255, round(255 * (v / top) ** 0.65)))


def braille(img, max_cells, ground):
    """Render RGBA art as rows of (colour, braille text), one colour per row."""
    box = img.getchannel("A").getbbox()
    img = img.crop(box)
    # A terminal cell is about twice as tall as wide, so its 2x4 dots are square.
    max_w, max_h = max_cells[0] * 2, max_cells[1] * 4
    scale = min(max_w / img.width, max_h / img.height)
    size = (max(2, round(img.width * scale / 2) * 2), max(4, round(img.height * scale / 4) * 4))

    grey, _ = tone_map(img)
    grey = continuous(grey).resize(size, Image.LANCZOS)
    # Terminal braille dots are tiny, so rows lean towards the marble's lit tone.
    inks = [px for _, px in (img.getcolors(1 << 16) or []) if px[3]]
    lit = hexc(max(inks, key=luminance)) if inks else "#ffffff"
    dots = grey.convert("1", dither=Image.Dither.FLOYDSTEINBERG).load()
    colour_src = img.resize(size, Image.BOX).load()

    rows = []
    for cy in range(size[1] // 4):
        cells, weight, acc = [], 0, [0.0, 0.0, 0.0]
        for cx in range(size[0] // 2):
            code = 0
            for (dx, dy), bit in DOTS.items():
                x, y = cx * 2 + dx, cy * 4 + dy
                if dots[x, y]:
                    code |= bit
                    r, g, b, a = colour_src[x, y]
                    if a:
                        acc = [s + v * a for s, v in zip(acc, (r, g, b))]
                        weight += a
            cells.append(chr(0x2800 + code) if code else BLANK)
        colour = hexc([s / weight for s in acc]) if weight else None
        rows.append((readable(mix(colour, lit, 0.5), ground, 4.5) if colour else None, "".join(cells)))

    # Drop empty rows at either end, keep inner gaps.
    while rows and rows[0][0] is None:
        rows.pop(0)
    while rows and rows[-1][0] is None:
        rows.pop()
    fallback = next((c for c, _ in rows if c), "#ffffff")
    return [(c or fallback, text) for c, text in rows]


def markup(rows):
    return "\n".join(f"[{colour}]{text}[/]" for colour, text in rows)


def lettering(theme, ground):
    stops = [readable(stop(s), ground, 4.5) for s in theme["vars"]["wordmark"]]
    # Top rows take the first stop, bottom rows the last, like the Desktop gradient.
    picks = [stops[i * len(stops) // len(LETTERING)] for i in range(len(LETTERING))]
    return "\n".join(f"[bold {colour}]{line}[/]" for colour, line in zip(picks, LETTERING))


# ── YAML output ─────────────────────────────────────────────────────────────

def block(key, text, indent="  "):
    return f"{key}: |-\n" + "\n".join(indent + line for line in text.splitlines())


def mapping(key, values):
    return f"{key}:\n" + "\n".join(f'  {k}: "{v}"' for k, v in values.items())


def skin_yaml(theme):
    logo = lettering(theme, DARK_GROUND)
    hero = markup(braille(decode(theme["art"]["top"]), HERO_MAX, DARK_GROUND))
    description = f"Pantheon: {theme['description']}"
    return "\n".join([
        "# Generated by cli/build_skins.py from desktop/plugin.js. Do not edit by hand.",
        f"name: {theme['name']}",
        f'description: "{description}"',
        mapping("colors", palette(theme, DARK_GROUND)),
        mapping("light_colors", palette(theme, LIGHT_GROUND)),
        block("banner_logo", logo),
        block("banner_hero", hero),
        "",
    ])


def themes():
    src = (ROOT / "desktop" / "plugin.js").read_text(encoding="utf-8")
    start = src.index("const THEMES = ") + len("const THEMES = ")
    end = src.index("\n]\n", start) + 2
    return json.loads(src[start:end])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in themes():
        if not re.fullmatch(r"[a-z]+", theme["name"]):
            raise SystemExit(f"unexpected theme name: {theme['name']!r}")
        (OUT / f"{theme['name']}.yaml").write_text(skin_yaml(theme), encoding="utf-8")
        print(f"cli/skins/{theme['name']}.yaml")


if __name__ == "__main__":
    main()
