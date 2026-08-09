"""Modify Track Alignment program/main.py to add labeled station markers."""
from pathlib import Path

p = Path(r"C:\AI Projects\MagneMotionMonitor\Track Alignment program\main.py")
# Read preserving CRLF
with open(p, "rb") as f:
    data = f.read()

# Work with LF internally for easier edits, then restore CRLF
if b"\r\n" in data:
    sep = "\r\n"
    text = data.decode("utf-8").replace("\r\n", "\n")
else:
    sep = "\n"
    text = data.decode("utf-8")

# 1. Update PATH_LABELS (already updated by hand; skip if present)
old_labels = """PATH_LABELS: dict[int, str] = {
    1: "Right Spur Entry/Exit (Mold 1 side)",
    2: "Mold 1 Spur (Unload / Mold Direction Check)",
    3: "Top Main Rail (Load Roller / Inspection / Roller Test / Offload)",
    4: "Mold 2 Spur (Pre-Load / Load / Cooling)",
    5: "Left Spur Entry/Exit (Mold 2 side)",
    6: "Bottom Return Rail (Home / Cleanout / Return to Load)",
}"""

new_labels = """PATH_LABELS: dict[int, str] = {
    1: "Mold 1 Entry/Exit (right junction stub)",
    2: "Mold 1 Spur — right vertical loop",
    3: "Lower connector (HOME / Cleanout / return)",
    4: "Mold 2 Spur — left vertical loop",
    5: "Mold 2 Entry/Exit (left junction stub)",
    6: "Top main rail (Pre-Load / Inspection / Roller Test / Offload)",
}

# Map CSV TrackLocation values to PLC path IDs. These match the *code* semantics
# used by mm_monitor/track_photo.py and track_geometry.py.
TRACK_LOCATION_TO_PATH: dict[str, int] = {
    "Top Main Rail": 6,
    "Right Vertical Loop": 2,
    "Left Vertical Loop": 4,
    "Middle Connector": 3,
}"""

if old_labels in text:
    text = text.replace(old_labels, new_labels)
else:
    print("PATH_LABELS already updated; skipping")

# 2. Insert _station_pixel_positions before _build_anchors_from_paths
insert_marker = "def _build_anchors_from_paths("
if insert_marker not in text:
    raise ValueError("insert marker not found")

station_func = """def _station_pixel_positions(
    csv_rows: list[dict],
    track_py_path: Path,
) -> list[dict]:
    \"\"\"Convert CSV station positions (meters) to pixel (x, y) using current waypoints.\"\"\"
    import importlib.util
    spec = importlib.util.spec_from_file_location("track_photo_module", str(track_py_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Need real path lengths to build the model; import project track_geometry
    sys.path.insert(0, str(PROJECT_DIR))
    try:
        from mm_monitor.track_geometry import build_track
        track = build_track()
        real_lengths = {pid: pg.length for pid, pg in track.paths.items()}
    finally:
        sys.path.pop(0)

    model = mod.PhotoTrackModel(real_lengths)

    results = []
    for row in csv_rows:
        loc = row.get("TrackLocation", "").strip()
        path_id = TRACK_LOCATION_TO_PATH.get(loc)
        if path_id is None:
            continue
        try:
            pos_m = float(row.get("Actual", row.get("Command", 0)) or 0)
        except ValueError:
            continue
        pt = model.point_at(path_id, pos_m)
        if pt is None:
            continue
        results.append({
            "station": row.get("Station", "").strip(),
            "path_id": path_id,
            "location": loc,
            "pos_m": pos_m,
            "x": pt[0],
            "y": pt[1],
        })
    return results


"""

text = text.replace(insert_marker, station_func + insert_marker)

# 3. Add StationMarker class after ReferenceMarker class
old_ref_end = """class ReferenceMarker(QGraphicsEllipseItem):
    \"\"\"Small static marker showing where a station should be.\"\"\"

    def __init__(self, x: float, y: float, label: str):
        super().__init__(-4, -4, 8, 8)
        self.setPos(x, y)
        self.setPen(QPen(QColor("black"), 1))
        self.setBrush(QColor("yellow"))
        self.setZValue(15)
        text = QGraphicsSimpleTextItem(label, self)
        text.setBrush(QColor("black"))
        text.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        text.setPos(8, -8)
"""

new_ref_end = """class ReferenceMarker(QGraphicsEllipseItem):
    \"\"\"Small static marker showing where a station should be.\"\"\"

    def __init__(self, x: float, y: float, label: str):
        super().__init__(-4, -4, 8, 8)
        self.setPos(x, y)
        self.setPen(QPen(QColor("black"), 1))
        self.setBrush(QColor("yellow"))
        self.setZValue(15)
        text = QGraphicsSimpleTextItem(label, self)
        text.setBrush(QColor("black"))
        text.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        text.setPos(8, -8)


class StationMarker(QGraphicsEllipseItem):
    \"\"\"Labeled station/pallet-stop marker from track_points.csv.\"\"\"

    def __init__(self, x: float, y: float, label: str, path_id: int, pos_m: float):
        super().__init__(-6, -6, 12, 12)
        self.setPos(x, y)
        self.setPen(QPen(Qt.black, 2))
        color = PATH_COLORS.get(path_id, QColor("yellow"))
        self.setBrush(color)
        self.setZValue(20)
        self.label = label
        self.path_id = path_id
        self.pos_m = pos_m
        text = QGraphicsSimpleTextItem(label, self)
        text.setBrush(QColor("black"))
        text.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        text.setPos(10, -10)
        # White halo behind text for readability
        halo = QGraphicsSimpleTextItem(label, self)
        halo.setBrush(QColor("white"))
        halo.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        halo.setPos(11, -9)
        halo.setZValue(-1)
        text.setZValue(0)

    def set_highlighted(self, highlighted: bool):
        pen = QPen(QColor("red") if highlighted else Qt.black, 4 if highlighted else 2)
        self.setPen(pen)
        self.setZValue(40 if highlighted else 20)
"""

if old_ref_end not in text:
    raise ValueError("ReferenceMarker block not found")
text = text.replace(old_ref_end, new_ref_end)

# 4. Modify TrackView to add station markers
# Find add_reference_markers and replace with combined add_markers + add station list support
old_add_ref = """    def add_reference_markers(self, markers: list[tuple[float, float, str]]) -> None:
        for x, y, label in markers:
            self._scene.addItem(ReferenceMarker(x, y, label))
"""

new_add_ref = """    def add_reference_markers(self, markers: list[tuple[float, float, str]]) -> None:
        for x, y, label in markers:
            self._scene.addItem(ReferenceMarker(x, y, label))

    def set_station_markers(self, stations: list[dict]) -> None:
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

    def station_marker_clicked(self, scene_pos) -> dict | None:
        \"\"\"Find the nearest station marker to a scene click.\"\"\"
        best = None
        best_d2 = 400.0  # 20px threshold
        for m in getattr(self, "_station_markers", []):
            dx = m.pos().x() - scene_pos.x()
            dy = m.pos().y() - scene_pos.y()
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best = m
        return best
"""

if old_add_ref not in text:
    raise ValueError("add_reference_markers block not found")
text = text.replace(old_add_ref, new_add_ref)

# 5. Add mousePressEvent handling for station marker clicks
old_mouse_press = """    def mousePressEvent(self, event: QMouseEvent):
        if self._add_mode and event.button() == Qt.MouseButton.LeftButton:
            pos = self.mapToScene(event.pos())
            self.anchor_added.emit(pos.x(), pos.y())
            return
        super().mousePressEvent(event)
"""

new_mouse_press = """    def mousePressEvent(self, event: QMouseEvent):
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

if old_mouse_press not in text:
    raise ValueError("mousePressEvent block not found")
text = text.replace(old_mouse_press, new_mouse_press)

# 6. Add station_selected signal to TrackView class
old_signals = """class TrackView(QGraphicsView):
    anchor_selected = Signal(int)
    anchor_moved = Signal(int, float, float)
    anchor_added = Signal(float, float)
"""

new_signals = """class TrackView(QGraphicsView):
    anchor_selected = Signal(int)
    anchor_moved = Signal(int, float, float)
    anchor_added = Signal(float, float)
    station_selected = Signal(str, int, float)
"""

if old_signals not in text:
    raise ValueError("TrackView signals not found")
text = text.replace(old_signals, new_signals)

# 7. Modify MainWindow to load stations, add list, sync selection
# Add connection in _build_ui right after path_list
old_path_list = """        v.addSpacing(10)
        v.addWidget(QLabel("<b>PLC Paths</b>"))
        self._path_list = QListWidget()
        self._path_list.setMaximumHeight(140)
        v.addWidget(self._path_list)

        v.addStretch()
"""

new_path_list = """        v.addSpacing(10)
        v.addWidget(QLabel("<b>PLC Paths</b>"))
        self._path_list = QListWidget()
        self._path_list.setMaximumHeight(120)
        v.addWidget(self._path_list)

        v.addWidget(QLabel("<b>Stations / Pallet Stops</b>"))
        info2 = QLabel(
            "Labeled points from track_points.csv. Click one to center the "
            "view on it. Positions update when the path changes."
        )
        info2.setWordWrap(True)
        v.addWidget(info2)
        self._station_list = QListWidget()
        self._station_list.setMaximumHeight(220)
        self._station_list.itemClicked.connect(self._on_station_clicked)
        v.addWidget(self._station_list)

        v.addStretch()
"""

if old_path_list not in text:
    raise ValueError("path_list block not found")
text = text.replace(old_path_list, new_path_list)

# 8. Connect station_selected signal
old_connections = """        self._view = TrackView()
        self._view.anchor_selected.connect(self._on_selected)
        self._view.anchor_moved.connect(self._on_moved)
        self._view.anchor_added.connect(self._on_added)
"""

new_connections = """        self._view = TrackView()
        self._view.anchor_selected.connect(self._on_selected)
        self._view.anchor_moved.connect(self._on_moved)
        self._view.anchor_added.connect(self._on_added)
        self._view.station_selected.connect(self._on_station_from_image)
"""

if old_connections not in text:
    raise ValueError("TrackView connections not found")
text = text.replace(old_connections, new_connections)

# 9. Add _stations list field + load in _load_all
old_init_fields = """        self._anchors: list[tuple[float, float]] = []
        self._junction_indices: list[int] = []
        self._current_idx: int | None = None
        self._spacing = 6.0
"""

new_init_fields = """        self._anchors: list[tuple[float, float]] = []
        self._junction_indices: list[int] = []
        self._current_idx: int | None = None
        self._spacing = 6.0
        self._stations: list[dict] = []
"""

if old_init_fields not in text:
    raise ValueError("init fields not found")
text = text.replace(old_init_fields, new_init_fields)

# 10. Load stations after loading waypoints in _load_all
old_load_wps = """        self._view.load_image(self._img_path)

        self._anchors, self._junction_indices = _build_anchors_from_paths(wps, epsilon=4.0)
        self._view.set_master(self._anchors, self._junction_indices)
        self._refresh_path_list()
        self._update_info()
"""

new_load_wps = """        self._view.load_image(self._img_path)

        self._anchors, self._junction_indices = _build_anchors_from_paths(wps, epsilon=4.0)
        self._view.set_master(self._anchors, self._junction_indices)
        self._refresh_path_list()

        self._load_stations()
        self._update_info()
"""

if old_load_wps not in text:
    raise ValueError("_load_all waypoint load block not found")
text = text.replace(old_load_wps, new_load_wps)

# 11. Add _load_stations, _refresh_station_list, _on_station_clicked, _on_station_from_image methods
old_on_added = """    def _on_added(self, x: float, y: float):
        # Find closest master segment and insert anchor there
        best_idx = 0
        best_dist = float("inf")
        n = len(self._anchors)
        for i in range(n):
            a = self._anchors[i]
            b = self._anchors[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            seg_len2 = dx * dx + dy * dy
            if seg_len2 == 0:
                d2 = _dist2((x, y), a)
            else:
                t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / seg_len2))
                proj = (a[0] + t * dx, a[1] + t * dy)
                d2 = _dist2((x, y), proj)
            if d2 < best_dist:
                best_dist = d2
                best_idx = i
        insert_at = (best_idx + 1) % (n + 1)
        self._anchors.insert(insert_at, (x, y))
        # Update indices
        self._junction_indices = [i if i < insert_at else i + 1 for i in self._junction_indices]
        self._current_idx = insert_at
        self._view.set_master(self._anchors, self._junction_indices)
        self._view.highlight(insert_at)
        self._refresh_path_list()
        self._update_info()
"""

new_on_added = """    def _load_stations(self):
        try:
            rows = load_csv_points(self._csv_path)
            self._stations = _station_pixel_positions(rows, self._py_path)
            self._view.set_station_markers(self._stations)
            self._refresh_station_list()
        except Exception as e:
            print(f"Could not load stations: {e}")
            self._stations = []

    def _refresh_station_list(self):
        self._station_list.clear()
        for s in self._stations:
            label = PATH_LABELS.get(s["path_id"], f"Path {s['path_id']}")
            item = QListWidgetItem(
                f"{s['station']}\n  Path {s['path_id']} @ {s['pos_m']:.3f}m — {s['x']:.0f},{s['y']:.0f}"
            )
            item.setData(Qt.ItemDataRole.UserRole, s["station"])
            color = PATH_COLORS.get(s["path_id"], QColor("yellow"))
            item.setForeground(color)
            self._station_list.addItem(item)

    def _on_station_clicked(self, item: QListWidgetItem):
        name = item.data(Qt.ItemDataRole.UserRole)
        self._highlight_station(name)

    def _on_station_from_image(self, name: str, path_id: int, pos_m: float):
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

    def _on_added(self, x: float, y: float):
        # Find closest master segment and insert anchor there
        best_idx = 0
        best_dist = float("inf")
        n = len(self._anchors)
        for i in range(n):
            a = self._anchors[i]
            b = self._anchors[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            seg_len2 = dx * dx + dy * dy
            if seg_len2 == 0:
                d2 = _dist2((x, y), a)
            else:
                t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / seg_len2))
                proj = (a[0] + t * dx, a[1] + t * dy)
                d2 = _dist2((x, y), proj)
            if d2 < best_dist:
                best_dist = d2
                best_idx = i
        insert_at = (best_idx + 1) % (n + 1)
        self._anchors.insert(insert_at, (x, y))
        # Update indices
        self._junction_indices = [i if i < insert_at else i + 1 for i in self._junction_indices]
        self._current_idx = insert_at
        self._view.set_master(self._anchors, self._junction_indices)
        self._view.highlight(insert_at)
        self._refresh_path_list()
        self._update_info()
"""

if old_on_added not in text:
    raise ValueError("_on_added block not found")
text = text.replace(old_on_added, new_on_added)

# 12. Refresh station markers after save/regenerate/reset since path may shift
old_regen = """    def _regenerate(self):
        # Just refresh the interpolated view from current anchors
        self._view.set_master(self._anchors, self._junction_indices)
        self._refresh_path_list()
        self._update_info()
"""

new_regen = """    def _regenerate(self):
        # Just refresh the interpolated view from current anchors
        self._view.set_master(self._anchors, self._junction_indices)
        self._refresh_path_list()
        self._load_stations()
        self._update_info()
"""

if old_regen not in text:
    raise ValueError("_regenerate block not found")
text = text.replace(old_regen, new_regen)

old_reset = """    def _reset_to_loaded(self):
        self._load_all()
"""

new_reset = """    def _reset_to_loaded(self):
        self._load_all()
"""
# No change needed for reset since _load_all calls _load_stations

old_spacing = """    def _spacing_changed(self, v: float):
        self._spacing = v
        self._view.set_master(self._anchors, self._junction_indices)
        self._refresh_path_list()
"""

new_spacing = """    def _spacing_changed(self, v: float):
        self._spacing = v
        self._view.set_master(self._anchors, self._junction_indices)
        self._refresh_path_list()
"""
# No change needed

# Restore line endings
if sep == "\r\n":
    text = text.replace("\n", "\r\n")

with open(p, "wb") as f:
    f.write(text.encode("utf-8"))

print("main.py modified successfully")
