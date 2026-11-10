"""Génère le campus virtuel Eiffel (ECE / INSEEC) pour WorkAdventure.

Cartes produites :
  quartier.tmj          le quartier Campus Eiffel (point d'arrivée), avec les 4 bâtiments
  eiffel1.tmj … 4.tmj   l'intérieur de chaque bâtiment
  tileset.png           les tuiles graphiques (partagées)
  salles.json           la liste des salles à code / à tableau (lue par le serveur)
  apercu-*.png          un aperçu de chaque carte

Usage :  python tools/generate.py
Les plans intérieurs sont INVENTÉS (les vrais plans ne sont pas publics) : il suffit de modifier
la description des bâtiments plus bas pour les rapprocher de la réalité.
"""
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
T = 32
COLS = 8
NAVY = (18, 38, 82)
CYAN = (0, 170, 200)
INSEEC = (196, 30, 58)   # couleur d'accent des bâtiments INSEEC

random.seed(42)

# ================================================================ tuiles ====
TILES, ID = [], {}
COLLIDES = {"wall", "desk", "tree", "plant", "table", "board", "sign", "shelf", "sofa", "counter",
            "coffee", "pc", "workbench", "bigtable", "roof", "facade", "water", "parkbench"}


def tid(name):
    """Identifiant Tiled (gid) d'une tuile, créée à la demande."""
    if name not in ID:
        ID[name] = len(TILES)
        TILES.append(name)
    return ID[name] + 1


def font(size):
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def noise_fill(d, base, var=10, n=40):
    d.rectangle([0, 0, T - 1, T - 1], fill=base)
    for _ in range(n):
        x, y = random.randrange(T), random.randrange(T)
        d.point((x, y), fill=tuple(max(0, min(255, v + random.randint(-var, var))) for v in base))


_plaques_cache = {}


def plaque_image(texte, n, style):
    key = (texte, n, style)
    if key not in _plaques_cache:
        fond = {"mur": (120, 126, 140), "facade": (205, 196, 178), "toit": (92, 98, 112)}[style]
        bord = INSEEC if "INSEEC" in texte else NAVY
        img = Image.new("RGBA", (n * T, T), fond)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([2, 5, n * T - 3, T - 6], 4, fill="white", outline=bord, width=2)
        f = font(12)
        while d.textlength(texte, font=f) > n * T - 10 and f.size > 8:
            f = font(f.size - 1)
        d.text(((n * T - d.textlength(texte, font=f)) / 2, (T - f.size) / 2 - 1), texte, fill=bord, font=f)
        _plaques_cache[key] = img
    return _plaques_cache[key]


def draw_tile(name):
    img = Image.new("RGBA", (T, T), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if name.startswith("plq|"):                      # plq|texte|n|i|style
        _, texte, n, i, style = name.split("|")
        n, i = int(n), int(i)
        return plaque_image(texte, n, style).crop((i * T, 0, (i + 1) * T, T))
    if name == "grass":
        noise_fill(d, (96, 168, 72), 18, 90)
    elif name == "path":
        noise_fill(d, (196, 188, 170), 10, 50)
        d.line([0, 15, 31, 15], fill=(170, 162, 146)); d.line([15, 0, 15, 15], fill=(170, 162, 146))
        d.line([7, 16, 7, 31], fill=(170, 162, 146))
    elif name == "sidewalk":
        d.rectangle([0, 0, 31, 31], fill=(206, 202, 194))
        d.rectangle([0, 0, 31, 31], outline=(184, 180, 172))
    elif name == "road":
        noise_fill(d, (70, 72, 78), 6, 50)
    elif name == "roadline":
        noise_fill(d, (70, 72, 78), 6, 50)
        d.rectangle([4, 14, 27, 17], fill=(235, 235, 235))
    elif name == "roadvline":
        noise_fill(d, (70, 72, 78), 6, 50)
        d.rectangle([14, 4, 17, 27], fill=(235, 235, 235))
    elif name == "crosswalk":
        noise_fill(d, (70, 72, 78), 6, 50)
        for x in (2, 12, 22):
            d.rectangle([x, 0, x + 6, 31], fill=(235, 235, 235))
    elif name == "water":
        d.rectangle([0, 0, 31, 31], fill=(60, 110, 150))
        for y in (6, 18, 28):
            d.arc([random.randint(0, 12), y - 3, random.randint(18, 31), y + 3], 200, 340, fill=(130, 175, 205))
    elif name == "roof":
        noise_fill(d, (92, 98, 112), 6, 40)
        d.line([0, 31, 31, 31], fill=(70, 74, 86))
    elif name == "facade":
        d.rectangle([0, 0, 31, 31], fill=(205, 196, 178))
        d.rectangle([7, 6, 24, 24], fill=(120, 160, 190), outline=(90, 90, 90))
        d.line([16, 6, 16, 24], fill=(90, 90, 90))
    elif name == "parkbench":
        d.rectangle([2, 10, 29, 22], fill=(120, 80, 45), outline=(70, 45, 25))
        d.line([2, 14, 29, 14], fill=(70, 45, 25)); d.line([2, 18, 29, 18], fill=(70, 45, 25))
    elif name == "wood":
        d.rectangle([0, 0, 31, 31], fill=(190, 140, 90))
        for y in (0, 8, 16, 24):
            d.line([0, y, 31, y], fill=(160, 112, 68))
        for y, x in ((0, 12), (8, 24), (16, 6), (24, 18)):
            d.line([x, y, x, y + 7], fill=(160, 112, 68))
    elif name == "class":
        d.rectangle([0, 0, 31, 31], fill=(226, 228, 232)); d.rectangle([0, 0, 31, 31], outline=(204, 207, 214))
    elif name == "beton":
        noise_fill(d, (168, 170, 172), 8, 70)
    elif name == "carpet":
        noise_fill(d, (52, 74, 140), 8, 60)
    elif name == "carpetred":
        noise_fill(d, (140, 40, 55), 8, 60)
    elif name == "checker":
        d.rectangle([0, 0, 31, 31], fill=(240, 240, 240))
        d.rectangle([0, 0, 15, 15], fill=(200, 60, 60)); d.rectangle([16, 16, 31, 31], fill=(200, 60, 60))
    elif name == "stage":
        d.rectangle([0, 0, 31, 31], fill=(110, 70, 40))
        for y in (0, 10, 21):
            d.line([0, y, 31, y], fill=(85, 52, 28))
    elif name == "libcarpet":
        noise_fill(d, (70, 120, 90), 8, 60)
    elif name == "wall":
        d.rectangle([0, 0, 31, 31], fill=(120, 126, 140))
        for y in (0, 10, 21):
            d.line([0, y, 31, y], fill=(98, 104, 118))
        for y, xs in ((0, (8, 24)), (10, (0, 16)), (21, (8, 24))):
            for x in xs:
                d.line([x, y, x, y + 10], fill=(98, 104, 118))
        d.rectangle([0, 0, 31, 3], fill=NAVY)
    elif name == "desk":
        d.rectangle([1, 6, 30, 26], fill=(150, 100, 60), outline=(100, 64, 36))
        d.rectangle([10, 10, 21, 17], fill=(40, 40, 50)); d.rectangle([11, 11, 20, 16], fill=CYAN)
    elif name == "pc":
        d.rectangle([1, 4, 30, 28], fill=(225, 225, 228), outline=(150, 150, 155))
        d.rectangle([7, 6, 24, 18], fill=(30, 30, 35)); d.rectangle([9, 8, 22, 16], fill=(40, 120, 200))
        d.rectangle([14, 18, 17, 21], fill=(60, 60, 60)); d.rectangle([8, 22, 23, 26], fill=(80, 80, 85))
    elif name == "workbench":
        d.rectangle([0, 4, 31, 27], fill=(150, 150, 140), outline=(90, 90, 80))
        d.rectangle([4, 8, 13, 15], fill=(40, 140, 70))      # carte électronique
        d.rectangle([18, 10, 27, 20], fill=(230, 180, 40))   # oscilloscope
        d.rectangle([20, 12, 25, 17], fill=(30, 30, 30))
    elif name == "bigtable":
        d.rectangle([0, 3, 31, 28], fill=(110, 75, 50), outline=(70, 45, 30))
    elif name == "chair":
        d.rounded_rectangle([8, 8, 23, 25], 4, fill=(40, 60, 110), outline=(20, 30, 60))
        d.rectangle([8, 4, 23, 9], fill=(30, 45, 90))
    elif name == "tree":
        d.ellipse([2, 2, 29, 29], fill=(40, 120, 50), outline=(25, 80, 35)); d.ellipse([8, 6, 20, 16], fill=(70, 150, 70))
    elif name == "plant":
        d.rectangle([11, 20, 20, 29], fill=(150, 80, 40)); d.ellipse([6, 3, 25, 22], fill=(50, 140, 60))
    elif name == "table":
        d.ellipse([3, 3, 28, 28], fill=(230, 220, 200), outline=(150, 140, 120)); d.ellipse([12, 9, 19, 16], fill=(120, 70, 40))
    elif name == "board":
        d.rectangle([0, 4, 31, 24], fill=(30, 30, 35)); d.rectangle([2, 6, 29, 22], fill=(235, 245, 250))
        d.line([5, 10, 20, 10], fill=CYAN, width=2); d.line([5, 15, 25, 15], fill=(120, 120, 130))
    elif name == "sign":
        d.rectangle([14, 16, 17, 31], fill=(90, 60, 40))
        d.rectangle([3, 3, 28, 18], fill=CYAN, outline=NAVY, width=2)
        d.text((12, 3), "i", fill="white", font=font(14))
    elif name == "shelf":
        d.rectangle([0, 0, 31, 31], fill=(110, 70, 40))
        colors = [(200, 50, 50), (50, 120, 200), (230, 180, 40), (60, 160, 90), (150, 70, 160)]
        for row in (2, 17):
            x = 2
            while x < 29:
                w = random.randint(3, 5)
                d.rectangle([x, row, x + w - 1, row + 12], fill=random.choice(colors)); x += w + 1
    elif name == "sofa":
        d.rounded_rectangle([1, 6, 30, 28], 5, fill=CYAN, outline=NAVY); d.rectangle([4, 6, 27, 12], fill=(0, 130, 160))
    elif name == "sofared":
        d.rounded_rectangle([1, 6, 30, 28], 5, fill=INSEEC, outline=(110, 15, 30)); d.rectangle([4, 6, 27, 12], fill=(160, 20, 45))
    elif name == "counter":
        d.rectangle([0, 4, 31, 27], fill=(80, 80, 90)); d.rectangle([0, 4, 31, 9], fill=(170, 170, 180))
    elif name == "coffee":
        d.rectangle([5, 2, 26, 29], fill=(60, 60, 65), outline=(20, 20, 20))
        d.rectangle([9, 6, 22, 12], fill=CYAN); d.rectangle([12, 18, 19, 25], fill=(240, 240, 240))
    elif name == "mat":
        d.rectangle([0, 0, 31, 31], fill=(70, 70, 70)); d.rectangle([2, 2, 29, 29], outline=CYAN, width=2)
    elif name == "door":
        d.rectangle([0, 0, 31, 31], fill=(150, 105, 60)); d.rectangle([0, 0, 31, 31], outline=(90, 60, 30), width=2)
        d.rectangle([2, 2, 6, 29], fill=(120, 80, 45)); d.rectangle([25, 2, 29, 29], fill=(120, 80, 45))
        d.ellipse([7, 14, 10, 17], fill=(230, 200, 60)); d.line([0, 31, 31, 31], fill=CYAN, width=2)
    elif name == "glassdoor":
        d.rectangle([0, 0, 31, 31], fill=(160, 200, 220)); d.rectangle([0, 0, 31, 31], outline=(60, 60, 70), width=3)
        d.line([16, 0, 16, 31], fill=(60, 60, 70), width=2)
    elif name == "sofa_i":                            # alias : canapé INSEEC
        return draw_tile("sofared")
    return img


def plaque(carte, layer, x, y, texte, n, style="mur"):
    for i in range(n):
        carte.put(layer, x + i, y, f"plq|{texte}|{n}|{i}|{style}")
        COLLIDES.add(f"plq|{texte}|{n}|{i}|{style}")


# ================================================================ cartes ===
class Carte:
    def __init__(self, cle, nom, w=48, h=34):
        self.cle, self.nom, self.W, self.H = cle, nom, w, h
        self.layers = {k: [[0] * w for _ in range(h)] for k in ("sol", "start", "murs", "mobilier", "dessus")}
        self.objects, self.oid = [], 1

    def put(self, layer, x, y, name):
        self.layers[layer][y][x] = tid(name)

    def fill(self, layer, x0, y0, x1, y1, name):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.put(layer, x, y, name)

    def clear(self, layer, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.layers[layer][y][x] = 0

    def area(self, name, x0, y0, x1, y1, props=None, kind="area"):
        o = {"id": self.oid, "name": name, "type": kind, "visible": True, "rotation": 0,
             "x": x0 * T, "y": y0 * T, "width": (x1 - x0 + 1) * T, "height": (y1 - y0 + 1) * T}
        if props:
            def typ(v):
                return "bool" if isinstance(v, bool) else "float" if isinstance(v, float) else "int" if isinstance(v, int) else "string"
            o["properties"] = [{"name": k, "type": typ(v), "value": v} for k, v in props.items()]
        self.objects.append(o)
        self.oid += 1

    def tmj(self, tileset):
        def tl(lid, name, props=None):
            lyr = {"id": lid, "name": name, "type": "tilelayer", "x": 0, "y": 0, "width": self.W, "height": self.H,
                   "opacity": 1, "visible": True, "data": [v for row in self.layers[name] for v in row]}
            if props:
                lyr["properties"] = props
            return lyr
        return {
            "type": "map", "version": "1.10", "tiledversion": "1.10.2", "orientation": "orthogonal",
            "renderorder": "right-down", "infinite": False, "width": self.W, "height": self.H,
            "tilewidth": T, "tileheight": T, "compressionlevel": -1,
            "properties": [
                {"name": "script", "type": "string", "value": "script.js"},
                {"name": "cle", "type": "string", "value": self.cle},
                {"name": "mapName", "type": "string", "value": self.nom},
            ],
            "tilesets": [tileset],
            "layers": [
                tl(1, "sol"), tl(2, "start", [{"name": "startLayer", "type": "bool", "value": True}]),
                tl(3, "murs"), tl(4, "mobilier"),
                {"id": 5, "name": "zones", "type": "objectgroup", "draworder": "topdown", "opacity": 1,
                 "visible": True, "x": 0, "y": 0, "objects": self.objects},
                {"id": 6, "name": "floorLayer", "type": "objectgroup", "draworder": "topdown", "opacity": 1,
                 "visible": True, "x": 0, "y": 0, "objects": []},
                tl(7, "dessus"),
            ],
            "nextlayerid": 8, "nextobjectid": self.oid,
        }


SALLES = {}   # id -> nom complet, pour le serveur (codes + tableau)


# ------------------------------------------------ mobilier des salles ------
def salle_amphi(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, r.get("sol", "carpet"))
    c.fill("sol", 19, 3, 28, 5, "stage")
    c.fill("mobilier", 21, 3, 26, 3, "board")
    for row in (7, 9, 11):
        for x in range(16, 32):
            if x not in (23, 24):
                c.put("mobilier", x, row, "desk"); c.put("mobilier", x, row + 1, "chair")
    c.put("mobilier", 14, 13, "plant"); c.put("mobilier", 33, 13, "plant")
    return (19, 4, 28, 5), (23.5, 6.5)   # zone prof (estrade), point de sortie pour les non-profs


def salle_classe(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, r.get("sol", "class"))
    c.fill("mobilier", x0 + 3, 3, x0 + 6, 3, "board")
    for gx, gy in ((x0 + 1, 6), (x0 + 6, 6), (x0 + 1, 10), (x0 + 6, 10)):
        c.fill("mobilier", gx, gy, gx + 1, gy, "desk")
        for cx in (gx, gx + 1):
            c.put("mobilier", cx, gy - 1, "chair"); c.put("mobilier", cx, gy + 1, "chair")
    return (x0 + 2, 4, x0 + 7, 4), (x0 + 4.5, 8.5)


def salle_labpc(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, r.get("sol", "class"))
    c.fill("mobilier", x0 + 3, 3, x0 + 6, 3, "board")
    for row in (6, 9, 12):
        for x in list(range(x0 + 1, x0 + 4)) + list(range(x0 + 6, x0 + 9)):
            c.put("mobilier", x, row, "pc")
            if row + 1 <= 13:
                c.put("mobilier", x, row + 1, "chair")
    return (x0 + 2, 4, x0 + 7, 4), (x0 + 4.5, 8.5)


def salle_fablab(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, "beton")
    c.fill("mobilier", 21, 3, 26, 3, "board")
    for bx0, bx1 in ((15, 17), (19, 21), (26, 28), (30, 32)):
        for by in (7, 11):
            c.fill("mobilier", bx0, by, bx1, by, "workbench")
            for cx in range(bx0, bx1 + 1):
                c.put("mobilier", cx, by - 1, "chair"); c.put("mobilier", cx, by + 1, "chair")
    c.fill("mobilier", 14, 13, 15, 13, "shelf"); c.fill("mobilier", 32, 13, 33, 13, "shelf")
    return (20, 4, 27, 4), (23.5, 9.5)


def salle_reunion(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, r.get("sol", "carpet"))
    c.fill("mobilier", x0 + 3, 3, x0 + 6, 3, "board")
    c.fill("mobilier", x0 + 2, 7, x0 + 7, 8, "bigtable")
    for x in range(x0 + 2, x0 + 8):
        c.put("mobilier", x, 6, "chair"); c.put("mobilier", x, 9, "chair")
    c.put("mobilier", x0, 13, "plant"); c.put("mobilier", x1, 13, "plant")
    return (x0 + 2, 4, x0 + 7, 4), (x0 + 4.5, 11.5)


def salle_biblio(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, "libcarpet")
    c.fill("mobilier", 3, 20, 8, 20, "shelf"); c.fill("mobilier", 11, 20, 16, 20, "shelf")
    c.fill("mobilier", 3, 22, 3, 28, "shelf"); c.fill("mobilier", 16, 22, 16, 28, "shelf")
    for tx, ty in ((6, 23), (11, 23), (6, 26), (11, 26)):
        c.fill("mobilier", tx, ty, tx + 1, ty, "desk")
        c.put("mobilier", tx, ty + 1, "chair"); c.put("mobilier", tx + 1, ty + 1, "chair")


def salle_learning(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, "wood")
    for tx, ty in ((5, 23), (10, 23), (5, 26), (10, 26)):
        c.fill("mobilier", tx, ty, tx + 1, ty, "desk")
        for cx in (tx, tx + 1):
            c.put("mobilier", cx, ty - 1, "chair"); c.put("mobilier", cx, ty + 1, "chair")
    c.fill("mobilier", 15, 22, 15, 25, r.get("sofa", "sofa"))
    c.put("mobilier", 3, 20, "plant"); c.put("mobilier", 16, 28, "plant"); c.put("mobilier", 3, 28, "plant")


def salle_admin(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, "class")
    c.fill("mobilier", 3, 25, 15, 25, "counter")          # guichet ; passage à droite (x=16)
    for x in (4, 7, 10, 13):
        c.put("mobilier", x, 27, "pc"); c.put("mobilier", x, 26, "chair")
    for x in (5, 8, 11):
        c.put("mobilier", x, 21, "chair")
    c.put("mobilier", 3, 20, "plant"); c.put("mobilier", 16, 20, "plant")
    return (3, 26, 16, 28), (9.5, 22.5)


def salle_cafe(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, "checker")
    c.fill("mobilier", 32, 20, 38, 20, "counter")
    c.put("mobilier", 40, 20, "coffee"); c.put("mobilier", 41, 20, "coffee")
    for tx, ty in ((33, 23), (37, 23), (41, 23), (33, 26), (37, 26), (41, 26)):
        c.put("mobilier", tx, ty, "table"); c.put("mobilier", tx - 1, ty, "chair"); c.put("mobilier", tx + 1, ty, "chair")


def salle_bde(c, r):
    x0, y0, x1, y1 = r["rect"]
    c.fill("sol", x0, y0, x1, y1, "wood")
    c.fill("mobilier", 32, 22, 32, 26, "sofa"); c.fill("mobilier", 43, 22, 43, 26, r.get("sofa", "sofa"))
    for tx, ty in ((36, 23), (39, 23), (36, 26), (39, 26)):
        c.put("mobilier", tx, ty, "table"); c.put("mobilier", tx, ty - 1, "chair"); c.put("mobilier", tx, ty + 1, "chair")
    c.put("mobilier", 41, 20, "coffee"); c.put("mobilier", 31, 28, "plant"); c.put("mobilier", 44, 28, "plant")


TYPES = {"amphi": salle_amphi, "classe": salle_classe, "labpc": salle_labpc, "fablab": salle_fablab,
         "reunion": salle_reunion, "biblio": salle_biblio, "learning": salle_learning, "admin": salle_admin,
         "cafe": salle_cafe, "bde": salle_bde}

# Emplacements fixes du squelette de bâtiment : rectangle, porte, plaque, positions couloir / intérieur
EMPL = {
    "A": dict(rect=(3, 3, 12, 13), porte=(7, 8, 14), plq=(3, 14, 4), dehors=(7.5, 16.5), dedans=(7.5, 12.5)),
    "B": dict(rect=(14, 3, 33, 13), porte=(22, 25, 14), plq=(17, 14, 5), dehors=(23.5, 16.5), dedans=(23.5, 12.5)),
    "C": dict(rect=(35, 3, 44, 13), porte=(39, 40, 14), plq=(41, 14, 4), dehors=(39.5, 16.5), dedans=(39.5, 12.5)),
    "D": dict(rect=(3, 20, 16, 28), porte=(9, 10, 19), plq=(11, 19, 5), dehors=(9.5, 17.5), dedans=(9.5, 20.5)),
    "F": dict(rect=(31, 20, 44, 28), porte=(37, 38, 19), plq=(39, 19, 5), dehors=(37.5, 17.5), dedans=(37.5, 20.5)),
}


def batiment(cfg):
    c = Carte(cfg["cle"], f"{cfg['nom']} – {cfg['ecoles']}")
    accent_sofa = "sofared" if "INSEEC" in cfg["ecoles"] else "sofa"
    c.fill("sol", 0, 0, c.W - 1, c.H - 1, "grass")
    c.fill("sol", 22, 29, 25, c.H - 1, "path")
    for x, y in [(1, 1), (46, 1), (1, 31), (5, 32), (10, 31), (16, 32), (31, 32), (37, 31), (42, 32), (46, 31)]:
        c.put("dessus", x, y, "tree")
    # Couloir, hall, seuils
    c.fill("sol", 3, 15, 44, 18, "wood")
    c.fill("sol", 3, 14, 44, 14, "wood"); c.fill("sol", 3, 19, 44, 19, "wood")
    c.fill("sol", 18, 20, 29, 28, "wood")
    c.fill("sol", 23, 28, 24, 29, "mat")
    # Murs
    for x in range(2, 46):
        for y in (2, 29, 14, 19):
            c.put("murs", x, y, "wall")
    for y in range(2, 30):
        c.put("murs", 2, y, "wall"); c.put("murs", 45, y, "wall")
    for y in range(3, 14):
        c.put("murs", 13, y, "wall"); c.put("murs", 34, y, "wall")
    for y in range(20, 29):
        c.put("murs", 17, y, "wall"); c.put("murs", 30, y, "wall")
    c.clear("murs", 22, 19, 25, 19)          # hall ouvert sur le couloir
    c.fill("murs", 23, 29, 24, 29, "glassdoor")
    plaque(c, "murs", 18, 19, cfg["nom"].upper(), 4)
    for x in (5, 15, 32, 42):
        c.put("mobilier", x, 15, "plant")

    # Hall d'accueil
    for x, y in ((18, 20), (29, 20), (18, 27), (29, 27)):
        c.put("mobilier", x, y, "plant")
    c.fill("mobilier", 19, 24, 19, 26, accent_sofa); c.fill("mobilier", 28, 24, 28, 26, accent_sofa)
    c.put("mobilier", 21, 21, "sign"); c.put("mobilier", 26, 21, "sign")
    c.area("panneau-infos", 20, 22, 22, 22, {"openWebsite": "infos.html", "openWebsiteTrigger": "onaction",
                                            "openWebsiteTriggerMessage": "ESPACE : guide du campus"})
    c.area("panneau-ecole", 25, 22, 27, 22, {"openWebsite": cfg["site"], "openWebsiteTrigger": "onaction",
                                            "openWebsiteTriggerMessage": "ESPACE : site de l'école"})
    c.area("accueil", 18, 20, 29, 28, {"message": f"👋 {cfg['nom']} – {cfg['ecoles']} : hall d'accueil"})
    c.area("popupAccueil", 22, 25, 25, 26, kind="")
    # Entrée / sortie du bâtiment
    c.fill("start", 22, 26, 25, 27, "wood")
    c.area("arrivee-quartier", 22, 26, 25, 27)
    c.area("sortie", 22, 32, 25, 33, {"versCarte": "quartier.tmj"})

    # Salles
    for slot, r in cfg["salles"].items():
        e = EMPL[slot]
        r = {**r, "rect": e["rect"], "sofa": accent_sofa}
        sid = f"{cfg['cle']}-{r['id']}"
        res = TYPES[r["type"]](c, r)
        px0, px1, py = e["porte"]
        c.fill("murs", px0, py, px1, py, "door")
        x, y, n = e["plq"]
        plaque(c, "murs", x, y, r["court"], n)
        x0, y0, x1, y1 = e["rect"]
        props = {"message": r["message"]} if r.get("message") else {}
        if r.get("silence"):
            props["silent"] = True
        if r.get("tableau"):
            props["tableau"] = sid; props["nomSalle"] = r["nom"]
            SALLES[sid] = f"{r['nom']} ({cfg['nom']})"
        c.area(f"salle-{sid}", x0, y0, x1, y1, props or None)
        if r.get("code"):
            (dx, dy), (ix, iy) = e["dehors"], e["dedans"]
            c.area(f"porte-{sid}", px0, py, px1, py, {"codeSalle": sid, "nomSalle": r["nom"],
                                                      "sortieX": dx, "sortieY": dy, "entreeX": ix, "entreeY": iy})
            SALLES[sid] = f"{r['nom']} ({cfg['nom']})"
        if res:   # zone réservée (estrade / tableau / back-office)
            (zx0, zy0, zx1, zy1), (sx, sy) = res
            reserve = "admin" if r["type"] == "admin" else "staff"
            zp = {"reserve": reserve, "sortieX": sx, "sortieY": sy}
            if reserve == "staff":
                zp.update({"speakerMegaphone": sid, "focusable": True,
                           "message": "🎤 Tu es au tableau : toute la salle t'entend"})
                c.area(f"auditoire-{sid}", x0, zy1 + 1, x1, y1, {"listenerMegaphone": sid})
            else:
                zp["message"] = "🗂️ Back-office de la scolarité"
            c.area(f"reserve-{sid}", zx0, zy0, zx1, zy1, zp)
    return c


BATIMENTS = [
    {"cle": "eiffel1", "nom": "Eiffel 1", "ecoles": "ECE", "site": "https://www.ece.fr", "salles": {
        "A": {"id": "td1", "nom": "Salle de TD 1", "court": "TD 1", "type": "classe", "code": True, "tableau": True,
              "message": "📘 TD 1 : installe-toi à un îlot pour travailler en groupe"},
        "B": {"id": "amphi", "nom": "Amphi Eiffel", "court": "AMPHI", "type": "amphi", "code": True, "tableau": True,
              "message": "🎓 Amphi Eiffel : le prof sur l'estrade est entendu par toute la salle"},
        "C": {"id": "td2", "nom": "Salle de TD 2", "court": "TD 2", "type": "classe", "code": True, "tableau": True,
              "message": "📗 TD 2 : installe-toi à un îlot pour travailler en groupe"},
        "D": {"id": "biblio", "nom": "Bibliothèque", "court": "BIBLIO", "type": "biblio", "silence": True,
              "message": "🤫 Bibliothèque : zone silencieuse"},
        "F": {"id": "cafe", "nom": "Cafétéria", "court": "CAFÉ", "type": "cafe",
              "message": "☕ Cafétéria : approche-toi de quelqu'un pour discuter"},
    }},
    {"cle": "eiffel2", "nom": "Eiffel 2", "ecoles": "INSEEC", "site": "https://www.inseec.com", "salles": {
        "A": {"id": "s201", "nom": "Salle 201", "court": "SALLE 201", "type": "classe", "code": True, "tableau": True,
              "message": "📘 Salle 201 : cours et études de cas en groupe"},
        "B": {"id": "amphi", "nom": "Amphi INSEEC", "court": "AMPHI", "type": "amphi", "sol": "carpetred",
              "code": True, "tableau": True, "message": "🎓 Amphi INSEEC : conférences et cours magistraux"},
        "C": {"id": "s202", "nom": "Salle 202", "court": "SALLE 202", "type": "classe", "code": True, "tableau": True,
              "message": "📗 Salle 202 : cours et études de cas en groupe"},
        "D": {"id": "learning", "nom": "Learning Lab", "court": "LEARNING", "type": "learning",
              "message": "💡 Learning Lab : travail en équipe et projets"},
        "F": {"id": "cafe", "nom": "Cafétéria", "court": "CAFÉ", "type": "cafe",
              "message": "☕ Cafétéria : approche-toi de quelqu'un pour discuter"},
    }},
    {"cle": "eiffel3", "nom": "Eiffel 3", "ecoles": "ECE Labs", "site": "https://www.ece.fr", "salles": {
        "A": {"id": "labinfo", "nom": "Lab informatique", "court": "LAB INFO", "type": "labpc", "code": True,
              "tableau": True, "message": "💻 Lab informatique : TP de programmation"},
        "B": {"id": "fablab", "nom": "Fablab électronique", "court": "FABLAB", "type": "fablab", "code": True,
              "tableau": True, "message": "🔧 Fablab : TP d'électronique et prototypes"},
        "C": {"id": "labreseau", "nom": "Lab réseaux", "court": "RÉSEAUX", "type": "labpc", "code": True,
              "tableau": True, "message": "🌐 Lab réseaux et cybersécurité"},
        "D": {"id": "projets", "nom": "Salle projets", "court": "PROJETS", "type": "learning",
              "message": "🚀 Salle projets : travail en équipe"},
        "F": {"id": "bde", "nom": "Espace BDE", "court": "BDE", "type": "bde",
              "message": "🎉 Espace BDE : associations et détente"},
    }},
    {"cle": "eiffel4", "nom": "Eiffel 4", "ecoles": "ECE · INSEEC", "site": "https://www.omneseducation.com", "salles": {
        "A": {"id": "reunion", "nom": "Salle de réunion", "court": "RÉUNION", "type": "reunion", "code": True,
              "tableau": True, "message": "🤝 Salle de réunion : jurys, soutenances, réunions"},
        "B": {"id": "amphi", "nom": "Grand amphi", "court": "GRAND AMPHI", "type": "amphi", "code": True,
              "tableau": True, "message": "🎓 Grand amphi : cours communs ECE et INSEEC"},
        "C": {"id": "td", "nom": "Salle de TD", "court": "TD", "type": "classe", "code": True, "tableau": True,
              "message": "📘 Salle de TD : travail en groupe"},
        "D": {"id": "scolarite", "nom": "Scolarité", "court": "SCOLARITÉ", "type": "admin",
              "message": "🗂️ Scolarité : présente-toi au guichet"},
        "F": {"id": "cafe", "nom": "Cafétéria", "court": "CAFÉ", "type": "cafe",
              "message": "☕ Cafétéria : approche-toi de quelqu'un pour discuter"},
    }},
]


# ------------------------------------------------------------- quartier ----
def quartier():
    c = Carte("quartier", "Campus Eiffel – ECE / INSEEC", 48, 36)
    c.fill("sol", 0, 0, 47, 35, "sidewalk")
    c.fill("sol", 0, 0, 47, 3, "water")                       # la Seine
    c.fill("sol", 0, 6, 47, 8, "road"); c.fill("sol", 0, 7, 47, 7, "roadline")
    c.fill("sol", 22, 9, 25, 35, "road"); c.fill("sol", 23, 9, 24, 35, "roadvline")
    c.fill("sol", 10, 6, 13, 8, "crosswalk"); c.fill("sol", 34, 6, 37, 8, "crosswalk")
    c.fill("sol", 22, 6, 25, 8, "road")
    for x in range(1, 47, 4):
        c.put("dessus", x, 4, "tree")
    for x in (3, 19, 29, 43):
        c.put("mobilier", x, 5, "parkbench")
    plaque(c, "mobilier", 6, 4, "QUAI · SEINE", 3, "toit")
    plaque(c, "mobilier", 26, 10, "RUE SEXTIUS MICHEL", 5, "toit")

    batis = [  # cle, nom, école, x0, y0, x1, y1 (porte en bas, au centre)
        ("eiffel1", "EIFFEL 1", "ECE", 3, 11, 18, 19),
        ("eiffel2", "EIFFEL 2", "INSEEC", 29, 11, 44, 19),
        ("eiffel3", "EIFFEL 3", "ECE · LABS", 3, 23, 18, 31),
        ("eiffel4", "EIFFEL 4", "ECE · INSEEC", 29, 23, 44, 31),
    ]
    for cle, nom, ecole, x0, y0, x1, y1 in batis:
        c.fill("murs", x0, y0, x1, y1 - 1, "roof")
        c.fill("murs", x0, y1, x1, y1, "facade")
        mx = (x0 + x1) // 2
        c.fill("murs", mx, y1, mx + 1, y1, "glassdoor")
        plaque(c, "murs", mx - 5, y1, nom, 4, "facade")
        plaque(c, "murs", mx - 2, (y0 + y1) // 2 - 1, ecole, 6, "toit")
        if cle == "eiffel1":
            plaque(c, "murs", mx + 3, y1, "10 RUE SEXTIUS MICHEL", 5, "facade")
        c.put("mobilier", x0, y1 + 1, "plant"); c.put("mobilier", x1, y1 + 1, "plant")
        c.area(f"entree-{cle}", mx, y1, mx + 1, y1,
               {"versCarte": f"{cle}.tmj", "message": f"🏢 Entrée de {nom.title()} ({ecole})"})
        c.area(f"arrivee-{cle}", mx, y1 + 2, mx + 1, y1 + 2)
    # Point d'arrivée et panneau d'infos
    c.fill("start", 19, 21, 20, 22, "sidewalk")
    c.put("mobilier", 20, 20, "sign")
    c.area("panneau-infos", 19, 21, 21, 21, {"openWebsite": "infos.html", "openWebsiteTrigger": "onaction",
                                            "openWebsiteTriggerMessage": "ESPACE : plan et guide du campus"})
    c.area("accueil", 19, 21, 20, 22, {"bienvenue": True})
    c.area("popupAccueil", 17, 18, 21, 19, kind="")
    for x, y in ((1, 34), (8, 34), (15, 34), (32, 34), (39, 34), (46, 34), (20, 12), (27, 26)):
        c.put("dessus", x, y, "tree")
    return c


# ================================================================ export ===
def main():
    cartes = [quartier()] + [batiment(b) for b in BATIMENTS]
    tid("grass")  # garantit au moins une tuile
    rows = (len(TILES) + COLS - 1) // COLS
    sheet = Image.new("RGBA", (COLS * T, rows * T), (0, 0, 0, 0))
    for i, name in enumerate(TILES):
        sheet.paste(draw_tile(name), ((i % COLS) * T, (i // COLS) * T))
    sheet.save(ROOT / "tileset.png")
    tileset = {
        "firstgid": 1, "name": "campus-eiffel", "image": "tileset.png",
        "imagewidth": sheet.width, "imageheight": sheet.height, "tilewidth": T, "tileheight": T,
        "columns": COLS, "tilecount": len(TILES), "margin": 0, "spacing": 0,
        "tiles": [{"id": ID[n], "properties": [{"name": "collides", "type": "bool", "value": True}]}
                  for n in TILES if n in COLLIDES],
    }
    for c in cartes:
        (ROOT / f"{c.cle}.tmj").write_text(json.dumps(c.tmj(tileset), ensure_ascii=False), encoding="utf-8")
        prev = Image.new("RGBA", (c.W * T, c.H * T))
        for lname in ("sol", "murs", "mobilier", "dessus"):
            for y, row in enumerate(c.layers[lname]):
                for x, g in enumerate(row):
                    if g:
                        i = g - 1
                        prev.alpha_composite(sheet.crop(((i % COLS) * T, (i // COLS) * T, (i % COLS + 1) * T, (i // COLS + 1) * T)), (x * T, y * T))
        prev.save(ROOT / f"apercu-{c.cle}.png")
    (ROOT / "salles.json").write_text(json.dumps(SALLES, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK : {len(cartes)} cartes, {len(TILES)} tuiles, {len(SALLES)} salles")


if __name__ == "__main__":
    main()
