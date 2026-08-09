"""Make station points draggable and add a save-to-CSV feature in main.py."""
from pathlib import Path

p = Path(r"C:\AI Projects\MagneMotionMonitor\Track Alignment program\main.py")
with open(p, "rb") as f:
    data = f.read()

if b"\r\n" in data:
    sep = "\r\n"
    text = data.decode("utf-8").replace("\r\n", "\n")
else:
    sep = "\n"
    text = data.decode("utf-8")

# 1. Add StopHandle class after AnchorHandle
old_anchor_handle_end = """    def mousePressEvent(self, event: QMouseEvent):
        self.setSelected(True)
        if self.on_selected:
            self.on_selected(self.idx)
        super().mousePressEvent(event)


class TrackView(QGraphicsView):
"""

new_anchor_handle_end = """    def mousePressEvent(self, event: QMouseEvent):
        self.setSelected(True)
        if self.on_selected:
            self.on_selected(self.idx)
        super().mousePressEvent(event)


class StopHandle(QGraphicsEllipseItem):
    \"\"\"Draggable labeled station/pallet-stop handle.\"\"\"

    def __init__(self, name: str, x: float, y: float, path_id: int, pos_m: float):
        super().__init__(-8, -8, 16, 16)
        self.name = name
        self.path_id = path_id
        self.pos_m = pos_m
        self.setPos(x, y)
        self.setPen(QPen(Qt.black, 2))
        self.setBrush(QColor("white"))
        self.setFlags(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsEllipseItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setZValue(35)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.on_moved = None
        self.on_selected = None
        # Label text
        text = QGraphicsSimpleTextItem(name, self)
        text.setBrush(QColor("black"))
        text.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        text.setPos(10, -10)
        halo = QGraphicsSimpleTextItem(name, self)
        halo.setBrush(QColor("white"))
        halo.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        halo.setPos(11, -9)
        halo.setZValue(-1)
        text.setZValue(0)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            p = QPointF(value)
            r = self.scene().sceneRect()
            p.setX(max(0, min(p.x(), r.width())))
            p.setY(max(0, min(p.y(), r.height())))
            return p
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            pos = self.pos()
            if self.on_moved:
                self.on_moved(self.name, pos.x(), pos.y())
        return super().itemChange(change, value)

    def set_highlighted(self, highlighted: bool):
        pen = QPen(QColor("red") if highlighted else Qt.black, 4 if highlighted else 2)
        self.setPen(pen)
        self.setZValue(55 if highlighted else 35)

    def mousePressEvent(self, event: QMouseEvent):
        self.setSelected(True)
        if self.on_selected:
            self.on_selected(self.name)
        super().mousePressEvent(event)


class TrackView(QGraphicsView):
"""

if old_anchor_handle_end not in text:
    raise ValueError("AnchorHandle end block not found")
text = text.replace(old_anchor_handle_end, new_anchor_handle_end)

# 2. Replace StationMarker with simpler non-draggable reference (or keep both)
# We already have StationMarker. We'll keep it for reference and add StopHandle as editable.
# Modify TrackView.set_station_markers to use StopHandle instead of StationMarker.
old_station_class = """class StationMarker(QGraphicsEllipseItem):
    \"\"\"Labeled station/pallet-stop marker from track_points.csv.\"\"\"

    def __init__(self, x: float, y: float, label: str, path_id: int, pos_m: float):
        super().__init__(-6, -6, 12, 12)
        self.setPos(x, y)
        self.setPen(QPen(Qt.black, 2))
        color = PATH_COLORS.get(path_id, QColor(\"yellow\"))
        self.setBrush(color)
        self.setZValue(20)
        self.label = label
        self.path_id = path_id
        self.pos_m = pos_m
        text = QGraphicsSimpleTextItem(label, self)
        text.setBrush(QColor(\"black\"))
        text.setFont(QFont(\"Arial\", 9, QFont.Weight.Bold))
        text.setPos(10, -10)
        # White halo behind text for readability
        halo = QGraphicsSimpleTextItem(label, self)
        halo.setBrush(QColor(\"white\"))
        halo.setFont(QFont(\"Arial\", 9, QFont.Weight.Bold))
        halo.setPos(11, -9)
        halo.setZValue(-1)
        text.setZValue(0)

    def set_highlighted(self, highlighted: bool):
        pen = QPen(QColor(\"red\" if highlighted else Qt.black), 4 if highlighted else 2)
        self.setPen(pen)
        self.setZValue(40 if highlighted else 20)
"""

# Leave StationMarker as is; it will be unused. Actually, replace with StopHandle usage below.

# 3. Replace set_station_markers to create StopHandle items
old_set_markers = """    def set_station_markers(self, stations: list[dict]) -> None:
        # Clear old station markers
        for item in list(self._scene.items()):
            if isinstance(item, StationMarker):
                self._scene.removeItem(item)
        self._station_markers = []
        for s in stations:
            m = StationMarker(s["x"], s["y"], s["station"], s["path_id"], s["pos_m"])
            m.on_clicked = None
            self._scene.addItem(m)
            self._station_markers.append(m)
"""

new_set_markers = """    def set_station_markers(self, stations: list[dict]) -> None:
        # Clear old station markers
        for item in list(self._scene.items()):
            if isinstance(item, (StationMarker, StopHandle)):
                self._scene.removeItem(item)
        self._station_markers = []
        for s in stations:
            m = StopHandle(s["station"], s["x"], s["y"], s["path_id"], s["pos_m"])
            m.on_moved = lambda n, nx, ny: self.stop_moved.emit(n, nx, ny)
            m.on_selected = lambda n: self.stop_selected.emit(n)
            self._scene.addItem(m)
            self._station_markers.append(m)
"""

if old_set_markers not in text:
    raise ValueError("set_station_markers block not found")
text = text.replace(old_set_markers, new_set_markers)

# 4. Add signals for stop movement/selection
old_signals = """class TrackView(QGraphicsView):
    anchor_selected = Signal(int)
    anchor_moved = Signal(int, float, float)
    anchor_added = Signal(float, float)
    station_selected = Signal(str, int, float)
"""

new_signals = """class TrackView(QGraphicsView):
    anchor_selected = Signal(int)
    anchor_moved = Signal(int, float, float)
    anchor_added = Signal(float, float)
    station_selected = Signal(str, int, float)
    stop_moved = Signal(str, float, float)
    stop_selected = Signal(str)
"""

if old_signals not in text:
    raise ValueError("TrackView signals not found")
text = text.replace(old_signals, new_signals)

# 5. Update mousePressEvent to prioritize stop handles over station marker fallback
old_mouse_press = """    def mousePressEvent(self, event: QMouseEvent):
        if self._add_mode and event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            self.anchor_added.emit(pos.x(), pos.y())
            return
        # If a station marker is under the click, emit its index
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            hit = self.station_marker_clicked(pos)
            if hit is not None:
                self.station_selected.emit(hit.label, hit.path_id, hit.pos_m)
                event.accept()
                return
        super().mousePressEvent(event)
"""

new_mouse_press = """    def mousePressEvent(self, event: QMouseEvent):
        if self._add_mode and event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            self.anchor_added.emit(pos.x(), pos.y())
            return
        # Stop handles are real items and will receive clicks naturally; no special hit test needed.
        super().mousePressEvent(event)
"""

if old_mouse_press not in text:
    raise ValueError("mousePressEvent block not found")
text = text.replace(old_mouse_press, new_mouse_press)

# 6. Connect stop signals in MainWindow
old_connections = """        self._view = TrackView()
        self._view.anchor_selected.connect(self._on_selected)
        self._view.anchor_moved.connect(self._on_moved)
        self._view.anchor_added.connect(self._on_added)
        self._view.station_selected.connect(self._on_station_from_image)
"""

new_connections = """        self._view = TrackView()
        self._view.anchor_selected.connect(self._on_selected)
        self._view.anchor_moved.connect(self._on_moved)
        self._view.anchor_added.connect(self._on_added)
        self._view.station_selected.connect(self._on_station_from_image)
        self._view.stop_moved.connect(self._on_stop_moved)
        self._view.stop_selected.connect(self._on_stop_selected)
"""

if old_connections not in text:
    raise ValueError("TrackView connections not found")
text = text.replace(old_connections, new_connections)

# 7. Add stop buttons to sidebar
old_station_list = """        self._station_list = QListWidget()
        self._station_list.setMaximumHeight(220)
        self._station_list.itemClicked.connect(self._on_station_clicked)
        v.addWidget(self._station_list)

        v.addStretch()
"""

new_station_list = """        self._station_list = QListWidget()
        self._station_list.setMaximumHeight(220)
        self._station_list.itemClicked.connect(self._on_station_clicked)
        v.addWidget(self._station_list)

        self._btn_save_stops = QPushButton("Save Stop Positions")
        self._btn_save_stops.setToolTip("Write adjusted pixel positions to track_points_adjusted.csv")
        self._btn_save_stops.clicked.connect(self._save_stops)
        v.addWidget(self._btn_save_stops)

        v.addStretch()
"""

if old_station_list not in text:
    raise ValueError("station_list block not found")
text = text.replace(old_station_list, new_station_list)

# 8. Add stop handling methods
old_on_station_from_image = """    def _on_station_from_image(self, name: str, path_id: int, pos_m: float):
        self._highlight_station(name)

    def _highlight_station(self, name: str):
        # Select in list
        for i in range(self._station_list.count()):
            item = self._station_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == name:
                self._station_list.setCurrentItem(item)
                self._station_list.scrollToItem(item)
                break
        # Highlight marker
        for m in getattr(self._view, "_station_markers", []):
            m.set_highlighted(m.label == name)
        # Center view on station
        for s in self._stations:
            if s["station"] == name:
                self._view.centerOn(s["x"], s["y"])
                break
"""

new_stop_methods = """    def _on_station_from_image(self, name: str, path_id: int, pos_m: float):
        self._highlight_station(name)

    def _on_stop_selected(self, name: str):
        self._highlight_station(name)

    def _on_stop_moved(self, name: str, x: float, y: float):
        for s in self._stations:
            if s["station"] == name:
                s["x"] = x
                s["y"] = y
                break
        self._refresh_station_list()
        self._highlight_station(name)

    def _highlight_station(self, name: str):
        # Select in list
        for i in range(self._station_list.count()):
            item = self._station_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == name:
                self._station_list.setCurrentItem(item)
                self._station_list.scrollToItem(item)
                break
        # Highlight marker
        for m in getattr(self._view, "_station_markers", []):
            m.set_highlighted(m.name == name)
        # Center view on station
        for s in self._stations:
            if s["station"] == name:
                self._view.centerOn(s["x"], s["y"])
                break

    def _save_stops(self):
        \"\"\"Write adjusted stop pixel positions to track_points_adjusted.csv.\"\"\"
        try:
            out_path = self._csv_path.with_stem(self._csv_path.stem + "_adjusted")
            import csv
            with open(out_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Station", "Command", "Actual", "TrackLocation", "PixelX", "PixelY"])
                # Preserve original command/actual/location for each station
                orig = {r.get("station", "").strip(): r for r in load_csv_points(self._csv_path)}
                for s in self._stations:
                    r = orig.get(s["station"], {})
                    writer.writerow([
                        s["station"],
                        r.get("command", ""),
                        r.get("actual", ""),
                        r.get("location", ""),
                        f"{s['x']:.2f}",
                        f"{s['y']:.2f}",
                    ])
            self._lbl_info.setText(f"Saved adjusted stops to {out_path.name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
"""

if old_on_station_from_image not in text:
    raise ValueError("_on_station_from_image block not found")
text = text.replace(old_on_station_from_image, new_stop_methods)

# 9. Update _refresh_station_list to use m.name instead of m.label
old_refresh_list = """    def _refresh_station_list(self):
        self._station_list.clear()
        for s in self._stations:
            label = PATH_LABELS.get(s["path_id"], f"Path {s['path_id']}")
            item = QListWidgetItem(
                f"{s['station']}  — Path {s['path_id']} @ {s['pos_m']:.3f}m  ({s['x']:.0f},{s['y']:.0f})"
            )
            item.setData(Qt.ItemDataRole.UserRole, s["station"])
            color = PATH_COLORS.get(s["path_id"], QColor("yellow"))
            item.setForeground(color)
            self._station_list.addItem(item)
"""

new_refresh_list = """    def _refresh_station_list(self):
        self._station_list.clear()
        for s in self._stations:
            item = QListWidgetItem(
                f"{s['station']}  — Path {s['path_id']} @ {s['pos_m']:.3f}m  ({s['x']:.0f},{s['y']:.0f})"
            )
            item.setData(Qt.ItemDataRole.UserRole, s["station"])
            color = PATH_COLORS.get(s["path_id"], QColor("yellow"))
            item.setForeground(color)
            self._station_list.addItem(item)
"""

if old_refresh_list not in text:
    raise ValueError("_refresh_station_list block not found")
text = text.replace(old_refresh_list, new_refresh_list)

# 10. Refresh stops on regenerate
old_regen = """    def _regenerate(self):
        # Just refresh the interpolated view from current anchors
        self._view.set_master(self._anchors, self._junction_indices)
        self._refresh_path_list()
        self._load_stations()
        self._update_info()
"""

# Already does _load_stations; but that resets positions. Don't change.

# Restore line endings
if sep == "\r\n":
    text = text.replace("\n", "\r\n")

with open(p, "wb") as f:
    f.write(text.encode("utf-8"))

print("main.py modified for draggable stops")
