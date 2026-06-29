"""DXF Exporter for Building Model v2."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, TextIO, Tuple
from ..validation.cross_entity_validator import BuildingModel


def _line(f, x1, y1, x2, y2, layer="0", color=7):
    f.write(f"  0\nLINE\n  8\n{layer}\n 62\n{color}\n")
    f.write(f" 10\n{x1}\n 20\n{y1}\n 30\n0.0\n")
    f.write(f" 11\n{x2}\n 21\n{y2}\n 31\n0.0\n")


def _text(f, x, y, tex, height=0.5, layer="0", color=7, rot=0.0):
    f.write(f"  0\nTEXT\n  8\n{layer}\n 62\n{color}\n")
    f.write(f" 10\n{x}\n 20\n{y}\n 30\n0.0\n")
    f.write(f" 40\n{height}\n  1\n{tex}\n 50\n{rot}\n")


def _circle(f, cx, cy, r, layer="0", color=7):
    f.write(f"  0\nCIRCLE\n  8\n{layer}\n 62\n{color}\n")
    f.write(f" 10\n{cx}\n 20\n{cy}\n 30\n0.0\n 40\n{r}\n")


def _poly(f, pts, layer="0", color=7, closed=True):
    flag = 1 if closed else 0
    f.write(f"  0\nPOLYLINE\n  8\n{layer}\n 62\n{color}\n 66\n1\n 70\n{flag}\n")
    for px, py in pts:
        f.write(f"  0\nVERTEX\n  8\n{layer}\n 10\n{px}\n 20\n{py}\n 30\n0.0\n")
    f.write(f"  0\nSEQEND\n  8\n{layer}\n")


def _arc(f, cx, cy, r, sa, ea, layer="0", color=7):
    f.write(f"  0\nARC\n  8\n{layer}\n 62\n{color}\n")
    f.write(f" 10\n{cx}\n 20\n{cy}\n 30\n0.0\n 40\n{r}\n 50\n{sa}\n 51\n{ea}\n")


def _dim(f, x1, y1, x2, y2, dy, layer="A-DIMS", color=8):
    length = abs(x2-x1) if abs(x2-x1)>abs(y2-y1) else abs(y2-y1)
    f.write(f"  0\nDIMENSION\n  8\n{layer}\n 62\n{color}\n")
    f.write(f" 10\n{x1}\n 20\n{dy}\n 30\n0.0\n")
    f.write(f" 11\n{(x1+x2)/2}\n 21\n{dy+0.5}\n 31\n0.0\n 70\n1\n  1\n{int(length)} ft\n")


class PaperSize:
    A4="A4";A3="A3";A2="A2";A1="A1";A0="A0";LETTER="LETTER";LEGAL="LEGAL";TABLOID="TABLOID"
    def __init__(self,v="A3"):self.value=v

class DrawingUnits:
    FEET="feet";INCHES="inches";METERS="meters";MILLIMETERS="millimeters"
    def __init__(self,v="feet"):self.value=v

class DrawingSettings:
    def __init__(self,paper_size=None,units=None,scale=1.0,
                 text_height=0.5,dimension_height=0.35,line_width=0.25,
                 show_grid=True,show_dimensions=True,show_title_block=True,
                 show_north_arrow=True,show_room_labels=True,show_room_areas=True,
                 layer_visibility=None):
        self.paper_size=paper_size or PaperSize()
        self.units=units or DrawingUnits()
        self.scale=scale
        self.text_height=text_height
        self.dimension_height=dimension_height
        self.line_width=line_width
        self.show_grid=show_grid
        self.show_dimensions=show_dimensions
        self.show_title_block=show_title_block
        self.show_north_arrow=show_north_arrow
        self.show_room_labels=show_room_labels
        self.show_room_areas=show_room_areas
        self.layer_visibility=layer_visibility or {
            "A-WALL":True,"A-DOOR":True,"A-WINDOW":True,"A-COLUMN":True,
            "A-STAIR":True,"A-TEXT":True,"A-DIMS":True,"A-GRID":True,
            "A-HATCH":True,"A-TITLE":True}
    @classmethod
    def default(cls):return cls()
    def to_dict(self):
        return {"paper_size":self.paper_size.value,"units":self.units.value,
                "scale":self.scale,"text_height":self.text_height,
                "dimension_height":self.dimension_height,"line_width":self.line_width,
                "show_grid":self.show_grid,"show_dimensions":self.show_dimensions,
                "show_title_block":self.show_title_block,
                "show_north_arrow":self.show_north_arrow,
                "show_room_labels":self.show_room_labels,
                "show_room_areas":self.show_room_areas,
                "layer_visibility":dict(self.layer_visibility)}
    @classmethod
    def from_dict(cls,d):
        return cls(paper_size=PaperSize(d.get("paper_size","A3")),
                   units=DrawingUnits(d.get("units","feet")),
                   scale=float(d.get("scale",1.0)),
                   text_height=float(d.get("text_height",0.5)),
                   dimension_height=float(d.get("dimension_height",0.35)),
                   line_width=float(d.get("line_width",0.25)),
                   show_grid=d.get("show_grid",True),
                   show_dimensions=d.get("show_dimensions",True),
                   show_title_block=d.get("show_title_block",True),
                   show_north_arrow=d.get("show_north_arrow",True),
                   show_room_labels=d.get("show_room_labels",True),
                   show_room_areas=d.get("show_room_areas",True),
                   layer_visibility=d.get("layer_visibility",{}))


class Color:
    def __init__(self, r, g, b): self.r=r; self.g=g; self.b=b
    @property
    def aci(self):
        m={(0,0,0):7,(255,0,0):1,(255,255,0):2,(0,255,0):3,(0,255,255):4,
           (0,0,255):5,(255,0,255):6,(255,255,255):7,(128,128,128):8}
        return m.get((self.r,self.g,self.b),7)


class LineType:
    def __init__(self,name,desc=""): self.name=name; self.description=desc

class DXFStyle:
    def __init__(self,name,color,lw=0.25,th=0.5):
        self.name=name; self.color=color; self.line_width=lw; self.text_height=th

LINE_CONTINUOUS=LineType("CONTINUOUS","Solid line")
LINE_HIDDEN=LineType("HIDDEN","Hidden line")
LINE_CENTER=LineType("CENTER","Center line")

COLOR_WALL=Color(0,0,0);COLOR_DOOR=Color(0,0,255);COLOR_WINDOW=Color(0,255,255)
COLOR_COLUMN=Color(128,128,128);COLOR_STAIR=Color(255,255,0);COLOR_TEXT=Color(255,255,255)
COLOR_DIM=Color(128,128,128);COLOR_GRID=Color(200,200,200)
COLOR_HATCH=Color(220,220,220);COLOR_TITLE=Color(0,0,0)

STYLE_WALL=DXFStyle("A-WALL",COLOR_WALL,0.35)
STYLE_DOOR=DXFStyle("A-DOOR",COLOR_DOOR,0.25)
STYLE_WINDOW=DXFStyle("A-WINDOW",COLOR_WINDOW,0.25)
STYLE_COLUMN=DXFStyle("A-COLUMN",COLOR_COLUMN,0.25)
STYLE_STAIR=DXFStyle("A-STAIR",COLOR_STAIR,0.25)
STYLE_TEXT=DXFStyle("A-TEXT",COLOR_TEXT,0.18,0.5)
STYLE_DIM=DXFStyle("A-DIMS",COLOR_DIM,0.18)
STYLE_GRID=DXFStyle("A-GRID",COLOR_GRID,0.09)

ALL_STYLES=[STYLE_WALL,STYLE_DOOR,STYLE_WINDOW,STYLE_COLUMN,STYLE_STAIR,STYLE_TEXT,STYLE_DIM,STYLE_GRID]
STYLE_MAP={s.name:s for s in ALL_STYLES}


class DXFLayer:
    def __init__(self,name,color,lw=0.25,line_type=None):
        self.name=name; self.color=color; self.line_width=lw
        self.line_type=line_type or LINE_CONTINUOUS

LAYER_WALL=DXFLayer("A-WALL",COLOR_WALL,0.35)
LAYER_DOOR=DXFLayer("A-DOOR",COLOR_DOOR,0.25)
LAYER_WINDOW=DXFLayer("A-WINDOW",COLOR_WINDOW,0.25)
LAYER_COLUMN=DXFLayer("A-COLUMN",COLOR_COLUMN,0.25)
LAYER_STAIR=DXFLayer("A-STAIR",COLOR_STAIR,0.25)
LAYER_TEXT=DXFLayer("A-TEXT",COLOR_TEXT,0.18)
LAYER_DIM=DXFLayer("A-DIMS",COLOR_DIM,0.18)
LAYER_GRID=DXFLayer("A-GRID",COLOR_GRID,0.09)
LAYER_HATCH=DXFLayer("A-HATCH",COLOR_HATCH,0.09)
LAYER_TITLE=DXFLayer("A-TITLE",COLOR_TITLE,0.25)

ALL_LAYERS=[LAYER_WALL,LAYER_DOOR,LAYER_WINDOW,LAYER_COLUMN,LAYER_STAIR,
            LAYER_TEXT,LAYER_DIM,LAYER_GRID,LAYER_HATCH,LAYER_TITLE]
LAYER_MAP={l.name:l for l in ALL_LAYERS}


class TitleBlockData:
    def __init__(self,project_name="Craftshood AI Project",project_number="",
                 description="",site_name="",site_address="",drawn_by="Craftshood AI",
                 date=None,scale="1:100",revision="A",sheet_number="1 of 1"):
        self.project_name=project_name;self.project_number=project_number
        self.description=description;self.site_name=site_name;self.site_address=site_address
        self.drawn_by=drawn_by;self.date=date or datetime.now().strftime("%Y-%m-%d")
        self.scale=scale;self.revision=revision;self.sheet_number=sheet_number
    def to_dict(self):return self.__dict__.copy()
    @classmethod
    def from_dict(cls,d):return cls(**{k:v for k,v in d.items() if k in cls.__init__.__code__.co_varnames})


class DXFExporter:
    def __init__(self, settings=None):
        self._settings = settings or DrawingSettings.default()

    def export(self, model, output_path, title_block=None):
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            self._write_header(f)
            self._write_tables(f)
            self._write_blocks(f)
            self._write_entities(f, model)
            if self._settings.show_title_block and title_block:
                self._write_title_block(f, title_block)
            f.write("  0\nEOF\n")
        return output_path

    def export_to_string(self, model):
        from io import StringIO
        buf = StringIO()
        self._write_header(buf)
        self._write_tables(buf)
        self._write_blocks(buf)
        self._write_entities(buf, model)
        buf.write("  0\nEOF\n")
        return buf.getvalue()

    def _write_header(self, f):
        u = {"feet":2,"inches":1,"meters":6,"millimeters":4}.get(self._settings.units.value,2)
        f.write("  0\nSECTION\n  2\nHEADER\n  9\n$ACADVER\n  1\nAC1015\n")
        f.write("  9\n$INSUNITS\n 70\n{}\n  9\n$TEXTSIZE\n 40\n{}\n  0\nENDSEC\n".format(u, self._settings.text_height))

    def _write_tables(self, f):
        f.write("  0\nSECTION\n  2\nTABLES\n  0\nTABLE\n  2\nLAYER\n 70\n{}\n".format(len(ALL_LAYERS)))
        for layer in ALL_LAYERS:
            f.write("  0\nLAYER\n  2\n{}\n 70\n0\n 62\n{}\n  6\n{}\n".format(layer.name, layer.color.aci, layer.line_type.name))
        f.write("  0\nENDTAB\n  0\nTABLE\n  2\nLTYPE\n 70\n3\n")
        for lt in [LineType("CONTINUOUS"),LineType("HIDDEN"),LineType("CENTER")]:
            f.write("  0\nLTYPE\n  2\n{}\n 70\n0\n  3\n{}\n 72\n65\n 73\n0\n 40\n0.0\n".format(lt.name,lt.description))
        f.write("  0\nENDTAB\n  0\nENDSEC\n")

    def _write_blocks(self, f):
        f.write("  0\nSECTION\n  2\nBLOCKS\n  0\nENDSEC\n")

    def _write_entities(self, f, model):
        f.write("  0\nSECTION\n  2\nENTITIES\n")
        if self._settings.show_grid: self._write_grid(f, model)
        self._write_walls(f, model)
        if self._settings.show_room_labels: self._write_room_labels(f, model)
        self._write_columns(f, model); self._write_stairs(f, model)
        self._write_doors(f, model); self._write_windows(f, model)
        if self._settings.show_north_arrow: self._write_north_arrow(f, model)
        if self._settings.show_dimensions: self._write_dimensions(f, model)
        f.write("  0\nENDSEC\n")

    def _write_walls(self, f, model):
        if not self._settings.layer_visibility.get("A-WALL", True):
            return
        for wall in model.walls.values():
            if wall.geometry.is_empty:
                continue
            coords = list(wall.geometry.coords)
            for i in range(len(coords) - 1):
                _line(f, coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1], LAYER_WALL.name, LAYER_WALL.color.aci)
        for room in model.rooms.values():
            if room.polygon.is_empty:
                continue
            coords = list(room.polygon.exterior.coords)
            for i in range(len(coords) - 1):
                _line(f, coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1], LAYER_WALL.name, LAYER_WALL.color.aci)

    def _write_room_labels(self, f, model):
        for room in model.rooms.values():
            if room.polygon.is_empty:
                continue
            c = room.centroid
            _text(f, c.x, c.y, room.room_type.value, self._settings.text_height, LAYER_TEXT.name, LAYER_TEXT.color.aci)
            if self._settings.show_room_areas:
                _text(f, c.x, c.y - self._settings.text_height - 0.2, "{:.0f} sqft".format(room.polygon.area), self._settings.text_height * 0.7, LAYER_TEXT.name)

    def _write_columns(self, f, model):
        if not self._settings.layer_visibility.get("A-COLUMN", True):
            return
        for col in model.columns.values():
            if col.geometry:
                _circle(f, col.geometry.x, col.geometry.y, max(col.size / 2, 0.5), "A-COLUMN", 8)

    def _write_stairs(self, f, model):
        if not self._settings.layer_visibility.get("A-STAIR", True):
            return
        for stair in model.stairs.values():
            if stair.geometry and not stair.geometry.is_empty:
                coords = list(stair.geometry.coords)
                for i in range(len(coords) - 1):
                    _line(f, coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1], "A-STAIR", 2)

    def _write_doors(self, f, model):
        if not self._settings.layer_visibility.get("A-DOOR", True):
            return
        for door in model.doors.values():
            if door.location:
                _circle(f, door.location.x, door.location.y, door.width / 2, "A-DOOR", 5)

    def _write_windows(self, f, model):
        if not self._settings.layer_visibility.get("A-WINDOW", True):
            return
        for win in model.windows.values():
            if win.location:
                _circle(f, win.location.x, win.location.y, win.width / 2, "A-WINDOW", 4)

    def _write_grid(self, f, model):
        mn_x, mn_y, mx_x, mx_y = self._get_bounds(model)
        sp = 10.0
        x = float(int(mn_x/sp)*int(sp))
        while x <= mx_x:
            _line(f, x, mn_y, x, mx_y, LAYER_GRID.name, LAYER_GRID.color.aci)
            x += sp
        y = float(int(mn_y/sp)*int(sp))
        while y <= mx_y:
            _line(f, mn_x, y, mx_x, y, LAYER_GRID.name, LAYER_GRID.color.aci)
            y += sp

    def _write_dimensions(self, f, model):
        mn_x, mn_y, mx_x, mx_y = self._get_bounds(model)
        o = 5.0
        _dim(f, mn_x, mn_y-o, mx_x, mn_y-o, mn_y-o-2)
        _dim(f, mn_x-o, mn_y, mn_x-o, mx_y, mn_x-o-2)

    def _write_north_arrow(self, f, model):
        mn_x, mn_y, mx_x, mx_y = self._get_bounds(model)
        cx, cy = mx_x+15, mx_y-15
        _poly(f, [(cx,cy-10),(cx-5,cy+5),(cx,cy+2),(cx+5,cy+5),(cx,cy-10)], "A-TITLE", 7)
        _text(f, cx, cy+8, "N", 0.7, "A-TITLE", 7)

    def _write_title_block(self, f, tb):
        mx = 1000
        w, h = 40.0, 15.0
        bx, by = mx-w-5, -5
        _poly(f, [(bx,by),(bx+w,by),(bx+w,by+h),(bx,by+h),(bx,by)], "A-TITLE", 7)
        _text(f, bx+1, by+h-2, "Project: {}".format(tb.project_name), 0.4, "A-TITLE", 7)
        _text(f, bx+1, by+h-4, "Date: {}".format(tb.date), 0.4, "A-TITLE", 7)
        _text(f, bx+1, by+h-6, "Scale: {}".format(tb.scale), 0.4, "A-TITLE", 7)
        _text(f, bx+1, by+h-8, "Rev: {}  By: {}".format(tb.revision, tb.drawn_by), 0.4, "A-TITLE", 7)

    def _get_bounds(self, model):
        mn_x = mn_y = float("inf")
        mx_x = mx_y = float("-inf")
        for room in model.rooms.values():
            if not room.polygon.is_empty:
                b = room.polygon.bounds
                mn_x, mn_y = min(mn_x, b[0]), min(mn_y, b[1])
                mx_x, mx_y = max(mx_x, b[2]), max(mx_y, b[3])
        if mn_x == float("inf"):
            return -10.0, -10.0, 10.0, 10.0
        return mn_x, mn_y, mx_x, mx_y


def export_building(model, output_path, settings=None):
    return DXFExporter(settings).export(model, output_path)
