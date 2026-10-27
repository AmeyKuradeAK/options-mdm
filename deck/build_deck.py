"""Builds options_talk.pdf (4 slides, 1920x1080 pt, vector, fonts embedded)."""
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080

for name, f in [("Black", "ArchivoBlack-Regular.ttf"),
                ("Serif", "DMSerifDisplay-Italic.ttf"),
                ("Mono", "SpaceMono-Regular.ttf"),
                ("MonoB", "SpaceMono-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(name, os.path.join(HERE, "fonts", f)))

PAPER = HexColor("#F4EFE3")
SAND = HexColor("#E6DCC6")
GRID = HexColor("#DDD3BD")
INK = HexColor("#16130F")
ORANGE = HexColor("#FF4B1F")
CARD = HexColor("#FCFAF4")
MUTED = HexColor("#7A7263")


def Y(y):
    return H - y


def text(c, x, y, s, font, size, color=INK, anchor="l", spacing=0):
    c.setFont(font, size)
    c.setFillColor(color)
    w = pdfmetrics.stringWidth(s, font, size) + spacing * max(len(s) - 1, 0)
    if anchor == "r":
        x -= w
    elif anchor == "c":
        x -= w / 2
    # Always go through a text object and set char spacing explicitly:
    # PDF's Tc operator persists in the graphics state, so skipping it would
    # leak the previous call's spacing into this one.
    t = c.beginText(x, Y(y))
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(spacing)
    t.textOut(s)
    c.drawText(t)
    return w + spacing


def fit_size(s, font, max_w, start=400):
    size = start
    while pdfmetrics.stringWidth(s, font, size) > max_w:
        size -= 2
    return size


def background(c, ladder=True):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    if ladder:
        c.setStrokeColor(GRID)
        c.setLineWidth(1.5)
        for y in range(90, H, 90):
            c.line(0, Y(y), W, Y(y))


def tag(c, left, right):
    text(c, 100, 92, left, "MonoB", 24, INK, spacing=3)
    text(c, W - 100, 92, right, "Mono", 24, MUTED, anchor="r", spacing=3)


def payoff(c, x0, yflat, xk, x1, y1, lw=11):
    """Hockey-stick: flat to strike, then rising."""
    c.setStrokeColor(ORANGE)
    c.setLineWidth(lw)
    c.setLineCap(1)
    c.setLineJoin(1)
    p = c.beginPath()
    p.moveTo(x0, Y(yflat))
    p.lineTo(xk, Y(yflat))
    p.lineTo(x1, Y(y1))
    c.drawPath(p, stroke=1, fill=0)
    c.setFillColor(INK)
    c.circle(xk, Y(yflat), 22, stroke=0, fill=1)
    c.setFillColor(PAPER)
    c.circle(xk, Y(yflat), 9, stroke=0, fill=1)


def hard_card(c, x, y, w, h, off=16):
    c.setFillColor(INK)
    c.rect(x + off, Y(y + h) - off, w, h, stroke=0, fill=1)
    c.setFillColor(CARD)
    c.setStrokeColor(INK)
    c.setLineWidth(4)
    c.rect(x, Y(y + h), w, h, stroke=1, fill=1)


# ------------------------------------------------------------------ slide 1
def slide_intro(c):
    background(c)
    c.setFillColor(SAND)
    c.circle(1620, Y(330), 400, stroke=0, fill=1)
    tag(c, "FINANCE  /  A SHORT TALK", "01")

    size = fit_size("OPTIONS", "Black", 1130, 260)
    text(c, 92, 470, "OPTIONS", "Black", size)
    text(c, 92, 470 + size * 0.86, "TRADING", "Black", size, ORANGE)

    y = 880
    w = text(c, 100, y, "How people make millions... and ", "Serif", 62)
    text(c, 100 + w, y, "lose billions.", "Serif", 62, ORANGE)

    payoff(c, 1250, 900, 1470, 1840, 440)
    text(c, 1480, 965, "STRIKE", "MonoB", 22, INK, spacing=3)
    text(c, 1840, 400, "PROFIT", "MonoB", 22, ORANGE, anchor="r", spacing=3)
    text(c, 1250, 965, "LOSS CAPPED", "Mono", 22, MUTED, spacing=3)


# ------------------------------------------------------------------ slide 2
def slide_option(c):
    background(c)
    tag(c, "02  /  THE BASICS", "WHAT IS AN OPTION")

    text(c, 100, 250, "A coupon", "Black", 118)
    w = text(c, 100, 395, "for the ", "Black", 118)
    text(c, 100 + w, 395, "future.", "Serif", 150, ORANGE)

    # receipt card
    cx, cy, cw, ch = 100, 480, 700, 360
    hard_card(c, cx, cy, cw, ch)

    def row(y, label, val):
        dots = 33 - len(label) - len(val)
        text(c, cx + 36, y, label + " " + "." * max(dots - 2, 2) + " " + val,
             "Mono", 29)

    row(cy + 78, "STOCK TODAY", "$100")
    row(cy + 138, "YOU PAY", "$5")
    c.setStrokeColor(INK)
    c.setLineWidth(3)
    c.setDash(10, 8)
    c.line(cx + 36, Y(cy + 180), cx + cw - 36, Y(cy + 180))
    c.setDash()
    text(c, cx + 36, cy + 238, "YOU GET", "MonoB", 29, ORANGE, spacing=2)
    text(c, cx + 36, cy + 282, "THE RIGHT TO BUY AT $100", "MonoB", 29)
    text(c, cx + 36, cy + 330, "WORST CASE: LOSE THE $5", "Mono", 29, MUTED)

    # payoff chart
    px = lambda p: 960 + (p - 90) * 28
    zero = 600
    py = lambda v: zero - v * 22
    c.setStrokeColor(INK)
    c.setLineWidth(3)
    c.line(px(90), Y(zero), px(120), Y(zero))

    # profit area
    c.saveState()
    c.setFillColor(ORANGE)
    c.setFillAlpha(0.22)
    p = c.beginPath()
    p.moveTo(px(105), Y(zero))
    p.lineTo(px(120), Y(py(15)))
    p.lineTo(px(120), Y(zero))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFillAlpha(0.10)
    p = c.beginPath()
    p.moveTo(px(90), Y(zero))
    p.lineTo(px(105), Y(zero))
    p.lineTo(px(100), Y(py(-5)))
    p.lineTo(px(90), Y(py(-5)))
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()

    payoff(c, px(90), py(-5), px(100), px(120), py(15), lw=10)

    # breakeven marker
    c.setFillColor(INK)
    c.circle(px(105), Y(zero), 10, stroke=0, fill=1)
    text(c, px(105), zero - 28, "BREAKEVEN $105", "MonoB", 22, INK, anchor="c", spacing=2)
    text(c, px(120), py(15) - 30, "UNLIMITED UPSIDE", "MonoB", 22, ORANGE, anchor="r", spacing=2)
    text(c, px(90), py(-5) + 60, "MAX LOSS = $5", "MonoB", 22, MUTED, spacing=2)
    for p_ in (90, 100, 110, 120):
        text(c, px(p_), 800, "$%d" % p_, "Mono", 22, MUTED, anchor="c")
    text(c, px(105), 840, "PRICE AT EXPIRY", "Mono", 20, MUTED, anchor="c", spacing=3)

    # three uses
    y = 960
    c.setStrokeColor(INK)
    c.setLineWidth(3)
    c.line(100, Y(y - 50), W - 100, Y(y - 50))
    cols = [(100, "SPECULATE", "bet on direction"),
            (700, "HEDGE", "insurance for stocks"),
            (1300, "EARN", "sell coupons, collect fees")]
    for i, (x, big, small) in enumerate(cols):
        c.setFillColor(ORANGE if i == 0 else INK)
        if i == 0:      # triangle
            p = c.beginPath()
            p.moveTo(x, Y(y + 22)); p.lineTo(x + 52, Y(y + 22)); p.lineTo(x + 26, Y(y - 24))
            p.close(); c.drawPath(p, stroke=0, fill=1)
        elif i == 1:    # ring
            c.setStrokeColor(INK); c.setLineWidth(10)
            c.circle(x + 26, Y(y), 22, stroke=1, fill=0)
        else:           # square
            c.setFillColor(ORANGE)
            c.rect(x, Y(y + 24), 48, 48, stroke=0, fill=1)
        text(c, x + 80, y + 2, big, "Black", 40)
        text(c, x + 80, y + 38, small, "Mono", 22, MUTED)


# ------------------------------------------------------------------ slide 3
def slide_scams(c):
    background(c, ladder=False)
    # ghost grid for lower half
    c.setStrokeColor(GRID)
    c.setLineWidth(1.5)
    for x in range(0, W, 90):
        c.line(x, Y(580), x, 0)
    for y in range(580, H, 90):
        c.line(0, Y(y), W, Y(y))

    # orange band
    c.setFillColor(ORANGE)
    c.rect(0, Y(580), W, 440, stroke=0, fill=1)
    text(c, 100, 92, "03  /  THE SCAMS", "MonoB", 24, INK, spacing=3)
    text(c, W - 100, 92, "THE STORIES", "Mono", 24, INK, anchor="r", spacing=3)

    s1 = fit_size("MADOFF", "Black", 1720, 330)
    text(c, 88, 500, "MADOFF", "Black", s1, PAPER)

    s2 = fit_size("JANE STREET", "Black", 1740, 330)
    text(c, 88, 580 + 90 + s2 * 0.72 + 60, "JANE STREET", "Black", s2, INK)

    text(c, 100, 1020, "ALLEGED BY SEBI  /  DENIED BY THE FIRM  /  CASE ONGOING",
         "Mono", 22, MUTED, spacing=2)


# ------------------------------------------------------------------ slide 4
def slide_thanks(c):
    background(c)
    c.setFillColor(SAND)
    c.circle(1560, Y(760), 430, stroke=0, fill=1)
    tag(c, "04  /  THE END", "OPTIONS TRADING")

    size = fit_size("THANK", "Black", 1250, 300)
    text(c, 92, 440, "THANK", "Black", size)
    text(c, 92, 440 + size * 0.86, "YOU", "Black", size, ORANGE)

    text(c, 100, 880, "Questions?", "Serif", 90)
    text(c, 100, 1005, "Not financial advice. Coupons can expire worthless.",
         "Mono", 22, MUTED, spacing=2)

    payoff(c, 1330, 930, 1530, 1840, 520)


def main():
    out = os.path.join(HERE, "options_talk.pdf")
    c = canvas.Canvas(out, pagesize=(W, H))
    c.setTitle("Options Trading")
    for fn in (slide_intro, slide_option, slide_scams, slide_thanks):
        fn(c)
        c.showPage()
    c.save()
    print(out)


if __name__ == "__main__":
    main()
