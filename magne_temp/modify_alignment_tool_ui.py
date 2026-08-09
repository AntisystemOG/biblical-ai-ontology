"""Rewrite alignment tool UI to focus on stop placement."""
from pathlib import Path

p = Path(r"C:\AI Projects\MagneMotionMonitor\Track Alignment program\main.py")
with open(p, "rb") as f:
    data = f.read()

sep = "\r\n" if b"\r\n" in data else "\n"
text = data.decode("utf-8").replace("\r\n", "\n")

# Replace _build_ui entirely
old_build_ui = """    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        self._view = TrackView()
        self._view.anchor_selected.connect(self._on_selected)
        self._view.anchor_moved.connect(self._on_moved)
        self._view.anchor_added.connect(self._on_added)
        self._view.station_selected.connect(self._on_station_from_image)
        self._view.stop_moved.connect(self._on_stop_moved)
        self._view.stop_selected.connect(self._on_stop_selected)

        sidebar = QWidget()
        sidebar.setMaximumWidth(340)
        v = QVBoxLayout(sidebar)
        v.setSpacing(8)

        v.addWidget(QLabel("<b>Master Path</b>"))
        info = QLabel(
            "Edit one continuous loop. Yellow dots are anchor points; larger "
            "black-ringed dots are the 6 PLC path junctions. Colored lines show "
            "the interpolated PLC paths."
        )
        info.setWordWrap(True)
        v.addWidget(info)

        gb = QGroupBox("Actions")
        gb_v = QVBoxLayout(gb)

        self._btn_regen = QPushButton("Regenerate PLC Paths")
        self._btn_regen.setToolTip("Interpolate between current anchors and resample the 6 PLC paths")
        self._btn_regen.clicked.connect(self._regenerate)
        gb_v.addWidget(self._btn_regen)

        self._btn_reduce = QPushButton("Reduce Anchors")
        self._btn_reduce.setToolTip("Run RDP simplification between junctions to remove unnecessary anchors")
        self._btn_reduce.clicked.connect(self._reduce_now)
        gb_v.addWidget(self._btn_reduce)

        self._btn_reset = QPushButton("Reset to Loaded 6 Paths")
        self._btn_reset.clicked.connect(self._reset_to_loaded)
        gb_v.addWidget(self._btn_reset)
        v.addWidget(gb)

        v.addWidget(QLabel("<b>Resample Spacing (px)</b>"))
        self._spin_spacing = QDoubleSpinBox()
        self._spin_spacing.setRange(2.0, 30.0)
        self._spin_spacing.setValue(self._spacing)
        self._spin_spacing.setSingleStep(1.0)
        self._spin_spacing.valueChanged.connect(self._spacing_changed)
        v.addWidget(self._spin_spacing)

        v.addWidget(QLabel("<b>Selected Anchor</b>"))
        form = QFormLayout()
        self._spin_x = QSpinBox()
        self._spin_x.setRange(0, 5000)
        self._spin_x.valueChanged.connect(self._on_spin_changed)
        self._spin_y = QSpinBox()
        self._spin_y.setRange(0, 5000)
        self._spin_y.valueChanged.connect(self._on_spin_changed)
        form.addRow("X:", self._spin_x)
        form.addRow("Y:", self._spin_y)
        v.addLayout(form)

        self._btn_del_anchor = QPushButton("Delete Selected Anchor")
        self._btn_del_anchor.setToolTip("Junction points cannot be deleted")
        self._btn_del_anchor.clicked.connect(self._delete_selected_anchor)
        v.addWidget(self._btn_del_anchor)

        self._chk_add = QCheckBox("Add Anchor Mode (click on image)")
        self._chk_add.stateChanged.connect(lambda s: self._view.set_add_mode(s == Qt.CheckState.Checked.value))
        v.addWidget(self._chk_add)

        self._lbl_info = QLabel("Ready")
        self._lbl_info.setWordWrap(True)
        self._lbl_info.setStyleSheet("background: #f0f0f0; padding: 6px; border: 1px solid #ccc;")
        v.addWidget(self._lbl_info)

        v.addSpacing(10)
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

        self._btn_save_stops = QPushButton("Save Stop Positions")
        self._btn_save_stops.setToolTip("Write adjusted pixel positions to track_points_adjusted.csv")
        self._btn_save_stops.clicked.connect(self._save_stops)
        v.addWidget(self._btn_save_stops)

        v.addStretch()

        self._btn_save = QPushButton("Save to track_photo.py")
        self._btn_save.setStyleSheet("background: #2980b9; color: white; font-weight: bold; padding: 8px;")
        self._btn_save.clicked.connect(self._save)
        v.addWidget(self._btn_save)

        self._btn_export = QPushButton("Export waypoints to JSON...")
        self._btn_export.clicked.connect(self._export_json)
        v.addWidget(self._btn_export)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._view)
        splitter.addWidget(sidebar)
        splitter.setSizes([1150, 300])
        layout.addWidget(splitter)
"""

new_build_ui = """    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(4, 4, 4, 4)

        self._view = TrackView()
        self._view.anchor_selected.connect(self._on_selected)
        self._view.anchor_moved.connect(self._on_moved)
        self._view.anchor_added.connect(self._on_added)
        self._view.station_selected.connect(self._on_station_from_image)
        self._view.stop_moved.connect(self._on_stop_moved)
        self._view.stop_selected.connect(self._on_stop_selected)

        # ── Sidebar: stop-centric navigation ─────────────────────────────────
        sidebar = QWidget()
        sidebar.setMaximumWidth(380)
        v = QVBoxLayout(sidebar)
        v.setSpacing(6)

        title = QLabel("<h2>MagneMotion Stop Placement</h2>")
        v.addWidget(title)

        info = QLabel(
            "Drag each white dot onto the exact rail stop position. "
            "The list shows every named pallet stop from the machine. "
            "Click a list item to jump to it. Save when done."
        )
        info.setWordWrap(True)
        v.addWidget(info)

        # Search/filter
        self._station_filter = QLineEdit()
        self._station_filter.setPlaceholderText("Search stops...")
        self._station_filter.textChanged.connect(self._refresh_station_list)
        v.addWidget(self._station_filter)

        # Stop list
        v.addWidget(QLabel("<b>All Stopping Points</b>"))
        self._station_list = QListWidget()
        self._station_list.setMaximumHeight(600)
        self._station_list.itemClicked.connect(self._on_station_clicked)
        v.addWidget(self._station_list)

        # Selected stop edit
        v.addWidget(QLabel("<b>Selected Stop</b>"))
        form = QFormLayout()
        self._spin_stop_x = QSpinBox()
        self._spin_stop_x.setRange(0, 5000)
        self._spin_stop_x.valueChanged.connect(self._on_stop_spin_changed)
        self._spin_stop_y = QSpinBox()
        self._spin_stop_y.setRange(0, 5000)
        self._spin_stop_y.valueChanged.connect(self._on_stop_spin_changed)
        form.addRow("Pixel X:", self._spin_stop_x)
        form.addRow("Pixel Y:", self._spin_stop_y)
        v.addLayout(form)

        self._btn_save_stops = QPushButton("Save Stop Positions")
        self._btn_save_stops.setToolSheet("background: #27ae60; color: white; font-weight: bold; padding: 8px;")
        self._btn_save_stops.setToolTip("Write adjusted pixel positions to track_points_adjusted.csv")
        self._btn_save_stops.clicked.connect(self._save_stops)
        v.addWidget(self._btn_save_stops)

        # Anchor/path section (collapsible)
        self._gb_anchors = QGroupBox("Rail Path Anchors (advanced)")
        gb_v = QVBoxLayout(self._gb_anchors)

        self._btn_regen = QPushButton("Regenerate PLC Paths")
        self._btn_regen.setToolTip("Interpolate between current anchors and resample the 6 PLC paths")
        self._btn_regen.clicked.connect(self._regenerate)
        gb_v.addWidget(self._btn_regen)

        self._btn_reduce = QPushButton("Reduce Anchors")
        self._btn_reduce.setToolTip("Run RDP simplification between junctions to remove unnecessary anchors")
        self._btn_reduce.clicked.connect(self._reduce_now)
        gb_v.addWidget(self._btn_reduce)

        self._btn_reset = QPushButton("Reset to Loaded 6 Paths")
        self._btn_reset.clicked.connect(self._reset_to_loaded)
        gb_v.addWidget(self._btn_reset)

        self._btn_del_anchor = QPushButton("Delete Selected Anchor")
        self._btn_del_anchor.setToolTip("Junction points cannot be deleted")
        self._btn_del_anchor.clicked.connect(self._delete_selected_anchor)
        gb_v.addWidget(self._btn_del_anchor)

        self._chk_add = QCheckBox("Add Anchor Mode (click on image)")
        self._chk_add.stateChanged.connect(lambda s: self._view.set_add_mode(s == Qt.CheckState.Checked.value))
        gb_v.addWidget(self._chk_add)

        self._path_list = QListWidget()
        self._path_list.setMaximumHeight(100)
        gb_v.addWidget(self._path_list)

        self._gb_anchors.setCheckable(True)
        self._gb_anchors.setChecked(False)
        v.addWidget(self._gb_anchors)

        self._lbl_info = QLabel("Ready")
        self._lbl_info.setWordWrap(True)
        self._lbl_info.setStyleSheet("background: #f0f0f0; padding: 6px; border: 1px solid #ccc;")
        v.addWidget(self._lbl_info)

        self._btn_save = QPushButton("Save Path to track_photo.py")
        self._btn_save.setStyleSheet("background: #2980b9; color: white; font-weight: bold; padding: 8px;")
        self._btn_save.clicked.connect(self._save)
        v.addWidget(self._btn_save)

        self._btn_export = QPushButton("Export waypoints to JSON...")
        self._btn_export.clicked.connect(self._export_json)
        v.addWidget(self._btn_export)

        v.addStretch()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._view)
        splitter.addWidget(sidebar)
        splitter.setSizes([1350, 360])
        layout.addWidget(splitter)
"""

if old_build_ui not in text:
    raise ValueError("old _build_ui not found")
text = text.replace(old_build_ui, new_build_ui)

# Add QLineEdit import if missing
imports_block = "from PySide6.QtWidgets import ("
if imports_block in text and "QLineEdit" not in text:
    text = text.replace("QHBoxLayout,", "QHBoxLayout, QLineEdit,")

# Replace __init__ window size
old_init = """    def __init__(self):
        super().__init__()
        self.setWindowTitle("MagneMotion Track Alignment — Single Path")
        self.resize(1500, 950)
"""
new_init = """    def __init__(self):
        super().__init__()
        self.setWindowTitle("MagneMotion Track Stop Placement")
        self.resize(1800, 1000)
"""
if old_init in text:
    text = text.replace(old_init, new_init)

# Replace _update_info to be stop-centric
old_update_info = """    def _update_info(self):
        plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=False)
        total = sum(len(v) for v in plc.values())
        self._lbl_info.setText(
            f"Anchors: {len(self._anchors)} (junctions: {len(self._junction_indices)})\\n"
            f"Master length: {_poly_length(self._anchors):.0f}px\\n"
            f"PLC path points: {total}\\n\\n"
            "Drag anchors to reshape. Add anchors for curve control. "
            "Junctions (black ring) define where one PLC path ends and the next begins."
        )
"""
new_update_info = """    def _update_info(self):
        plc = _generate_plc_paths(self._anchors, self._junction_indices, self._spacing, smooth=False)
        total = sum(len(v) for v in plc.values())
        self._lbl_info.setText(
            f"Stops: {len(self._stations)}\\n"
            f"Anchors: {len(self._anchors)} (junctions: {len(self._junction_indices)})\\n"
            f"PLC path points: {total}\\n\\n"
            "1. Drag white stop dots onto exact rail positions.\\n"
            "2. Save Stop Positions writes track_points_adjusted.csv.\\n"
            "3. If the rail path itself is off, expand Rail Path Anchors."
        )
"""
if old_update_info in text:
    text = text.replace(old_update_info, new_update_info)

# Replace _refresh_station_list to support filter
old_refresh_list = """    def _refresh_station_list(self):
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
new_refresh_list = """    def _refresh_station_list(self, text: str = ""):
        self._station_list.clear()
        filt = text.lower() if text else ""
        for s in self._stations:
            display = f"{s['station']}  — Path {s['path_id']} @ {s['pos_m']:.3f}m  ({s['x']:.0f},{s['y']:.0f})"
            if filt and filt not in display.lower():
                continue
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, s["station"])
            color = PATH_COLORS.get(s["path_id"], QColor("yellow"))
            item.setForeground(color)
            self._station_list.addItem(item)
"""
if old_refresh_list not in text:
    raise ValueError("_refresh_station_list block not found")
text = text.replace(old_refresh_list, new_refresh_list)

# Add _on_stop_spin_changed method and update _on_stop_selected
old_on_stop_selected = """    def _on_stop_selected(self, name: str):
        self._highlight_station(name)

    def _on_stop_moved(self, name: str, x: float, y: float):
        for s in self._stations:
            if s["station"] == name:
                s["x"] = x
                s["y"] = y
                break
        self._refresh_station_list()
        self._highlight_station(name)
"""

new_on_stop_selected = """    def _on_stop_selected(self, name: str):
        self._current_stop_name = name
        self._highlight_station(name)
        for s in self._stations:
            if s["station"] == name:
                self._spin_stop_x.blockSignals(True)
                self._spin_stop_y.blockSignals(True)
                self._spin_stop_x.setValue(int(round(s["x"])))
                self._spin_stop_y.setValue(int(round(s["y"])))
                self._spin_stop_x.blockSignals(False)
                self._spin_stop_y.blockSignals(False)
                break

    def _on_stop_moved(self, name: str, x: float, y: float):
        for s in self._stations:
            if s["station"] == name:
                s["x"] = x
                s["y"] = y
                break
        self._refresh_station_list(self._station_filter.text())
        self._highlight_station(name)

    def _on_stop_spin_changed(self):
        if not getattr(self, "_current_stop_name", None):
            return
        name = self._current_stop_name
        x = float(self._spin_stop_x.value())
        y = float(self._spin_stop_y.value())
        for s in self._stations:
            if s["station"] == name:
                s["x"] = x
                s["y"] = y
                break
        # Move marker without recreating all markers
        for m in getattr(self._view, "_station_markers", []):
            if m.name == name:
                m.setPos(x, y)
                break
        self._refresh_station_list(self._station_filter.text())
        self._view.centerOn(x, y)
"""

if old_on_stop_selected not in text:
    raise ValueError("_on_stop_selected block not found")
text = text.replace(old_on_stop_selected, new_on_stop_selected)

# Update _highlight_station to not forcibly recenter every time (only when user requests)
old_highlight = """    def _highlight_station(self, name: str):
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
"""

new_highlight = """    def _highlight_station(self, name: str, center: bool = True):
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
        if center:
            for s in self._stations:
                if s["station"] == name:
                    self._view.centerOn(s["x"], s["y"])
                    break
"""

if old_highlight not in text:
    raise ValueError("_highlight_station block not found")
text = text.replace(old_highlight, new_highlight)

# Update _on_station_clicked to use center=True and trigger stop selection logic
old_on_station_clicked = """    def _on_station_clicked(self, item: QListWidgetItem):
        name = item.data(Qt.ItemDataRole.UserRole)
        self._highlight_station(name)
"""

new_on_station_clicked = """    def _on_station_clicked(self, item: QListWidgetItem):
        name = item.data(Qt.ItemDataRole.UserRole)
        self._current_stop_name = name
        self._highlight_station(name)
        for s in self._stations:
            if s["station"] == name:
                self._spin_stop_x.blockSignals(True)
                self._spin_stop_y.blockSignals(True)
                self._spin_stop_x.setValue(int(round(s["x"])))
                self._spin_stop_y.setValue(int(round(s["y"])))
                self._spin_stop_x.blockSignals(False)
                self._spin_stop_y.blockSignals(False)
                break
"""

if old_on_station_clicked not in text:
    raise ValueError("_on_station_clicked block not found")
text = text.replace(old_on_station_clicked, new_on_station_clicked)

# Update init fields to add _current_stop_name
old_init_fields = """        self._current_idx: int | None = None
        self._spacing = 6.0
        self._stations: list[dict] = []
"""
new_init_fields = """        self._current_idx: int | None = None
        self._spacing = 6.0
        self._stations: list[dict] = []
        self._current_stop_name: str | None = None
"""
if old_init_fields in text:
    text = text.replace(old_init_fields, new_init_fields)

# Fix typo setToolSheet -> setStyleSheet
if "setToolSheet" in text:
    text = text.replace("setToolSheet", "setStyleSheet")

# Restore line endings
if sep == "\r\n":
    text = text.replace("\n", "\r\n")

with open(p, "wb") as f:
    f.write(text.encode("utf-8"))

print("UI rewritten for stop-centric navigation")
