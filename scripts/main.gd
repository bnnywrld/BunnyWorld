extends Control

const State = preload("res://scripts/world_state.gd")
const MapPalette = preload("res://scripts/map_palette.gd")
const SAVE_DIRECTORY := "user://saves"
const Catalog = preload("res://scripts/save_catalog.gd")
const OCEAN := Color("16394d")
var state := State.new()
var build_version: String = str(ProjectSettings.get_setting("application/config/version"))
var planet_material: ShaderMaterial
var physical_shader: Shader
var political_shader: Shader
var planet: Node3D
var camera: Camera3D
var world_view: SubViewport
var view_container: SubViewportContainer
const Surface = preload("res://scripts/relief_surface.gd")
var relief_surface: RefCounted
var foundation: RefCounted
var capture_foundation := ""
var camera_tilt_degrees := 0.0
var region_images: Array[Image] = []
var country_list: ItemList
var search: LineEdit
var country_tags: Array[String] = []
var details: VBoxContainer
var date_text: Label
var pause_button: Button
var speed_picker: OptionButton
var map_picker: OptionButton
var org_picker: OptionButton
var right_panel: PanelContainer
var territory_clip: Control
var territory_handle: Button
var territory_collapsed := false
var territory_tween: Tween
var top_left_box: VBoxContainer
var clock_box: PanelContainer
var map_box: PanelContainer
var selection_box: PanelContainer
var national_metric := "age"
var territory_metric := "age"
var territory_panel: PanelContainer
var territory_heading: VBoxContainer
var territory_scroll: ScrollContainer
var territory_details: VBoxContainer
var navigation_row: HBoxContainer
var stats_row: HFlowContainer
var control_panel: PanelContainer
var diplomatic_details: VBoxContainer
var control_heading: VBoxContainer
var diplomatic_heading: VBoxContainer
var command_frame: PanelContainer
var command_stack: VBoxContainer
var overlay_layout_dirty := true
var overlay_size := Vector2.ZERO
var overlay_screen := ""
var last_panel_layout: Array = []
var last_city_view: Array = []
var last_camera_view: Array = []
var tiny_state_markers: Control
var map_rendering: RefCounted
var ownership_visual_dirty := false
var map_frame_policy := preload("res://scripts/map_frame_policy.gd").new()
var map_diagnostics := preload("res://scripts/map_diagnostics.gd").new()
var last_pick_key: Array = []
var last_pick_uv := Vector2(-1, -1)
var pick_ray_marches := 0
var pick_cache_hits := 0
var terrain_shading: RefCounted
var pending_hover := false
var pending_hover_position := Vector2.ZERO
var hover_requests := 0
var hover_queries := 0
var display_coverage: RefCounted
var control_details: VBoxContainer
var title_label: Label
var subtitle_label: Label
var stats_label: Label
var game_menu: AcceptDialog
var cities: Array = []
var city_point_index: RefCounted
var city_projection_tests := 0
var city_layer: Control
var country_label_layer: Control
var country_labels_enabled := true
var country_labels_button: Button
var national_profile_expanded := false
var territory_profile_expanded := false
var hover_owner := 0.0
var hover_blend := 0.0
var city_timer: float = 0.0
var city_scenery_enabled := true
var graphics_setting := 0
var frame_setting := 0
var scenery_toggle: CheckButton
const Places = preload("res://scripts/place_catalog.gd")
var places := Places.new()
var place_dialog: AcceptDialog
var place_input: LineEdit
var place_results: ItemList
var place_hint: Label
var place_matches: Array[Dictionary] = []
var water_passages: Array = []
const Urban = preload("res://scripts/urban_scenery.gd")
var urban_scenery: Node3D
var rotation_velocity := Vector2.ZERO
var last_drag_time: int = 0
var flags := preload("res://scripts/flag_store.gd").new()
var Commands = preload("res://scripts/debug_commands.gd")
var console: AcceptDialog
var console_input: LineEdit
var console_log: RichTextLabel
var header_flag: TextureRect
var graphics_picker: OptionButton
var frame_picker: OptionButton
var panel_tweens: Dictionary = {}
var star_points: PackedVector3Array = PackedVector3Array()
var status: Label
var hover_text: Label
var hover_flag: TextureRect
var hover_country: String = ""
var hover_flags: Dictionary = {}
var hover_panel: PanelContainer
var border_materials: Array[ShaderMaterial] = []
var border_meshes: Dictionary = {}
var spatial_map_layers: RefCounted
var waterways_material: ShaderMaterial
var sea_image: Image
var sound_player: AudioStreamPlayer
var sound_enabled: bool = true
var sound_streams: Dictionary = {}
var org_ids: Array[String] = []
var map_mode: int = 6
var active_org: String = "ASEAN"
var show_regions: bool = false
var drag_start := Vector2.ZERO
var dragging: bool = false
var drag_distance: float = 0.0
var focus_tween: Tween
var palette_texture: ImageTexture
var owners_texture: ImageTexture
var distance: float = 3.65
var smoke: bool = false
var capture_path: String = ""
var capture_inspect: bool = false
var capture_memberships: bool = false
var capture_tooltip: bool = false
var capture_water: int = 0
var capture_state: int = 0
var capture_point := Vector2(-1000, -1000)
var capture_find := ""
var capture_to := ""
var list_filter: String = ""
var inspect_region: int = 0
var inspect_province: int = 0
var resident_terrain: RefCounted
var loading_overlay: ColorRect
var loading_progress: ProgressBar
var loading_caption: Label
var menu_background: TextureRect
var menu_photo: Texture2D
var state_preview := 0
var active_feature := ""
var boot_complete := false
var last_surface_view: Array = []
var last_hover_view: Array = []
var view_uniform_updates := 0
var camera_pose_updates := 0
var inspection_active: bool = false
var relations_reverse: bool = false
var relations_picker: OptionButton
var last_relation_day: int = -1
var opinion_labels: Array[Label] = []
var organization_textures: Dictionary = {}
var info_dialog: AcceptDialog
var game_ui: Control
var country_sidebar: VBoxContainer
var session_controls: HBoxContainer
var menu_screen: CenterContainer
var selection_bar: HBoxContainer
var campaign_label: Label
var legend: Label
var screen: String = "menu"
var save_dialog: ConfirmationDialog
var load_dialog: ConfirmationDialog
var save_name_field: LineEdit
var save_entries: ItemList
var load_entries: ItemList
var save_feedback: Label
var load_feedback: Label
var load_paths: Array[String] = []
var save_slots: Array[Dictionary] = []
var last_save_name: String = ""
var save_directory: String = SAVE_DIRECTORY
var popup_was_paused: bool = true
var pending_overwrite_path: String = ""
var overwrite_dialog: ConfirmationDialog
const OUTLOOK_COLORS := {"Western Outlook": Color("498fe0"), "Emerging Outlook": Color("d75650"), "Non-Aligned Outlook": Color("d7b553"), "Salafist Outlook": Color("52a56f"), "Nationalist Outlook": Color("aa77cc"), "Unspecified": Color("718793")}

func _ready() -> void:
	set_process(false)
	_build_loading_screen()
	await get_tree().process_frame
	await get_tree().process_frame
	Engine.max_fps = 60
	DisplayServer.window_set_min_size(Vector2i(1100, 700))
	var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	if not raw is Dictionary:
		var error := Label.new()
		error.text = "The starting world could not be loaded. Please extract the entire ZIP before launching."
		add_child(error)
		return
	state.initialize(raw)
	state.territory_changed.connect(func(_id: int,_old: String,_new: String): ownership_visual_dirty=true)
	_loading_stage(20, "Preparing world and interface")
	await get_tree().process_frame
	_build_sounds()
	_build_theme()
	_build_interface()
	_unify_country_panel()
	foundation = preload("res://scripts/foundation_ui.gd").new()
	foundation.build(self)
	_loading_stage(40, "Preparing terrain and waterways")
	await get_tree().process_frame
	relief_surface = Surface.new()
	_build_planet()
	_rebuild_palette()
	country_label_layer.configure(self)
	tiny_state_markers=preload("res://scripts/tiny_state_markers.gd").new()
	view_container.add_child(tiny_state_markers)
	tiny_state_markers.configure(self)
	_update_country_list()
	_show_country(state.selected_country, false)
	_focus_country(state.selected_country, false)
	_build_menu()
	_build_save_dialogs()
	_build_game_menu()
	_build_console()
	cities = JSON.parse_string(FileAccess.get_file_as_string("res://data/cities.json"))
	for city: Dictionary in cities:
		var lon := deg_to_rad(float(city["longitude"]))
		var lat := deg_to_rad(float(city["latitude"]))
		city["sphere_point"] = Vector3(cos(lat) * sin(lon), sin(lat), cos(lat) * cos(lon))
		var uv := Vector2((float(city["longitude"])+180.0)/360.0,(90.0-float(city["latitude"]))/180.0)
		city["raised_point"] = relief_surface.point_at(uv) + city["sphere_point"] * .000025
	city_point_index = preload("res://scripts/map_point_index.gd").new()
	var city_points := PackedVector3Array()
	for city: Dictionary in cities: city_points.append(city["sphere_point"])
	city_point_index.build(city_points)
	last_city_view.clear()
	urban_scenery = Urban.new()
	planet.add_child(urban_scenery)
	_loading_stage(65, "Preparing cities and landmarks")
	await get_tree().process_frame
	urban_scenery.preparation_progress.connect(func(done: int,total: int): _loading_stage(65.0+20.0*float(done)/total,"Preparing cities and landmarks"))
	await urban_scenery.initialize(relief_surface)
	places.initialize(state, cities, JSON.parse_string(FileAccess.get_file_as_string("res://data/urban_scenery.json")))
	_build_place_search()
	for tag: String in state.countries:
		var country: Dictionary = state.countries[tag]
		hover_flags[tag + ":" + str(country.get("cosmetic", "")) + ":" + str(country.get("outlook", "Unspecified"))] = flags.resolve_hover(tag, str(country.get("cosmetic", "")), str(country.get("outlook", "Unspecified")))
	_loading_stage(90, "Preparing graphics")
	screen = "selection"
	map_mode = 6
	_rebuild_palette()
	distance = 1.08
	_update_camera_pose()
	urban_scenery.update_view(camera, distance, true, .3)

	# Exercise close terrain rendering while the loading screen is visible.
	planet_material.set_shader_parameter("camera_distance", distance)
	planet_material.set_shader_parameter("terrain_mix", 1.0)
	planet_material.set_shader_parameter("city_detail", 1.0)
	for warm_frame: int in 4:
		await get_tree().process_frame
	map_mode = 0
	_rebuild_palette()
	distance = 3.65
	_update_camera_pose()
	urban_scenery.update_view(camera, distance, false, .3)

	# Restore distant settings and draw the political shader before loading ends.
	planet_material.set_shader_parameter("camera_distance", distance)
	planet_material.set_shader_parameter("terrain_mix", 0.0)
	planet_material.set_shader_parameter("city_detail", 0.0)
	for warm_frame: int in 4:
		await get_tree().process_frame

	_enter_menu()
	_update_clock()
	_loading_stage(100, "Ready")
	await get_tree().process_frame
	loading_overlay.queue_free()
	boot_complete = true
	print("BUNNY_RENDERER ", JSON.stringify(map_diagnostics.adapter()))
	set_process(true)
	_set_status("World ready  ·  %d countries  ·  %d states" % [state.countries.size(), state.regions.size()])
	for arg: String in OS.get_cmdline_user_args():
		if arg == "--smoke-test":
			smoke = true
		if arg.begins_with("--capture="):
			capture_path = arg.trim_prefix("--capture=")
		if arg.begins_with("--capture-organization="):
			var oid := arg.trim_prefix("--capture-organization=")
			if state.organizations.has(oid):
				_open_organization(oid)
		if arg.begins_with("--capture-foundation="): capture_foundation = arg.trim_prefix("--capture-foundation=")
		if arg == "--capture-selection":
			_start_selection()
		if arg == "--capture-game":
			_start_selection()
			_begin_campaign()
		if arg.begins_with("--capture-map="):
			_map_changed(int(arg.trim_prefix("--capture-map=")))
		if arg == "--capture-memberships": capture_memberships = true
		if arg == "--capture-province":
			capture_inspect = true
		if arg == "--capture-tooltip": capture_tooltip = true
		if arg.begins_with("--capture-find="): capture_find = arg.trim_prefix("--capture-find=")
		if arg.begins_with("--capture-to="): capture_to = arg.trim_prefix("--capture-to=")
		if arg == "--capture-scenery-off": _set_city_scenery(false)
		if arg.begins_with("--capture-water="): capture_water = int(arg.trim_prefix("--capture-water="))
		if arg.begins_with("--capture-state="): capture_state = int(arg.trim_prefix("--capture-state="))
		if arg.begins_with("--capture-point="):
			var pair := arg.trim_prefix("--capture-point=").split(",")
			if pair.size() == 2: capture_point = Vector2(float(pair[0]), float(pair[1]))
		if arg == "--capture-reverse": relations_reverse = true; relations_picker.select(1); _rebuild_palette()
		if arg == "--capture-menu": _open_game_menu()
		if arg.begins_with("--capture-country="): _show_country(arg.trim_prefix("--capture-country="), false); _focus_country(state.selected_country, false)
		if arg == "--capture-own": _show_country(state.player_country, false)
		if arg == "--capture-console": _toggle_console()
		if arg.begins_with("--capture-distance="):
			distance = float(arg.trim_prefix("--capture-distance="))
			_update_camera_pose()
		if arg == "--capture-small":
			DisplayServer.window_set_size(Vector2i(1100, 700))
			get_window().content_scale_size = Vector2i(1100, 700)
	if smoke:
		_run_smoke_test.call_deferred()
	elif not capture_path.is_empty():
		_capture.call_deferred()

func _panel_style(color: Color, radius: int = 12, border: Color = Color("223b4c")) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color.lerp(Color("101e27"), .28)
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(mini(radius, 4))
	style.shadow_color = Color(0.01, 0.02, 0.025, 0.34)
	style.shadow_size = 5
	style.shadow_offset = Vector2(0, 3)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 14
	style.content_margin_bottom = 14
	return style

func _button_style(color: Color, radius: int = 7, border: Color = Color("294657")) -> StyleBoxFlat:
	var style := _panel_style(color, radius, border)
	style.content_margin_left = 9
	style.content_margin_right = 9
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	return style

func _build_theme() -> void:
	var t := Theme.new()
	t.default_font_size = 15
	var tooltip_style := _panel_style(Color("101f29"), 3, Color("62706b"))
	tooltip_style.shadow_size = 4
	t.set_stylebox("panel", "TooltipPanel", tooltip_style)
	t.set_color("font_color", "TooltipLabel", Color("e9e6d8"))
	t.set_font_size("font_size", "TooltipLabel", 13)
	t.set_color("font_disabled_color", "Button", Color("71848a"))
	var rule := StyleBoxLine.new()
	rule.color = Color("35454b")
	rule.thickness = 1
	t.set_stylebox("separator", "HSeparator", rule)
	var scroll_ink := StyleBoxFlat.new()
	scroll_ink.bg_color = Color("53646a")
	scroll_ink.set_corner_radius_all(3)
	t.set_stylebox("grabber", "VScrollBar", scroll_ink)
	t.set_stylebox("grabber_highlight", "VScrollBar", scroll_ink)
	t.set_color("font_color", "Label", Color("d5e4ec"))
	t.set_color("font_color", "Button", Color("c6dce4"))
	t.set_color("font_hover_color", "Button", Color("ffffff"))
	t.set_color("font_pressed_color", "Button", Color("ffffff"))
	t.set_color("font_color", "LineEdit", Color("d5e4ec"))
	t.set_color("font_placeholder_color", "LineEdit", Color("718b9e"))
	t.set_stylebox("normal", "Button", _button_style(Color("142a3b"), 7))
	t.set_stylebox("hover", "Button", _button_style(Color("20485a"), 7, Color("4fbaaa")))
	t.set_stylebox("pressed", "Button", _button_style(Color("24594f"), 7, Color("65d4ba")))
	t.set_stylebox("focus", "Button", _panel_style(Color(0, 0, 0, 0), 7, Color("7fe1c8")))
	t.set_stylebox("normal", "LineEdit", _panel_style(Color("0a1c2d"), 7))
	t.set_stylebox("focus", "LineEdit", _panel_style(Color("0a1c2d"), 7, Color("65c8b5")))
	t.set_stylebox("panel", "ItemList", _panel_style(Color("0b1c2b"), 8))
	t.set_stylebox("selected", "ItemList", _panel_style(Color("245347"), 5, Color("42907e")))
	t.set_stylebox("selected_focus", "ItemList", _panel_style(Color("245347"), 5, Color("65c8b5")))
	t.set_color("font_color", "ItemList", Color("b7cfda"))
	t.set_color("font_selected_color", "ItemList", Color("edfff7"))
	t.set_constant("v_separation", "ItemList", 7)
	t.set_stylebox("panel", "PopupMenu", _panel_style(Color("12283a"), 7))
	t.set_stylebox("panel", "AcceptDialog", _panel_style(Color("102739"), 10))
	t.set_constant("separation", "VBoxContainer", 12)
	t.set_constant("separation", "HBoxContainer", 12)
	theme = t
	var backdrop := ColorRect.new()
	backdrop.color = Color("081421")
	backdrop.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(backdrop)

func _label(text: String, font_size: int = 15, color: Color = Color("d5e4ec")) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label

func _button(text: String, action: Callable, tip: String = "") -> Button:
	var b := Button.new()
	b.text = text
	b.clip_text = false
	b.custom_minimum_size.x = clampf(text.length() * 7 + 20, 36, 230)
	b.focus_mode = Control.FOCUS_NONE
	b.tooltip_text = tip if not tip.is_empty() else text
	b.pressed.connect(func(): _play_ui("click"))
	b.pressed.connect(action)
	b.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	return b

func _build_interface() -> void:
	var margin := Control.new()
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	game_ui = margin
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side: String in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 10)
	add_child(margin)
	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 6)
	margin.add_child(root)
	stats_row = HFlowContainer.new()
	stats_row.add_theme_constant_override("h_separation", 5)
	stats_row.add_theme_constant_override("v_separation", 4)
	root.add_child(stats_row)
	var header := HBoxContainer.new()
	header.add_theme_constant_override("separation", 8)
	header.alignment = BoxContainer.ALIGNMENT_BEGIN
	navigation_row = header
	root.add_child(header)
	var identity := VBoxContainer.new()
	identity.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	identity.add_theme_constant_override("separation", 2)
	header.add_child(identity)
	header_flag = TextureRect.new()
	header_flag.custom_minimum_size = Vector2(72, 46)
	header_flag.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	header_flag.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	header_flag.mouse_filter = Control.MOUSE_FILTER_STOP
	header_flag.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	header_flag.tooltip_text = "Open your country control panel"
	header_flag.gui_input.connect(func(event: InputEvent):
		if screen == "playing" and event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			_show_country(state.player_country, false))
	header.add_child(header_flag)
	header.move_child(header_flag, 0)
	title_label = _label("BUNNY WORLD", 26, Color("eff8f7"))
	title_label.mouse_filter = Control.MOUSE_FILTER_STOP
	title_label.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	title_label.gui_input.connect(func(event: InputEvent):
		if screen == "playing" and event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			_show_country(state.player_country, false))
	identity.add_child(title_label)
	subtitle_label = _label("WORLD FOUNDATION  /  " + build_version, 12, Color("63c9b6"))
	identity.add_child(subtitle_label)
	campaign_label = _label("Choose your country", 13, Color("e5c888"))
	identity.add_child(campaign_label)
	session_controls = HBoxContainer.new()
	header.add_child(session_controls)
	date_text = _label("", 13)
	session_controls.add_child(date_text)
	pause_button = _button("Play", _toggle_pause, "Space: pause or resume")
	pause_button.custom_minimum_size = Vector2(36, 34)
	session_controls.add_theme_constant_override("separation", 5)
	session_controls.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	session_controls.add_child(pause_button)
	speed_picker = OptionButton.new()
	for value: int in State.SPEEDS:
		speed_picker.add_item("%dx" % value)
	speed_picker.tooltip_text = "Hours per second. Keys 1–4 change speed."
	speed_picker.item_selected.connect(_speed_changed)
	session_controls.add_child(speed_picker)
	var menu_button := _button("Menu", _open_game_menu)
	menu_button.name = "SessionMenu"
	session_controls.add_child(menu_button)
	stats_label = _label("", 14)
	stats_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(stats_label)
	stats_label.hide()
	
	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(body)
	control_panel = PanelContainer.new()
	control_panel.set_script(preload("res://scripts/briefing_frame.gd"))
	control_panel.mouse_force_pass_scroll_events = false
	control_panel.custom_minimum_size.x = 310
	control_panel.add_theme_stylebox_override("panel", _panel_style(Color("102332")))
	# Own-country panel is attached over the viewport below.
	var control_scroll := ScrollContainer.new()
	control_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var control_frame := VBoxContainer.new()
	control_frame.add_theme_constant_override("separation", 8)
	control_panel.add_child(control_frame)
	control_heading = VBoxContainer.new()
	control_heading.name = "PinnedHeading"
	control_frame.add_child(control_heading)
	control_scroll.name = "CountryScroll"
	control_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	control_frame.add_child(control_scroll)
	control_details = VBoxContainer.new()
	control_details.custom_minimum_size.x = 270
	control_details.add_theme_constant_override("separation", 6)
	control_scroll.add_child(control_details)
	_hide_panel(control_panel)
	var left := VBoxContainer.new()
	country_sidebar = left
	left.custom_minimum_size.x = 240
	body.add_child(left)
	left.add_child(_label("COUNTRIES", 12, Color("63c9b6")))
	search = LineEdit.new()
	search.placeholder_text = "Find a country…"
	search.tooltip_text = "Search by country name."
	search.text_changed.connect(_search_changed)
	left.add_child(search)
	country_list = ItemList.new()
	country_list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	country_list.custom_minimum_size.x = 240
	country_list.item_selected.connect(_country_item_selected)
	left.add_child(country_list)
	left.add_child(_button("Focus country", func(): _focus_country(state.selected_country), "F: centre the globe on the selected country"))
	selection_bar = HBoxContainer.new()
	left.add_child(selection_bar)
	var play := _button("Play", _begin_campaign, "Start playing as the selected country")
	play.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	selection_bar.add_child(play)
	var middle := VBoxContainer.new()
	middle.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(middle)
	var map_bar := HBoxContainer.new()
	middle.add_child(map_bar)
	map_picker = OptionButton.new()
	map_picker.add_item("Political map")
	map_picker.add_item("Organizations")
	map_picker.add_item("Population")
	map_picker.add_item("Outlook")
	map_picker.add_item("GDP")
	map_picker.add_item("GDP per capita")
	map_picker.add_item("Physical Earth")
	map_picker.add_item("Relations")
	map_picker.item_selected.connect(_map_changed)
	map_bar.add_child(map_picker)
	relations_picker = OptionButton.new()
	relations_picker.add_item("Selected country → others")
	relations_picker.add_item("Others → selected country")
	relations_picker.item_selected.connect(func(index: int): relations_reverse = index == 1; _rebuild_palette())
	relations_picker.hide()
	map_picker.get_parent().add_child(relations_picker)
	org_picker = OptionButton.new()
	for oid: String in state.organizations:
		org_ids.append(oid)
		org_picker.add_item(oid)
	org_picker.select(org_ids.find(active_org))
	org_picker.item_selected.connect(_organization_changed)
	org_picker.visible = false
	map_bar.add_child(org_picker)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	map_bar.add_child(spacer)
	var find_button := _icon_button("Find a city, state, country or landmark · Ctrl+F", load("res://assets/ui/search.svg"), _open_place_search, Vector2(36, 32))
	find_button.name = "FindPlace"
	country_labels_button = _button("Aa", _toggle_country_labels, "Show or hide country names on the map")
	country_labels_button.name = "CountryLabelsToggle"
	country_labels_button.toggle_mode = true
	country_labels_button.button_pressed = country_labels_enabled
	country_labels_button.custom_minimum_size = Vector2(34, 32)
	map_bar.add_child(country_labels_button)
	map_bar.add_child(find_button)
	view_container = SubViewportContainer.new()
	view_container.stretch = true
	view_container.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	view_container.size_flags_vertical = Control.SIZE_EXPAND_FILL
	view_container.custom_minimum_size = Vector2(350, 400)
	view_container.mouse_filter = Control.MOUSE_FILTER_STOP
	view_container.gui_input.connect(_globe_input)
	middle.add_child(view_container)
	world_view = SubViewport.new()
	world_view.size = Vector2i(700, 690)
	world_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	world_view.handle_input_locally = false
	world_view.msaa_3d = [Viewport.MSAA_2X, Viewport.MSAA_DISABLED, Viewport.MSAA_4X][graphics_setting]
	view_container.add_child(world_view)
	country_label_layer = Control.new()
	country_label_layer.name = "CountryNames"
	country_label_layer.set_script(preload("res://scripts/country_labels.gd"))
	country_label_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	country_label_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view_container.add_child(country_label_layer)
	city_layer = Control.new()
	city_layer.set_script(load("res://scripts/city_overlay.gd"))
	city_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	city_layer.clip_contents = true
	city_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view_container.add_child(city_layer)
	hover_panel = PanelContainer.new()
	hover_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hover_panel.add_theme_stylebox_override("panel", _button_style(Color("102333"), 7, Color("456377")))
	hover_text = _label("", 14, Color("edf5f5"))
	hover_text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var hover_row := HBoxContainer.new()
	hover_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hover_row.add_theme_constant_override("separation", 8)
	hover_flag = TextureRect.new()
	hover_flag.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hover_flag.custom_minimum_size = Vector2(30, 20)
	hover_flag.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	hover_flag.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	hover_flag.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	hover_flag.hide()
	hover_row.add_child(hover_flag)
	hover_row.add_child(hover_text)
	hover_panel.add_child(hover_row)
	add_child(hover_panel)
	hover_panel.hide()
	view_container.mouse_exited.connect(func(): hover_panel.hide())
	legend = _label("", 12, Color("b7cfda"))
	legend.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	view_container.add_child(legend)
	legend.mouse_filter = Control.MOUSE_FILTER_IGNORE
	legend.position = Vector2(12, 8)
	legend.custom_minimum_size.x = 300
	legend.add_theme_color_override("font_outline_color", Color("081421"))
	legend.add_theme_constant_override("outline_size", 4)
	right_panel = PanelContainer.new()
	right_panel.set_script(preload("res://scripts/briefing_frame.gd"))
	right_panel.mouse_force_pass_scroll_events = false
	right_panel.custom_minimum_size.x = 310
	right_panel.add_theme_stylebox_override("panel", _panel_style(Color("102332")))
	view_container.add_child(right_panel)
	view_container.add_child(control_panel)
	territory_panel = PanelContainer.new()
	territory_panel.set_script(preload("res://scripts/briefing_frame.gd"))
	territory_panel.mouse_force_pass_scroll_events = false
	territory_panel.name = "TerritoryDrawer"
	territory_panel.clip_contents = true
	territory_panel.add_theme_stylebox_override("panel", _button_style(Color("102332")))
	territory_clip = Control.new()
	territory_clip.name = "TerritoryClip"
	territory_clip.clip_contents = true
	territory_clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	view_container.add_child(territory_clip)
	view_container.move_child(territory_clip, right_panel.get_index())
	territory_clip.add_child(territory_panel)
	territory_handle = _button("‹", _toggle_territory, "Collapse State / province information")
	territory_handle.name = "TerritoryHandle"
	territory_handle.custom_minimum_size = Vector2(26, 36)
	view_container.add_child(territory_handle)
	territory_handle.hide()
	var territory_frame := VBoxContainer.new()
	territory_frame.add_theme_constant_override("separation", 5)
	territory_panel.add_child(territory_frame)
	territory_heading = VBoxContainer.new()
	territory_heading.name = "TerritoryHeading"
	territory_heading.add_theme_constant_override("separation", 5)
	territory_frame.add_child(territory_heading)
	territory_details = VBoxContainer.new()
	territory_details.custom_minimum_size.x = 270
	territory_details.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	territory_details.add_theme_constant_override("separation", 5)
	territory_scroll = ScrollContainer.new()
	territory_scroll.name = "TerritoryScroll"
	territory_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	territory_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	territory_scroll.mouse_force_pass_scroll_events = false
	territory_frame.add_child(territory_scroll)
	territory_scroll.add_child(territory_details)
	territory_panel.hide()
	_position_panels()
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var diplomacy_frame := VBoxContainer.new()
	diplomacy_frame.add_theme_constant_override("separation", 8)
	right_panel.add_child(diplomacy_frame)
	diplomatic_heading = VBoxContainer.new()
	diplomatic_heading.name = "PinnedHeading"
	diplomacy_frame.add_child(diplomatic_heading)
	scroll.name = "CountryScroll"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	diplomacy_frame.add_child(scroll)
	details = VBoxContainer.new()
	details.custom_minimum_size.x = 270
	details.add_theme_constant_override("separation", 6)
	details.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(details)
	diplomatic_details = details
	status = _label("", 12, Color("8da6b7"))
	status.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(status)
	status.hide()
	info_dialog = AcceptDialog.new()
	info_dialog.title = "Bunny World"
	add_child(info_dialog)

func _build_planet() -> void:
	var environment_node := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_SKY
	var sky_shader := Shader.new()
	sky_shader.code = "shader_type sky; float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);} void sky(){vec2 p=SKY_COORDS*vec2(1200.0,600.0);vec2 cell=floor(p);float seed=hash(cell);vec2 delta=fract(p)-vec2(0.5);float star=step(0.997,seed)*(1.0-smoothstep(0.02,0.16,length(delta))); COLOR=vec3(0.006,0.012,0.025)+vec3(0.65,0.72,0.85)*star;}"
	var sky_material := ShaderMaterial.new()
	sky_material.shader = sky_shader
	var sky := Sky.new()
	sky.radiance_size = Sky.RADIANCE_SIZE_32
	sky.sky_material = sky_material
	environment.sky = sky
	environment.background_color = Color("081421")
	environment_node.environment = environment
	world_view.add_child(environment_node)
	camera = Camera3D.new()
	_update_camera_pose()
	camera.fov = 40
	camera.near = 0.001
	camera.far = 20
	world_view.add_child(camera)
	planet = Node3D.new()
	planet.rotation_order = EULER_ORDER_XYZ
	world_view.add_child(planet)
	var mesh := MeshInstance3D.new()
	mesh.mesh = _sphere_mesh(384, 192)
	mesh.custom_aabb = mesh.mesh.get_aabb().grow(.025)
	mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	planet.add_child(mesh)
	planet_material = ShaderMaterial.new()
	political_shader = load("res://scripts/clean_globe.gdshader")
	physical_shader = load("res://scripts/clean_globe_physical.gdshader")
	planet_material.shader = physical_shader if map_mode == 6 else political_shader
	map_rendering=preload("res://scripts/map_rendering.gd").new()
	map_rendering.initialize(state.provinces,state.regions,state.countries)
	map_rendering.visual_changed.connect(map_frame_policy.invalidate)
	region_images=map_rendering.region_images
	planet_material.set_shader_parameter("map_resolution",Vector2(region_images[0].get_size()))
	for tile: int in map_rendering.region_textures.size():
		planet_material.set_shader_parameter("region_map_%d"%tile,map_rendering.region_textures[tile])
	planet_material.set_shader_parameter("palette_width", 8192.0)
	planet_material.set_shader_parameter("province_index",map_rendering.province_texture)
	planet_material.set_shader_parameter("relief_data", load("res://assets/relief_data.png"))
	water_passages = JSON.parse_string(FileAccess.get_file_as_string("res://data/waterways.json"))["passages"]
	resident_terrain = preload("res://scripts/resident_terrain.gd").new()
	resident_terrain.initialize(planet_material, graphics_setting == 1)
	terrain_shading = preload("res://scripts/terrain_shading.gd").new()
	terrain_shading.initialize(planet_material)
	display_coverage = preload("res://scripts/display_coverage.gd").new()
	display_coverage.initialize(planet_material, false)
	mesh.material_override = planet_material
	spatial_map_layers = preload("res://scripts/spatial_map_layers.gd").new()
	spatial_map_layers.initialize(str(state.database["version"]))
	# Clean globe uses unified single sphere mesh (1 draw call). Spatial map layers handles borders only.
	# CPU selection keeps exact sea IDs. The GPU only needs ocean coverage,
	# avoiding an otherwise unused full RGB sea-ID texture in steady state.
	sea_image = Image.new()
	if FileAccess.file_exists("res://assets/sea_ids.png"):
		var sea_error := sea_image.load_png_from_buffer(FileAccess.get_file_as_bytes("res://assets/sea_ids.png"))
		assert(sea_error == OK, "Sea selection IDs could not be decoded")
	else:
		sea_image = load("res://assets/sea_ids.png").get_image()
	if sea_image.is_compressed(): sea_image.decompress()
	planet_material.set_shader_parameter("sea_map", map_rendering.create_sea_mask_texture())
	planet_material.set_shader_parameter("urban_density", load("res://assets/urban_density.png"))
	planet_material.set_shader_parameter("urban_material", load("res://assets/materials/urban.png"))
	planet_material.set_shader_parameter("urban_grid_material", load("res://assets/materials/urban_grid.png"))
	planet_material.set_shader_parameter("urban_asian_material", load("res://assets/materials/urban_asian.png"))
	planet_material.set_shader_parameter("water_normal", load("res://assets/water_normal.png"))
	planet_material.set_shader_parameter("rock_detail", load("res://assets/materials/rock_detail.png"))
	planet_material.set_shader_parameter("farmland_detail", load("res://assets/materials/resident_2.png"))
	planet_material.set_shader_parameter("rice_paddy_detail", load("res://assets/materials/rice_paddy.png"))
	planet_material.set_shader_parameter("swamp_detail", load("res://assets/materials/swamp.png"))
	planet_material.set_shader_parameter("tundra_detail", load("res://assets/materials/tundra.png"))
	planet_material.set_shader_parameter("savanna_detail", load("res://assets/materials/savanna.png"))
	planet_material.set_shader_parameter("chaparral_detail", load("res://assets/materials/chaparral.png"))
	planet_material.set_shader_parameter("badlands_detail", load("res://assets/materials/badlands.png"))
	planet_material.set_shader_parameter("conifer_detail", load("res://assets/materials/conifer_forest.png"))
	planet_material.set_shader_parameter("rainforest_detail", load("res://assets/materials/rainforest.png"))
	planet_material.set_shader_parameter("alluvium_detail", load("res://assets/materials/alluvium.png"))
	planet_material.set_shader_parameter("mediterranean_detail", load("res://assets/materials/mediterranean.png"))
	planet_material.set_shader_parameter("city_growth", 1.0)
	for kind: String in ["land", "sea", "province"]:
		var border_mesh := MeshInstance3D.new()
		# Material holder only: prepared spatial batches own the geometry.
		var material := ShaderMaterial.new()
		material.shader = load("res://scripts/provinces.gdshader" if kind == "province" else "res://scripts/boundaries.gdshader")
		if kind == "province": material.set_shader_parameter("province_index",map_rendering.province_texture)
		for tile: int in map_rendering.region_textures.size(): material.set_shader_parameter("region_map_%d" % tile,map_rendering.region_textures[tile])
		material.set_shader_parameter("relief_data", load("res://assets/relief_data.png"))
		material.set_shader_parameter("camera_distance", distance)
		border_mesh.material_override = material
		border_materials.append(material)
		planet.add_child(border_mesh)
		border_meshes[kind] = border_mesh
		spatial_map_layers.register(kind,border_mesh,planet)
	_update_border_visibility()
	var waterways := MeshInstance3D.new()
	# Do not keep a second whole-world river mesh beside the spatial batches.
	var water_material := ShaderMaterial.new()
	waterways_material = water_material
	water_material.shader = load("res://scripts/waterways.gdshader")
	water_material.set_shader_parameter("relief_data",load("res://assets/relief_data.png"))
	waterways.material_override = water_material
	planet.add_child(waterways)
	spatial_map_layers.register("water",waterways,planet)
	# A very thin rim makes the sphere readable without terrain or models.
	var rim := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 1.028
	sphere.height = 2.056
	sphere.radial_segments = 128
	sphere.rings = 64
	rim.mesh = sphere
	var rim_shader: Shader = load("res://scripts/atmosphere.gdshader")
	var rim_material := ShaderMaterial.new()
	rim_material.shader = rim_shader
	rim.material_override = rim_material
	planet.add_child(rim)

func _sphere_mesh(segments: int, rings: int) -> ArrayMesh:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	for y: int in range(rings + 1):
		var v := float(y) / rings
		var latitude := PI / 2.0 - v * PI
		for x: int in range(segments + 1):
			var u := float(x) / segments
			var longitude := (u - 0.5) * TAU
			var p := Vector3(cos(latitude) * sin(longitude), sin(latitude), cos(latitude) * cos(longitude))
			vertices.append(p)
			normals.append(p)
			uvs.append(Vector2(u, v))
	for y: int in range(rings):
		for x: int in range(segments):
			var a := y * (segments + 1) + x
			var b := a + segments + 1
			indices.append_array(PackedInt32Array([a, a + 1, b, a + 1, b + 1, b]))
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh

func _rebuild_palette() -> void:
	last_surface_view.clear()
	last_hover_view.clear()
	_select_planet_shader()
	map_frame_policy.invalidate()
	if map_rendering != null: map_rendering.update_ownership(state.provinces,state.regions,state.countries)
	if country_label_layer != null and country_label_layer.preparation_runs>0: country_label_layer.refresh_if_changed()
	var color_image := Image.create(8192, 1, false, Image.FORMAT_RGBA8)
	var owner_image := Image.create(8192, 1, false, Image.FORMAT_RGBA8)
	color_image.fill(OCEAN)
	color_image.set_pixel(8191, 0, Color("d5e5eb"))
	owner_image.fill(Color(0, 0, 0, 1))
	var national_gdp: Dictionary = {}
	var max_gdp := 1.0
	var max_gdpc := 1.0
	var populations: Dictionary = {}
	for entry: Dictionary in state.regions.values():
		populations[entry["owner"]] = int(populations.get(entry["owner"], 0)) + int(entry["population"])
	for tag: String in state.countries:
		var per_capita := float(state.countries[tag].get("starting_stats", {}).get("gdp_per_capita_usd", 0))
		max_gdpc = maxf(max_gdpc, per_capita)
		national_gdp[tag] = per_capita * float(populations.get(tag, 0))
		max_gdp = maxf(max_gdp, national_gdp[tag])
	var max_population := 1.0
	for entry: Dictionary in state.regions.values():
		max_population = maxf(max_population, float(entry["population"]))
	for sid: String in state.regions:
		var region: Dictionary = state.regions[sid]
		var tag: String = region["owner"]
		var rgb := Color("556b78")
		var index: int = 0
		if state.countries.has(tag):
			var c: Dictionary = state.countries[tag]
			index = int(c["index"])
			var colors: Array = state.country_color(tag)
			rgb = Color(float(colors[0]) / 255.0, float(colors[1]) / 255.0, float(colors[2]) / 255.0)
			if map_mode == 1:
				rgb = Color("4ecab1") if tag in state.organizations[active_org]["members"] else Color("273f50")
		if map_mode == 2:
			var weight := log(1.0 + float(region["population"])) / log(1.0 + max_population)
			rgb = Color("1b354c").lerp(Color("ffd36b"), pow(weight, 4.0))
		elif map_mode == 3:
			rgb = OUTLOOK_COLORS.get(state.countries.get(tag, {}).get("outlook", "Unspecified"), Color("718793"))
		elif map_mode in [4, 5]:
			var value := float(national_gdp.get(tag, 0)) if map_mode == 4 else float(state.countries.get(tag, {}).get("starting_stats", {}).get("gdp_per_capita_usd", 0))
			rgb = MapPalette.economic(value, map_mode == 5)
		elif map_mode == 7:
			var score := state.opinion(tag, state.selected_country) if relations_reverse else state.opinion(state.selected_country, tag)
			rgb = MapPalette.relation(score)
			if tag == state.selected_country: rgb = Color("dfeff9")
		color_image.set_pixel(int(sid), 0, rgb)
		owner_image.set_pixel(int(sid), 0, Color(float(index & 255) / 255.0, float(index >> 8) / 255.0, 0, 1))
	if palette_texture == null:
		palette_texture = ImageTexture.create_from_image(color_image)
		owners_texture = ImageTexture.create_from_image(owner_image)
	else:
		palette_texture.update(color_image)
		owners_texture.update(owner_image)
	planet_material.set_shader_parameter("colors", palette_texture)
	planet_material.set_shader_parameter("owners", owners_texture)
	for material: ShaderMaterial in border_materials:
		material.set_shader_parameter("owners", owners_texture)
		material.set_shader_parameter("colors", palette_texture)
		material.set_shader_parameter("palette_width", 8192.0)
		material.set_shader_parameter("physical_mode", map_mode == 6)
	planet_material.set_shader_parameter("show_regions", show_regions)
	planet_material.set_shader_parameter("border_width", 1.15 if map_mode == 0 else 0.7)
	planet_material.set_shader_parameter("physical_mode", map_mode == 6)
	planet_material.set_shader_parameter("information_mode", map_mode in [1,2,3,4,5,7])
	_update_selection_shader()
	_update_legend()

func _update_selection_shader() -> void:
	map_frame_policy.invalidate()
	var previewing := state_preview > 0 and state.regions.has(str(state_preview))
	var active := inspection_active or previewing
	var region_id := state_preview if previewing else state.selected_region
	var province_id := 0 if previewing else state.selected_province
	var sea_id := 0 if previewing else state.selected_sea
	var tag: String = state.regions[str(region_id)]["owner"] if previewing else state.selected_country
	if display_coverage != null: display_coverage.select(region_id if active else 0, province_id if active else 0, sea_id)
	planet_material.set_shader_parameter("selected_sea", float(sea_id))
	for material: ShaderMaterial in border_materials:
		material.set_shader_parameter("selected_country", float(state.countries[tag]["index"]) if active else 0.0)
		material.set_shader_parameter("inspection_active", active)
		material.set_shader_parameter("selected_region", float(region_id))
		material.set_shader_parameter("selected_sea", float(sea_id))
		material.set_shader_parameter("selected_province", float(province_id))
	planet_material.set_shader_parameter("selected_country", float(state.countries[tag]["index"]) if active else 0.0)
	planet_material.set_shader_parameter("inspection_active", active)
	planet_material.set_shader_parameter("selected_region", float(region_id))
	planet_material.set_shader_parameter("selected_province", float(province_id))
	_update_border_visibility()

func _preview_state(id: int) -> void:
	if id == state_preview: return
	state_preview = id if state.regions.has(str(id)) else 0
	_update_selection_shader()

func _update_border_visibility() -> void:
	if border_meshes.is_empty(): return
	# Match the existing shader's exact zero-opacity ranges. Visibility changes
	# submit no geometry and never generate or load new meshes on camera travel.
	spatial_map_layers.set_enabled("land", distance < 4.5)
	spatial_map_layers.set_enabled("province", distance < 1.35 or state.selected_region > 0 or state_preview > 0)
	spatial_map_layers.set_enabled("sea", distance < 2.8 or state.selected_sea > 0)
	spatial_map_layers.set_enabled("water", distance < 3.5)
	spatial_map_layers.update_view(distance)
	spatial_map_layers.cull(camera, planet)

func _search_changed(value: String) -> void:
	list_filter = value.strip_edges().to_lower()
	_update_country_list()

func _update_country_list() -> void:
	country_list.clear()
	country_tags.clear()
	var sorted_tags: Array = state.countries.keys()
	sorted_tags.sort_custom(func(a: String, b: String): return state.countries[a]["name"].naturalnocasecmp_to(state.countries[b]["name"]) < 0)
	for tag: String in sorted_tags:
		var c: Dictionary = state.countries[tag]
		if not list_filter.is_empty() and list_filter not in (str(c["name"]) + " " + tag).to_lower():
			continue
		var i := country_list.add_item(c["name"])
		country_list.set_item_tooltip(i, c["name"])
		country_tags.append(tag)
		if tag == state.selected_country:
			country_list.select(i)

func _country_item_selected(index: int) -> void:
	if index >= 0 and index < country_tags.size():
		_show_country(country_tags[index], true)

func _clear_details() -> void:
	active_feature = ""
	var pinned: VBoxContainer = control_heading if details == control_details else diplomatic_heading
	if pinned != null:
		for child: Node in pinned.get_children(): pinned.remove_child(child); child.queue_free()
	opinion_labels.clear()
	for child: Node in details.get_children():
		details.remove_child(child)
		child.queue_free()
	if foundation != null: foundation.refresh_active_section()

func _wrapped(text: String, size: int = 14, color: Color = Color("96b1be")) -> Label:
	var label := _label(text, size, color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.custom_minimum_size.x = 270 if details == territory_details else 265
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return label

func _stat(caption: String, value: String) -> void:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 3)
	box.add_child(_label(caption.to_upper(), 11, Color("7797a9")))
	box.add_child(_wrapped(value, 19, Color("deedf3")))
	details.add_child(box)

func _number(value: int) -> String:
	var raw := str(value)
	var formatted: String = ""
	for i: int in raw.length():
		if i > 0 and (raw.length() - i) % 3 == 0:
			formatted += ","
		formatted += raw[i]
	return formatted

func _organization_texture(oid: String, compact: bool = false) -> Texture2D:
	var key := oid + (":compact" if compact else "")
	if compact:
		if not organization_textures.has(key):
			var original := _organization_texture(oid)
			var crop: Array = state.organizations[oid].get("compact_icon_region", [])
			if original != null and crop.size() == 4 and not organization_textures.get(oid + ":external", false):
				var emblem := AtlasTexture.new()
				emblem.atlas = original
				emblem.region = Rect2(crop[0], crop[1], crop[2], crop[3])
				emblem.filter_clip = true
				organization_textures[key] = emblem
			else:
				organization_textures[key] = original
		return organization_textures[key]
	if not organization_textures.has(oid):
		var folder := OS.get_executable_path().get_base_dir().path_join("organization_logos")
		for extension: String in ["png", "webp", "jpg"]:
			var external := folder.path_join(oid + "." + extension)
			if FileAccess.file_exists(external):
				var imported := Image.load_from_file(external)
				if imported != null and not imported.is_empty():
					imported.generate_mipmaps()
					organization_textures[oid + ":external"] = true
					organization_textures[oid] = ImageTexture.create_from_image(imported)
					return organization_textures[oid]
		var path: String = state.organizations[oid].get("logo", "")
		organization_textures[oid] = load(path) if ResourceLoader.exists(path) else null
	return organization_textures[oid]

func _rights_row(caption: String, tags: Array) -> void:
	details.add_child(_label(caption, 11, Color("8fb6c3")))
	if tags.is_empty():
		details.add_child(_wrapped("None", 13))
		return
	var grid := _icon_grid(4 if details == territory_details else 6)
	var ordered: Array = tags.duplicate()
	ordered.sort_custom(func(a: String, b: String): return str(state.country_record(a).get("name", a)).naturalnocasecmp_to(str(state.country_record(b).get("name", b))) < 0)
	for tag: String in ordered:
		var c := state.country_record(tag)
		grid.add_child(_icon_button(str(c.get("name", tag)), flags.resolve(tag, str(c.get("cosmetic", "")), str(c.get("outlook", "Unspecified"))), func(): _show_rights_country(tag)))

func _show_rights_country(tag: String) -> void:
	if state.countries.has(tag):
		_show_country(tag, true)
		return
	var c := state.country_record(tag)
	_hide_panel(control_panel)
	_reveal_panel(right_panel)
	details = diplomatic_details
	_clear_details()
	_entity_heading(str(c.get("name", tag)), flags.resolve(tag, str(c.get("cosmetic", "")), str(c.get("outlook", "Unspecified"))))
	details.add_child(_wrapped("No controlled territory.", 15))
	var values: Dictionary = c.get("starting_stats", {})
	_stat("Stability", "%.0f%%" % (float(values.get("stability", .65)) * 100))
	_stat("War support", "%.0f%%" % (float(values.get("war_support", .5)) * 100))
	_stat("Core states", str(state.regions.values().filter(func(r: Dictionary): return tag in r.get("cores", [])).size()))
	_stat("Claimed states", str(state.regions.values().filter(func(r: Dictionary): return tag in r.get("claims", [])).size()))

func _sea_at(position: Vector2) -> int:
	if sea_image == null or _region_at(position) != 0: return 0
	var uv := _uv_at(position)
	if uv.x < 0.0: return 0
	var passage := _water_passage_at(uv)
	if passage>0: return passage
	var pixel := sea_image.get_pixel(clampi(int(uv.x * sea_image.get_width()), 0, sea_image.get_width()-1), clampi(int(uv.y * sea_image.get_height()), 0, sea_image.get_height()-1))
	var id := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	if not state.sea_regions.has(str(id)): return 0
	var sea_data: Dictionary = state.sea_regions[str(id)]
	if sea_data.get("is_inland_water", false) or sea_data.get("name", "").begins_with("Inland Water"):
		return 0
	return id

func _show_sea(id: int) -> void:
	if not state.sea_regions.has(str(id)): return
	var sea_data: Dictionary = state.sea_regions[str(id)]
	if sea_data.get("is_inland_water", false) or sea_data.get("name", "").begins_with("Inland Water"):
		return
	state.selected_sea=id;state.selected_region=0;state.selected_province=0;inspect_region=0;inspect_province=0;inspection_active=false
	preload("res://scripts/territory_view.gd").new().sea(self,id)
	_update_selection_shader()

func _update_map_hover(position: Vector2) -> void:
	hover_queries += 1
	if dragging or screen == "menu":
		hover_panel.hide(); hover_owner = 0.0; return
	var id := _region_at(position)
	var text := ""
	var hover_tag := ""
	if state.regions.has(str(id)):
		var region: Dictionary = state.regions[str(id)]
		var tag: String = region["owner"]
		hover_tag = tag
		text = str(state.countries.get(tag, {}).get("name", "Unclaimed"))
		if screen == "playing" and show_regions: text += "\nState: " + str(region["name"])
		if map_mode == 7:
			var score := state.opinion(tag, state.selected_country) if relations_reverse else state.opinion(state.selected_country, tag)
			text += "\nOpinion: %+.0f" % score
		elif map_mode == 2: text += "\nState residents: " + _number(int(region["population"]))
		elif map_mode in [4, 5]:
			var per_capita := float(state.countries[tag].get("starting_stats", {}).get("gdp_per_capita_usd", 0))
			text += "\nGDP/person: $" + _number(int(per_capita)) if map_mode == 5 else "\nGDP: $%.1f billion" % (per_capita * float(state.country_metrics(tag)["population"]) / 1e9)
		if screen == "playing" and distance <= 1.2:
			var pid := _province_at(position)
			if pid > 0:
				var p: Dictionary = state.provinces[str(pid)]
				text += "\n" + str(p.get("name", "Province %d" % int(p["local_index"])))
	elif id == 8191: text = "Antarctica\nUnclaimed terrain"
	elif id == 0:
		var sea := _sea_at(position)
		if sea > 0: text = str(state.sea_regions[str(sea)]["name"]) + "\nSea region"
	hover_owner = float(state.countries[hover_tag]["index"]) if not hover_tag.is_empty() else 0.0
	if text.is_empty():
		hover_panel.hide(); return
	var flag_key := ""
	if not hover_tag.is_empty():
		var country: Dictionary = state.countries[hover_tag]
		flag_key = hover_tag + ":" + str(country.get("cosmetic", "")) + ":" + str(country.get("outlook", "Unspecified"))
		if not hover_flags.has(flag_key): hover_flags[flag_key] = flags.resolve_hover(hover_tag,str(country.get("cosmetic", "")),str(country.get("outlook", "Unspecified")))
	if hover_country != flag_key:
		hover_country = flag_key
		hover_flag.texture = hover_flags.get(flag_key)
		hover_flag.visible = hover_flag.texture != null
	hover_text.text = text
	hover_text.autowrap_mode = TextServer.AUTOWRAP_OFF
	hover_text.custom_minimum_size.x = 0
	# Measure each current tooltip so a shorter country name shrinks immediately.
	var widest := 0.0
	var font := hover_text.get_theme_font("font")
	for line: String in text.split("\n"):
		widest = maxf(widest, font.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x)
	if widest > 280:
		hover_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		hover_text.custom_minimum_size.x = 280
	hover_panel.reset_size()
	hover_panel.show()
	_position_map_hover()

func _position_map_hover() -> void:
	var mouse := get_global_mouse_position()
	# Check visible panel bounds directly as well as the hovered control. Native
	# pointer events can reach the viewport before its GUI hover target updates.
	for panel: Control in [control_panel, right_panel, territory_clip, territory_handle, top_left_box, clock_box, map_box, selection_box]:
		if panel != null and panel.is_visible_in_tree() and not (panel == territory_clip and territory_collapsed) and panel.get_global_rect().has_point(mouse):
			hover_panel.hide()
			return
	var hovered := get_viewport().gui_get_hovered_control()
	# Country panels are children of the globe container, but still cover the map.
	if hovered != null and hovered != view_container:
		hover_panel.hide(); return
	var desired := mouse + Vector2(20, 22)
	if desired.x + hover_panel.size.x > size.x - 8: desired.x = mouse.x - hover_panel.size.x - 18
	if desired.y + hover_panel.size.y > size.y - 8: desired.y = mouse.y - hover_panel.size.y - 18
	hover_panel.position = desired.clamp(Vector2(8, 8), (size - hover_panel.size - Vector2(8, 8)).max(Vector2(8, 8)))

func _build_sounds() -> void:
	sound_player = AudioStreamPlayer.new()
	sound_player.volume_db = -19.0
	add_child(sound_player)
	for id: String in ["click", "select", "confirm", "error", "open"]:
		sound_streams[id] = load("res://assets/sounds/" + id + ".wav")
	if FileAccess.file_exists("user://interface_settings.json"):
		var saved: Variant = JSON.parse_string(FileAccess.get_file_as_string("user://interface_settings.json"))
		if saved is Dictionary:
			sound_enabled = bool(saved.get("sounds", true))
			city_scenery_enabled = bool(saved.get("city_scenery", true))
			graphics_setting = clampi(int(saved.get("graphics", 0)), 0, 2)
			frame_setting = clampi(int(saved.get("frame_limit", 0)), 0, 1)
			country_labels_enabled = bool(saved.get("country_labels", true))
	Engine.max_fps = 60 if frame_setting == 0 else 30

func _play_ui(id: String) -> void:
	if not sound_enabled or sound_player == null or not sound_streams.has(id): return
	sound_player.stream = sound_streams[id]
	sound_player.play()

func _save_sound_setting(value: bool) -> void:
	sound_enabled = value
	_persist_interface_settings()

func _persist_interface_settings() -> void:
	var file := FileAccess.open("user://interface_settings.json", FileAccess.WRITE)
	if file != null: file.store_string(JSON.stringify({"sounds":sound_enabled,"city_scenery":city_scenery_enabled,"graphics":graphics_setting,"frame_limit":frame_setting,"country_labels":country_labels_enabled}))

func _set_city_scenery(value: bool) -> void:
	city_scenery_enabled = value
	if scenery_toggle != null and scenery_toggle.button_pressed != value: scenery_toggle.set_pressed_no_signal(value)
	if urban_scenery != null: urban_scenery.update_view(camera, distance, value and screen != "menu", .3)
	_update_cities()
	_persist_interface_settings()


func _icon_grid(columns: int = 6) -> GridContainer:
	var grid := GridContainer.new()
	grid.columns = columns
	grid.add_theme_constant_override("h_separation", 4)
	grid.add_theme_constant_override("v_separation", 5)
	details.add_child(grid)
	return grid

func _organization_light_background(oid: String) -> bool:
	var path: String = state.organizations[oid].get("logo", "")
	return "/supplied/" in path and path.ends_with(".svg")

func _icon_button(caption: String, texture: Texture2D, action: Callable, icon_size: Vector2 = Vector2(43, 36), light_background: bool = false) -> Button:
	var button := Button.new()
	button.custom_minimum_size = icon_size
	button.tooltip_text = caption
	button.pressed.connect(func(): _play_ui("select"))
	button.pressed.connect(action)
	if texture != null:
		var image := TextureRect.new()
		image.texture = texture
		image.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		image.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var image_parent: Control = button
		if light_background:
			var plate := PanelContainer.new()
			plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
			var plate_style := StyleBoxFlat.new()
			plate_style.bg_color = Color("e5eae7")
			plate_style.set_corner_radius_all(2)
			plate.add_theme_stylebox_override("panel", plate_style)
			button.add_child(plate)
			plate.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			plate.offset_left=5; plate.offset_right=-5; plate.offset_top=5; plate.offset_bottom=-5
			image_parent = plate
		image_parent.add_child(image)
		image.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		image.offset_left = 3
		image.offset_right = -3
		image.offset_top = 3
		image.offset_bottom = -3
	else: button.text = "◇"
	return button

func _opinion_stat(from_tag: String, toward_tag: String) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 5)
	for tag: String in [from_tag, toward_tag]:
		if tag == toward_tag:
			row.add_child(_label("opinion of", 11))
		var country: Dictionary = state.countries[tag]
		var flag := TextureRect.new()
		flag.texture = flags.resolve(tag, str(country.get("cosmetic", "")), country["outlook"])
		flag.custom_minimum_size = Vector2(30, 20)
		flag.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		flag.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		flag.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
		flag.mouse_filter = Control.MOUSE_FILTER_STOP
		flag.tooltip_text = country["name"]
		row.add_child(flag)
	var label := _label("", 14)
	label.custom_minimum_size.x = 34
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	label.mouse_filter = Control.MOUSE_FILTER_STOP
	label.set_meta("from", from_tag)
	label.set_meta("toward", toward_tag)
	opinion_labels.append(label)
	row.add_child(label)
	details.add_child(row)
	_refresh_opinions()

func _refresh_opinions() -> void:
	var valid: Array[Label] = []
	for label: Label in opinion_labels:
		if not is_instance_valid(label) or label.is_queued_for_deletion(): continue
		valid.append(label)
		var from_tag: String = label.get_meta("from")
		var toward_tag: String = label.get_meta("toward")
		var value := state.opinion(from_tag, toward_tag)
		label.text = "%+.0f" % value
		label.modulate = Color.WHITE
		label.add_theme_color_override("font_color", Color("70d2a4") if value > 0 else (Color("f0808d") if value < 0 else Color("f6d94d")))
		var reasons: Array[String] = []
		for entry: Dictionary in state.opinion_breakdown(from_tag, toward_tag): reasons.append("%s: %+.1f" % [entry["name"], entry["value"]])
		var relationship := "%s's opinion of %s" % [state.countries[from_tag]["name"], state.countries[toward_tag]["name"]]
		label.tooltip_text = relationship + "\n" + ("\n".join(reasons) if not reasons.is_empty() else "No diplomatic opinion modifiers. Neutral: 0.")
	opinion_labels = valid

func _toggle_country_labels() -> void:
	country_labels_enabled = not country_labels_enabled
	country_labels_button.set_pressed_no_signal(country_labels_enabled)
	country_label_layer.last_view = ""
	country_label_layer.update_view()
	_persist_interface_settings()

func _briefing_section(caption: String) -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 9)
	row.add_child(_label(caption.to_upper(), 11, Color("b5a680")))
	var rule := HSeparator.new()
	rule.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	rule.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(rule)
	details.add_child(row)

func _summary_grid(rows: Array) -> void:
	var grid := GridContainer.new()
	grid.name = "CountrySummary"
	grid.columns = 3
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_theme_constant_override("h_separation", 4)
	grid.add_theme_constant_override("v_separation", 4)
	for row: Array in rows:
		var cell := PanelContainer.new()
		cell.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		cell.mouse_force_pass_scroll_events = false
		var style := _button_style(Color("0c1922"), 3, Color("2b3d44"))
		style.shadow_size = 0
		style.content_margin_left = 5; style.content_margin_right = 5
		style.content_margin_top = 4; style.content_margin_bottom = 4
		cell.add_theme_stylebox_override("panel", style)
		var box := VBoxContainer.new()
		box.add_theme_constant_override("separation", 2)
		cell.add_child(box)
		var caption := _label(str(row[0]).to_upper(), 9, Color("8fa5aa"))
		caption.clip_text = true
		box.add_child(caption)
		var value := _label(str(row[1]), 14, Color("e9e6d7"))
		value.clip_text = true
		box.add_child(value)
		cell.tooltip_text = str(row[2]) if row.size()>2 else str(row[0])+": "+str(row[1])
		grid.add_child(cell)
	details.add_child(grid)

func _population_profile(chart: Control, state_scope: bool) -> void:
	var expanded: bool = territory_profile_expanded if state_scope else national_profile_expanded
	var button := _button(("▾  " if expanded else "▸  ")+"Population profile", func(): pass, "Age, religion and education")
	button.name = "StateProfileToggle" if state_scope else "NationalProfileToggle"
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.toggle_mode = true
	button.set_pressed_no_signal(expanded)
	button.pressed.connect(func():
		chart.visible = button.button_pressed
		button.text = ("▾  " if chart.visible else "▸  ")+"Population profile"
		if state_scope: territory_profile_expanded = chart.visible
		else: national_profile_expanded = chart.visible
		if foundation != null: foundation.refresh_active_section())
	details.add_child(button)
	chart.visible = expanded
	details.add_child(chart)

func _show_country(tag: String, focus: bool = true) -> void:
	if not state.countries.has(tag):
		return
	active_feature = ""
	_preview_state(0)
	_reveal_panel(control_panel)
	details = control_details
	state.selected_country = tag
	inspection_active = true
	var allow_state_selection := screen == "playing" and (distance <= 1.65)
	if not allow_state_selection:
		inspect_region = 0
		inspect_province = 0
	state.selected_region = inspect_region if inspect_region > 0 and state.regions[str(inspect_region)]["owner"] == tag else 0
	state.selected_province = inspect_province if state.provinces.has(str(inspect_province)) and int(state.provinces[str(inspect_province)]["region"]) == state.selected_region else 0
	state.selected_sea = 0
	var c: Dictionary = state.countries[tag]
	var metrics := state.country_metrics(tag)
	_clear_details()
	details.add_child(_label("COUNTRY CONTROL" if screen == "playing" and tag == state.player_country else "DIPLOMACY / INFORMATION", 11, Color("63c9b6")))
	_entity_heading(c["name"], flags.resolve(tag, str(c.get("cosmetic", "")), c["outlook"]))
	details.add_child(_wrapped(c["outlook"], 14, Color("e5c888")))
	var values: Dictionary = c.get("starting_stats", {})
	var per_capita := float(values.get("gdp_per_capita_usd", 0))
	var politics_summary := preload("res://scripts/political_summary.gd").new()
	var open_government := Callable()
	if screen == "playing" and tag == state.player_country:
		open_government = func(): _show_feature("Government")
	politics_summary.configure(true, open_government)
	details.add_child(politics_summary)
	_briefing_section("National overview")
	_summary_grid([
		["Population", foundation.compact_number(int(metrics["population"])), "Residents: "+_number(int(metrics["population"]))],
		["GDP", foundation.compact_money(per_capita*float(metrics["population"])), "GDP: $"+_number(int(per_capita*float(metrics["population"])))],
		["GDP / person", foundation.compact_money(per_capita), "GDP per capita: $"+_number(int(per_capita))],
		["Stability", "%.0f%%" % (float(values.get("stability",.65))*100)],
		["War support", "%.0f%%" % (float(values.get("war_support",.5))*100)],
		["States", str(metrics["regions"].size())]])
	var capital: String = str(int(c["capital"]))
	details.add_child(_wrapped("%d states  ·  Capital state: %s" % [metrics["regions"].size(), state.regions.get(capital,{}).get("name","Unknown")],12,Color("93a8aa")))
	if screen == "playing" and tag != state.player_country:
		_briefing_section("Diplomatic relations")
		_opinion_stat(state.player_country, tag)
		_opinion_stat(tag, state.player_country)
	var demographic_entry: Dictionary = foundation.demographics.country_metrics(state, tag)
	var workforce := preload("res://scripts/workforce_panel.gd").new()
	workforce.configure(demographic_entry["workforce"])
	details.add_child(workforce)
	var chart := preload("res://scripts/compact_demographics.gd").new()
	chart.name = "NationalDemographics"
	chart.configure(demographic_entry, national_metric, func(key: String): national_metric = key, false)
	_population_profile(chart, false)
	_show_territory()

	_briefing_section("Organizations")
	var memberships := state.memberships(tag)
	if memberships.is_empty():
		details.add_child(_wrapped("No memberships listed."))
	var organization_grid := _icon_grid(4)
	for oid: String in memberships:
		organization_grid.add_child(_icon_button(state.organizations[oid]["name"], _organization_texture(oid, true), func(): _open_organization(oid), Vector2(64, 54), _organization_light_background(oid)))
	details.add_child(HSeparator.new())
	if screen == "playing":
		if tag == state.player_country:
			_briefing_section("Government")
			var government: Dictionary = c.get("government", {})
			details.add_child(_wrapped(str(government.get("party", "")) if not str(government.get("party", "")).is_empty() else str(c["outlook"])))
			details.add_child(_button("Open government", func(): _show_feature("Government")))
		else:
			_briefing_section("Diplomatic actions")
			for action: String in ["Improve relations", "Offer treaty", "Trade agreement", "Diplomatic support", "Declare war"]:
				_placeholder(action)
	if map_mode == 7: _rebuild_palette()
	else: _update_selection_shader()
	var index := country_tags.find(tag)
	if index >= 0:
		country_list.select(index)
		country_list.ensure_current_is_visible()
	if focus:
		_focus_country(tag)
	if foundation != null: foundation.refresh_active_section()

func _selection_breadcrumb(region: Dictionary) -> void:
	var row := HBoxContainer.new()
	row.name = "SelectionBreadcrumb"
	row.add_theme_constant_override("separation", 2)
	var tag: String = region["owner"]
	var country := _button(str(state.countries[tag]["name"]), func(): _show_country_states(tag), "Browse this country's States")
	country.name = "BrowseCountryStates"
	var record: Dictionary = state.countries[tag]
	country.icon = flags.resolve(tag, str(record.get("cosmetic", "")), record["outlook"])
	country.expand_icon = true
	country.add_theme_constant_override("icon_max_width", 22)
	var state_button := _button(str(region["name"]), func(): _open_country_state(int(region["id"])), "Show selected State")
	for button: Button in [country,state_button]:
		button.add_theme_font_size_override("font_size",11)
		button.clip_text=true; button.custom_minimum_size.x=82
		button.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	row.add_child(country)
	row.add_child(_label("›",12,Color("b5a680")))
	row.add_child(state_button)
	if state.selected_province>0 and distance<=1.2:
		row.add_child(_label("›",12,Color("b5a680")))
		var province: Dictionary=state.provinces[str(state.selected_province)]
		var current := _label("Province "+str(int(province.get("local_index",state.selected_province))),11,Color("e9dfc3"))
		current.tooltip_text=str(province.get("name","Selected province"))
		row.add_child(current)
	details.add_child(row)

func _show_territory() -> void:
	_preview_state(0)
	preload("res://scripts/territory_view.gd").new().render(self)

func _show_country_states(tag: String) -> void:
	_preview_state(0)
	preload("res://scripts/territory_view.gd").new().country_states(self,tag)
	_focus_country(tag)

func _open_country_state(id: int) -> void:
	if not state.regions.has(str(id)): return
	_preview_state(0)
	inspect_region=id
	inspect_province=0
	state.selected_country=state.regions[str(id)]["owner"]
	state.selected_region=id
	state.selected_province=0
	state.selected_sea=0
	inspection_active=true
	_update_selection_shader()
	_show_territory()
	_focus_state(id)

func _focus_state(id: int) -> void:
	var region: Dictionary=state.regions[str(id)]
	var points: Array[Vector2]=[]
	var anchor:=Vector3.ZERO
	for pid: int in region["provinces"]:
		var p: Dictionary=state.provinces[str(pid)]
		var uv:=Vector2(p["map_center"][0],p["map_center"][1])
		points.append(uv)
		anchor+=ReliefSurface.unit_point(uv)*maxf(1.0,float(p["area_km2"]))
	var center:=ReliefSurface.uv_of(anchor.normalized())
	var radius:=sqrt(maxf(1.0,float(region["area_km2"]))/PI)/6371.0
	for uv: Vector2 in points:
		radius=maxf(radius,acos(clampf(ReliefSurface.unit_point(center).dot(ReliefSurface.unit_point(uv)),-1,1)))
	# Leave room for both inspectors, and fit the State rather than its capital.
	var available:=maxf(.25,1.0-2.0*_territory_width()/maxf(1.0,size.x))
	var horizontal:=2.0*atan(tan(deg_to_rad(camera.fov)*.5)*view_container.size.x/maxf(1.0,view_container.size.y)*available)
	var fit_angle:=maxf(.06,minf(deg_to_rad(camera.fov),horizontal)*.38)
	var target_distance:=clampf(1.0+sin(minf(radius+.012,1.4))/tan(fit_angle),1.06,3.2)
	var target:=Vector3(clampf((.5-center.y)*PI,-1.5,1.5),-(center.x-.5)*TAU,0)
	target.y=planet.rotation.y+wrapf(target.y-planet.rotation.y,-PI,PI)
	rotation_velocity=Vector2.ZERO
	if focus_tween!=null:focus_tween.kill()
	focus_tween=create_tween().set_parallel(true)
	focus_tween.tween_property(planet,"rotation",target,.55).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	focus_tween.tween_property(self,"distance",target_distance,.55).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)

func _open_organization(oid: String) -> void:
	active_org = oid
	map_mode = 1
	map_picker.select(1)
	org_picker.visible = true
	org_picker.select(org_ids.find(oid))
	_rebuild_palette()
	_show_organization()

func _show_organization() -> void:
	_hide_panel(control_panel)
	_reveal_panel(right_panel)
	details = diplomatic_details
	var org: Dictionary = state.organizations[active_org]
	_clear_details()
	details.add_child(_label("INTERNATIONAL ORGANIZATION", 11, Color("63c9b6")))
	_entity_heading(org["name"], _organization_texture(active_org), true)
	details.add_child(_wrapped(org["purpose"], 15, Color("e5c888")))
	details.add_child(HSeparator.new())
	_stat("Members", str(org["members"].size()))
	_stat("Role", org["direction"])
	if org.has("membership_note"): details.add_child(_wrapped(org["membership_note"], 12))
	details.add_child(HSeparator.new())
	details.add_child(_label("MEMBERSHIP", 11, Color("63c9b6")))
	var members: Array = org["members"].duplicate()
	members.sort_custom(func(a: String, b: String): return state.countries[a]["name"].naturalnocasecmp_to(state.countries[b]["name"]) < 0)
	var country_grid := _icon_grid()
	for tag: String in members:
		var c: Dictionary = state.countries[tag]
		country_grid.add_child(_icon_button(c["name"], flags.resolve(tag, str(c.get("cosmetic", "")), c["outlook"]), func(): _show_country(tag, true)))
	details.add_child(HSeparator.new())
	details.add_child(_wrapped("Budgets, proposals and shared projects will arrive in the next development stages.", 13))

func _map_changed(index: int) -> void:
	overlay_layout_dirty = true
	_play_ui("click")
	map_mode = index
	map_picker.select(index)
	org_picker.visible = index == 1
	relations_picker.visible = index == 7
	_rebuild_palette()
	if map_mode == 1:
		_show_organization()
	elif state.selected_sea > 0:
		_show_sea(state.selected_sea)
	else:
		_show_country(state.selected_country, false)

func _organization_changed(index: int) -> void:
	overlay_layout_dirty = true
	_play_ui("click")
	active_org = org_ids[index]
	_rebuild_palette()
	_show_organization()

func _focus_country(tag: String, animated: bool = true) -> void:
	var point: Array = state.countries[tag]["map_center"]
	var target := Vector3(clampf((0.5 - float(point[1])) * PI, -1.45, 1.45), -(float(point[0]) - 0.5) * TAU, 0)
	rotation_velocity = Vector2.ZERO
	if focus_tween != null:
		focus_tween.kill()
	var rotation := planet.rotation
	target.y = rotation.y + wrapf(target.y - rotation.y, -PI, PI)
	if animated:
		focus_tween = create_tween()
		focus_tween.tween_property(planet, "rotation", target, 0.55).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	else:
		planet.rotation = target
	_update_camera_pose()

func _update_camera_pose() -> void:
	if camera == null: return
	var key: Array = [distance, planet.global_transform if planet != null else Transform3D()]
	if key == last_camera_view: return
	last_camera_view = key
	camera_pose_updates += 1
	if planet == null:
		camera.position = Vector3(0, 0, distance)
		return
	var front := planet.global_transform.basis.inverse() * Vector3.BACK
	var uv := Surface.uv_of(front)
	var mountain_offset: float = (relief_surface.height_at(uv) if relief_surface != null else 0.0) * smoothstep(1.08, 1.02, distance)
	var radius: float = 1.0 + mountain_offset
	var amount := smoothstep(0.0, 1.0, clampf((1.18 - distance) / .165, 0, 1))
	camera_tilt_degrees = 38.0 * amount
	var tilt := deg_to_rad(camera_tilt_degrees)
	var anchor := Vector3(0, 0, radius)
	var clearance := maxf(.015, distance - 1.0)
	camera.position = anchor + Vector3(0, -sin(tilt), cos(tilt)) * clearance
	camera.look_at(anchor, Vector3.UP)
	_update_border_visibility()

func _uv_at(position: Vector2) -> Vector2:
	# Cache only the geometric intersection, never owner/state data. Repeated
	# region/province/sea queries share one accurate relief ray per view/point.
	var key: Array = [position, camera.global_transform, planet.global_transform, world_view.size, camera.fov, camera.near, camera.far, camera.projection, camera.keep_aspect, camera.size, camera.frustum_offset, camera.h_offset, camera.v_offset, relief_surface.get_instance_id()]
	if key == last_pick_key:
		pick_cache_hits += 1
		return last_pick_uv
	last_pick_key = key
	pick_ray_marches += 1
	var inverse := planet.global_transform.affine_inverse()
	var origin: Vector3 = inverse * camera.project_ray_origin(position)
	var direction: Vector3 = inverse.basis * camera.project_ray_normal(position)
	var point: Vector3 = relief_surface.ray_point(origin, direction.normalized())
	last_pick_uv = Surface.uv_of(point) if point != Vector3.ZERO else Vector2(-1, -1)
	return last_pick_uv

func _map_pixel_at(position: Vector2) -> Color:
	var uv := _uv_at(position)
	if uv.x < 0: return Color.BLACK
	if _water_passage_at(uv)>0: return Color.BLACK
	return map_rendering.pixel_at_uv(uv)

func _region_at(position: Vector2) -> int:
	if tiny_state_markers!=null:
		var marker: int=tiny_state_markers.province_at(position)
		if marker>0:return int(state.provinces[str(marker)]["region"])
	var pixel := _map_pixel_at(position)
	var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	if pid == 65535: return 8191
	return int(state.provinces.get(str(pid), {}).get("region", 0))

func _province_at(position: Vector2) -> int:
	if tiny_state_markers!=null:
		var marker: int=tiny_state_markers.province_at(position)
		if marker>0:return marker
	var pixel := _map_pixel_at(position)
	var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	return pid if state.provinces.has(str(pid)) else 0

func _ui_blocks_globe(position: Vector2) -> bool:
	# GUI events use viewport-local coordinates. A wheel event can bubble from
	# a child even when its panel uses MOUSE_FILTER_STOP, unless forced scroll
	# propagation is disabled. Also guard the camera when a drag enters a panel.
	var point := view_container.get_global_transform() * position
	for panel: Control in [control_panel, right_panel, territory_panel, territory_handle, clock_box, map_box, selection_box, top_left_box]:
		if panel == null or not panel.is_visible_in_tree() or not panel.get_global_rect().has_point(point):
			continue
		if panel == territory_panel and (not territory_clip.visible or not territory_clip.get_global_rect().has_point(point)):
			continue
		return true
	return false

func _globe_input(event: InputEvent) -> void:
	if event is InputEventMouse and _ui_blocks_globe(event.position):
		pending_hover = false
		dragging = false
		rotation_velocity = Vector2.ZERO
		return
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP and event.pressed:
			distance = maxf(1.015, 1.0 + (distance - 1.0) * 0.82)
			_update_camera_pose()
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN and event.pressed:
			distance = minf(8.0, 1.0 + (distance - 1.0) / 0.82)
			_update_camera_pose()
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			dragging = event.pressed
			if dragging:
				pending_hover = false
				rotation_velocity = Vector2.ZERO
				last_drag_time = Time.get_ticks_msec()
				if focus_tween != null: focus_tween.kill()
			elif Time.get_ticks_msec() - last_drag_time > 100:
				rotation_velocity = Vector2.ZERO
		elif event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
			rotation_velocity = Vector2.ZERO
			var id := _region_at(event.position)
			if state.regions.has(str(id)):
				var allow_state_selection := screen == "playing" and (distance <= 1.65)
				inspect_region = id if allow_state_selection else 0
				inspect_province = _province_at(event.position) if (allow_state_selection and distance <= 1.2) else 0
				_show_country(state.regions[str(id)]["owner"], false)
			elif id == 0:
				var sea := _sea_at(event.position)
				if sea > 0 and screen == "playing": _show_sea(sea)
				else: _close_panels()
			elif id == 8191: _close_panels()
			_play_ui("select")
		view_container.accept_event()
	elif event is InputEventMouseMotion:
		if dragging and (event.button_mask & MOUSE_BUTTON_MASK_RIGHT) != 0:
			var step: Vector2 = event.relative * 0.006 * clampf((distance - 1.0) * 0.35, 0.0025, 1.0)
			planet.rotation.y += step.x
			planet.rotation.x = clampf(planet.rotation.x + step.y, -1.5, 1.5)
			var now := Time.get_ticks_msec()
			var elapsed := maxf(0.008, float(now - last_drag_time) / 1000.0)
			rotation_velocity = rotation_velocity.lerp((step / elapsed).limit_length(0.8), 0.4)
			last_drag_time = now
		else:
			dragging = false
			_queue_map_hover(event.position)

func _process(delta: float) -> void:
	if not boot_complete: return
	if ownership_visual_dirty:
		ownership_visual_dirty=false
		_rebuild_palette()
		_update_country_bar()
		if country_label_layer!=null:country_label_layer.refresh_if_changed()
	if hover_panel != null:
		if foundation != null and foundation.modals_visible() or dragging or screen == "menu" or console != null and console.visible or game_menu != null and game_menu.visible or save_dialog != null and save_dialog.visible or load_dialog != null and load_dialog.visible or overwrite_dialog != null and overwrite_dialog.visible:
			hover_panel.hide()
		elif hover_panel.visible:
			_position_map_hover()
	if planet_material != null:
		if not dragging and screen != "menu" and not console.visible:
			planet.rotation.y += rotation_velocity.x * delta
			planet.rotation.x = clampf(planet.rotation.x + rotation_velocity.y * delta, -1.5, 1.5)
			rotation_velocity *= exp(-10.0 * delta)
			if rotation_velocity.length() < 0.0001: rotation_velocity = Vector2.ZERO
		_update_camera_pose()
		_update_view_uniforms()
		_flush_map_hover()
		var target_hover := 1.0 if hover_panel.visible and hover_owner>0.0 and not dragging else 0.0
		hover_blend = move_toward(hover_blend, target_hover, delta*7.0)
		var hover_view: Array = [hover_owner if target_hover > 0.0 else 0.0, hover_blend]
		if hover_view != last_hover_view:
			last_hover_view = hover_view
			planet_material.set_shader_parameter("hovered_country", hover_view[0])
			planet_material.set_shader_parameter("hover_amount", hover_blend)
		_update_cities()
		if urban_scenery != null: urban_scenery.update_view(camera, distance, city_scenery_enabled and screen != "menu", delta)
		if country_label_layer != null: country_label_layer.update_view()
		if tiny_state_markers!=null:tiny_state_markers.update_view()
		_position_panels(false)
	if screen == "playing" and not state.database.is_empty() and state.advance(delta):
		_update_clock()
		if state.day != last_relation_day:
			last_relation_day = state.day
			_update_country_bar()
			var government_panel: Node = control_details.get_node_or_null("PoliticalPanel")
			if government_panel != null: government_panel.refresh()
			_refresh_opinions()
			if map_mode == 7: _rebuild_palette()
	_update_map_rendering(delta)

# View-dependent uniforms change on zoom/mode changes, never on idle frames.
func _update_view_uniforms() -> void:
	var key: Array = [distance, map_mode]
	if key == last_surface_view: return
	last_surface_view = key
	view_uniform_updates += 1
	show_regions = distance <= 1.65
	planet_material.set_shader_parameter("show_regions", show_regions)
	planet_material.set_shader_parameter("region_opacity", clampf((1.65 - distance) / 0.15, 0, 1))
	planet_material.set_shader_parameter("camera_distance", distance)
	planet_material.set_shader_parameter("province_opacity", clampf((1.2 - distance) / 0.08, 0, 1))
	planet_material.set_shader_parameter("city_detail", clampf((1.50 - distance) / .25, 0, 1))
	planet_material.set_shader_parameter("far_filter", clampf((distance - 2.4) / 1.0, 0, 1))
	planet_material.set_shader_parameter("border_strength", clampf((4.1 - distance) / 1.3, 0, 1))
	planet_material.set_shader_parameter("coast_strength", clampf((3.2 - distance) / 1.0, 0, 1))
	planet_material.set_shader_parameter("terrain_mix", clampf((2.3 - distance) / 0.9, 0, 1) if map_mode == 6 else 0.0)
	for material: ShaderMaterial in border_materials:
		material.set_shader_parameter("show_regions", show_regions)
		material.set_shader_parameter("camera_distance", distance)
	waterways_material.set_shader_parameter("physical_mode", map_mode == 6)
	waterways_material.set_shader_parameter("camera_distance", distance)

func _toggle_pause() -> void:
	if screen != "playing":
		return
	state.paused = not state.paused
	_update_clock()

func _update_clock() -> void:
	overlay_layout_dirty = true
	date_text.text = state.date_label().replace("January", "Jan").replace("February", "Feb").replace("March", "Mar").replace("April", "Apr").replace("June", "Jun").replace("July", "Jul").replace("August", "Aug").replace("September", "Sep").replace("October", "Oct").replace("November", "Nov").replace("December", "Dec")
	date_text.tooltip_text = state.date_label()
	pause_button.text = "▶" if state.paused else "Ⅱ"
	pause_button.tooltip_text = ("Resume" if state.paused else "Pause") + " · Space"
	speed_picker.select(State.SPEEDS.find(state.speed))

func _speed_changed(index: int) -> void:
	_play_ui("click")
	state.speed = State.SPEEDS[index]
	_update_clock()

func _view_state() -> Dictionary:
	return {"rotation": [planet.rotation.x, planet.rotation.y], "distance": distance,
		"map_mode": map_mode, "organization": active_org, "show_regions": show_regions, "inspection_active": inspection_active, "relations_reverse": relations_reverse}

func _save() -> void:
	if screen != "playing":
		return
	_pause_for_dialog()
	save_slots = Catalog.scan(save_directory)
	save_entries.clear()
	for entry: Dictionary in save_slots:
		save_entries.add_item(entry["label"])
	save_name_field.text = last_save_name if not last_save_name.is_empty() else str(state.countries[state.player_country]["name"]) + " - " + state.date_label().replace(":", "h").replace("  ·  ", " - ")
	save_feedback.text = "Enter a name for a new save, or select an existing save to replace."
	save_dialog.popup_centered(Vector2i(660, 470))
	save_name_field.grab_focus()
	save_name_field.select_all()

func _load() -> void:
	_pause_for_dialog()
	var entries := Catalog.scan(save_directory)
	load_entries.clear()
	load_paths.clear()
	for entry: Dictionary in entries:
		load_entries.add_item(entry["label"])
		load_paths.append(entry["path"])
	load_dialog.get_ok_button().disabled = true
	load_feedback.text = "Select a save and confirm Load." if not entries.is_empty() else "No saved campaigns yet. Start a world and save it first."
	load_dialog.popup_centered(Vector2i(680, 450))

func _load_from(path: String, show_errors: bool = true) -> bool:
	var view := state.load_game(path)
	var loaded_sea := state.selected_sea
	if view.is_empty():
		if show_errors:
			_show_error(state.last_error)
		return false
	if focus_tween != null:
		focus_tween.kill()
	planet.rotation = Vector3(float(view["rotation"][0]), float(view["rotation"][1]), 0)
	distance = float(view["distance"])
	_update_camera_pose()
	map_mode = int(view["map_mode"])
	active_org = view["organization"]
	relations_reverse = view["relations_reverse"]
	relations_picker.select(1 if relations_reverse else 0)
	relations_picker.visible = map_mode == 7
	show_regions = view["show_regions"]
	inspect_region = state.selected_region
	inspect_province = state.selected_province
	map_picker.select(map_mode)
	org_picker.select(org_ids.find(active_org))
	org_picker.visible = map_mode == 1
	show_regions = distance <= 1.65
	_rebuild_palette()
	_update_country_list()
	_show_country(state.selected_country, false)
	_update_clock()
	_enter_campaign(false)
	_show_country(state.selected_country, false)
	inspection_active = view["inspection_active"]
	_update_selection_shader()
	if loaded_sea > 0: _show_sea(loaded_sea)
	last_save_name = path.get_file().get_basename()
	_set_status("Loaded  ·  " + state.date_label() + "  ·  Clock paused")
	_play_ui("confirm")
	return true

func _show_error(message: String) -> void:
	_play_ui("error")
	_set_status(message)
	info_dialog.dialog_text = message
	info_dialog.popup_centered(Vector2i(540, 190))


func _confirm_reset() -> void:
	var dialog := ConfirmationDialog.new()
	dialog.title = "Start a new world"
	dialog.dialog_text = "Return to 1 January 2000? Your saved world will remain available."
	add_child(dialog)
	dialog.confirmed.connect(_reset)
	dialog.confirmed.connect(dialog.queue_free)
	dialog.canceled.connect(dialog.queue_free)
	dialog.popup_centered(Vector2i(490, 170))

func _reset() -> void:
	state.reset()
	inspect_region = 0
	search.text = ""
	list_filter = ""
	_update_country_list()
	_rebuild_palette()
	_show_country(state.selected_country)
	_update_clock()
	_set_status("New world  ·  1 January 2000")

func _set_status(message: String) -> void:
	status.text = message

func _help() -> void:
	state.paused = true
	_update_clock()
	info_dialog.title = "Bunny World " + build_version + " — Controls"
	info_dialog.dialog_text = "Right-drag: rotate with short momentum. Wheel: zoom.\nLeft click: select land; click water to close country panels.\nClick your country flag to open its control panel. F: focus country.\n\nStates appear as you zoom closer; provinces at the closest levels.\nCapitals use stars. Physical Earth shows natural daytime terrain.\nCtrl+F: find cities, states, countries and landmarks.\nCity buildings/landmarks can be toggled in the game menu.\n\nSpace: pause/play     1–4: speed     F5/F9: save/load\nF11: fullscreen     Escape: game menu     Backtick: console\n\nHover membership icons for names; click for information.\nProvinces are movement/building foundations; those systems come later.\n\nSave folder: " + ProjectSettings.globalize_path("user://saves")
	info_dialog.popup_centered(Vector2i(720, 470))

func _quit() -> void:
	get_tree().quit()

func _open_save_folder() -> void:
	var folder := ProjectSettings.globalize_path("user://saves")
	var error := DirAccess.make_dir_recursive_absolute(folder)
	if error != OK or OS.shell_open(folder) != OK:
		_show_error("Could not open the save folder: " + folder)

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and pause_button != null:
		state.paused = true
		_update_clock()

func _close_side_tabs() -> bool:
	var closed := false
	if territory_panel != null and (territory_panel.visible or (territory_clip != null and territory_clip.visible)):
		_hide_panel(territory_panel)
		closed = true
	if control_panel != null and control_panel.visible:
		active_feature = ""
		_hide_panel(control_panel)
		if right_panel != null and right_panel != control_panel:
			_hide_panel(right_panel)
		inspection_active = false
		state.selected_region = 0
		state.selected_province = 0
		_update_selection_shader()
		closed = true
	return closed

func _input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	var focus := get_viewport().gui_get_focus_owner() if get_viewport() != null else null
	var is_typing := (focus is LineEdit or focus is TextEdit)
	if event.keycode == KEY_SPACE and not is_typing and screen == "playing":
		if not save_dialog.visible and not load_dialog.visible and not overwrite_dialog.visible and not game_menu.visible and not console.visible:
			_toggle_pause()
			get_viewport().set_input_as_handled()
			return
	if event.keycode == KEY_ESCAPE:
		if is_typing:
			focus.release_focus()
			get_viewport().set_input_as_handled()
			return
		if not save_dialog.visible and not load_dialog.visible and not overwrite_dialog.visible and not game_menu.visible and not console.visible:
			if _close_side_tabs():
				get_viewport().set_input_as_handled()
				return

func _unhandled_key_input(event: InputEvent) -> void:
	if not event is InputEventKey or not event.pressed or event.echo:
		return
	if event.keycode == KEY_QUOTELEFT:
		if not save_dialog.visible and not load_dialog.visible and not game_menu.visible: _toggle_console()
		return
	if save_dialog.visible or load_dialog.visible or overwrite_dialog.visible or game_menu.visible or console.visible:
		return
	if event.ctrl_pressed and event.keycode == KEY_F and screen != "menu":
		_open_place_search()
		get_viewport().set_input_as_handled()
		return
	if place_dialog != null and place_dialog.visible: return
	if foundation != null and foundation.modals_visible(): return
	if get_viewport().gui_get_focus_owner() is LineEdit:
		if event.keycode == KEY_ESCAPE:
			get_viewport().gui_get_focus_owner().release_focus()
		return
	if screen == "menu" and event.keycode not in [KEY_F9, KEY_F11]:
		return
	match event.keycode:
		KEY_SPACE: _toggle_pause()
		KEY_F: _focus_country(state.selected_country)
		KEY_F5: _save()
		KEY_F9: _load()
		KEY_F11:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN else DisplayServer.WINDOW_MODE_FULLSCREEN)
		KEY_ESCAPE:
			if not _close_side_tabs():
				_open_game_menu()
		KEY_1: _speed_changed(0)
		KEY_2: _speed_changed(1)
		KEY_3: _speed_changed(2)
		KEY_4: _speed_changed(3)

func _capture() -> void:
	await get_tree().create_timer(1.0).timeout
	if not capture_to.is_empty():
		var matches := places.find_places(capture_to)
		if not matches.is_empty(): _go_to_place(matches[0],false)
	if capture_point.x > -999:
		if focus_tween != null: focus_tween.kill()
		var uv := Vector2((capture_point.x + 180.0) / 360.0, (90.0 - capture_point.y) / 180.0)
		planet.rotation = Vector3(clampf((.5 - uv.y) * PI, -1.45, 1.45), -(uv.x - .5) * TAU, 0)
		_update_camera_pose()
	if capture_state > 0 and state.regions.has(str(capture_state)):
		if focus_tween != null: focus_tween.kill()
		var region: Dictionary = state.regions[str(capture_state)]
		var center: Array = region["map_center"]
		planet.rotation = Vector3(clampf((.5 - float(center[1])) * PI, -1.45, 1.45), -(float(center[0])-.5)*TAU, 0)
		inspect_region = capture_state
		_show_country(region["owner"], false)
	await get_tree().create_timer(5.0 if map_mode == 6 else 1.5).timeout
	if capture_water > 0 and state.sea_regions.has(str(capture_water)):
		var point: Array = state.sea_regions[str(capture_water)]["map_center"]
		planet.rotation = Vector3(clampf((.5 - float(point[1])) * PI, -1.45, 1.45), -(float(point[0])-.5)*TAU, 0)
		_show_sea(capture_water)
	if capture_inspect:
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.pressed = true
		click.position = Vector2(world_view.size) / 2.0
		_globe_input(click)
	if capture_memberships:
		var scroll: ScrollContainer = details.get_parent()
		var sections := details.get_children()
		for i: int in sections.size():
			if sections[i] is Label and sections[i].text == "ORGANIZATIONS" and i + 1 < sections.size():
				scroll.ensure_control_visible(sections[i + 1])
	if capture_tooltip:
		Input.warp_mouse(view_container.global_position + view_container.size * Vector2(.61,.45))
		_update_map_hover(Vector2(world_view.size) * Vector2(.61,.45))
	if not capture_find.is_empty():
		_open_place_search()
		place_input.text = capture_find
		_find_places(capture_find)
	match capture_foundation:
		"demographics", "religion", "education", "activity": foundation.open_demographics(state.selected_country, capture_state)
		"ledger": foundation.open_ledger()
		"tension": foundation.open_tension()
	await get_tree().create_timer(.5).timeout
	await RenderingServer.frame_post_draw
	var result := get_viewport().get_texture().get_image().save_png(capture_path)
	print("RESIDENT_TERRAIN material_layers=", resident_terrain.layer_count, " runtime_uploads=0")
	print("CAPTURE_RESULT ", result)
	print("CAPTURE_TERRAIN tilt_degrees=", camera_tilt_degrees, " surface=single_sphere")
	if urban_scenery != null: print("CAPTURE_URBAN alpha=", urban_scenery.visibility_alpha, " buildings=", urban_scenery.visible_buildings, " clusters=", urban_scenery.active.size(), " landmarks=", urban_scenery.active_landmarks.keys(), " peak=", urban_scenery.peak_visible_buildings)
	print("CAPTURE_LAYOUT viewport=", get_viewport().get_visible_rect().size, " window=", DisplayServer.window_get_size())
	print("CAPTURE_REFINEMENTS scenery_enabled=",city_scenery_enabled," place_results=",place_matches.size()," selected_country=",state.selected_country," province=",state.selected_province)
	get_tree().quit(result)

func _run_smoke_test() -> void:
	await get_tree().create_timer(0.7).timeout
	var checks: Array[bool] = []
	_smoke_check(checks, Catalog.valid_name("My Poland campaign"), "Catalog.valid_name(\"My Poland campaign\")")
	_smoke_check(checks, not Catalog.valid_name("../bad") and not Catalog.valid_name("CON") and not Catalog.valid_name(""), "not Catalog.valid_name(\"../bad\") and not Catalog.valid_name(\"CON\") and not Catalog.valid_name(\"\")")
	_smoke_check(checks, screen == "menu" and state.paused and menu_screen.visible and not game_ui.visible, "screen == \"menu\" and state.paused and menu_screen.visible and not game_ui.visible")
	_start_selection()
	_smoke_check(checks, screen == "selection" and country_sidebar.visible and state.paused, "screen == \"selection\" and country_sidebar.visible and state.paused")
	_process(0.25)
	_smoke_check(checks, state.day == 0, "state.day == 0")
	_show_country("POL", false)
	_begin_campaign()
	_smoke_check(checks, screen == "playing" and not country_sidebar.visible and state.paused and state.player_country == "POL", "screen == \"playing\" and not country_sidebar.visible and state.paused and state.player_country == \"POL\"")
	_show_country("GER", false)
	_smoke_check(checks, state.player_country == "POL", "state.player_country == \"POL\"")
	_smoke_check(checks, right_panel.visible and not control_panel.visible and title_label.text == state.countries["POL"]["name"], "right_panel.visible and not control_panel.visible and title_label.text == state.countries[\"POL\"][\"name\"]")
	_show_country("POL", false)
	_smoke_check(checks, control_panel.visible and not right_panel.visible, "control_panel.visible and not right_panel.visible")
	_close_panels()
	_smoke_check(checks, not control_panel.visible and not right_panel.visible and not inspection_active, "not control_panel.visible and not right_panel.visible and not inspection_active")
	var flag_click := InputEventMouseButton.new()
	flag_click.button_index = MOUSE_BUTTON_LEFT
	flag_click.pressed = true
	header_flag.gui_input.emit(flag_click)
	_smoke_check(checks, control_panel.visible and state.selected_country == state.player_country, "control_panel.visible and state.selected_country == state.player_country")
	_close_panels()
	_open_game_menu()
	_smoke_check(checks, game_menu.visible and state.paused, "game_menu.visible and state.paused")
	game_menu.hide()
	_resume_after_dialog()
	_smoke_check(checks, not stats_label.text.is_empty(), "not stats_label.text.is_empty()")
	_smoke_check(checks, state.organizations["CSTO"]["members"].size() == 6, "state.organizations[\"CSTO\"][\"members\"].size() == 6")
	_smoke_check(checks, Commands.execute(state, "tag jap").begins_with("Now playing"), "Commands.execute(state, \"tag jap\").begins_with(\"Now playing\")")
	_smoke_check(checks, state.player_country == "JAP", "state.player_country == \"JAP\"")
	_show_country("CHI", false)
	_smoke_check(checks, opinion_labels.size() == 2, "opinion_labels.size() == 2")
	if opinion_labels.size() == 2:
		_smoke_check(checks, opinion_labels[0].get_meta("from") == "JAP" and opinion_labels[0].get_meta("toward") == "CHI" and opinion_labels[0].text == "-20", "opinion_labels[0].get_meta(\"from\") == \"JAP\" and opinion_labels[0].get_meta(\"toward\") == \"CHI\" and opinion_labels[0].text == \"-20\"")
		_smoke_check(checks, opinion_labels[1].get_meta("from") == "CHI" and opinion_labels[1].get_meta("toward") == "JAP" and opinion_labels[1].text == "-40", "opinion_labels[1].get_meta(\"from\") == \"CHI\" and opinion_labels[1].get_meta(\"toward\") == \"JAP\" and opinion_labels[1].text == \"-40\"")
		_smoke_check(checks, state.set_opinion("JAP", "CHI", -77), "state.set_opinion(\"JAP\", \"CHI\", -77)")
		_refresh_opinions()
		_smoke_check(checks, opinion_labels[0].text == "-77" and opinion_labels[1].text == "-40" and "China" in opinion_labels[0].tooltip_text, "opinion_labels[0].text == \"-77\" and opinion_labels[1].text == \"-40\" and \"China\" in opinion_labels[0].tooltip_text")
		state.relation_offsets.erase("JAP|CHI")
	_smoke_check(checks, Commands.execute(state, "set stability 80").contains("updated"), "Commands.execute(state, \"set stability 80\").contains(\"updated\")")
	_smoke_check(checks, is_equal_approx(float(state.countries["JAP"]["starting_stats"]["stability"]), 0.8), "is_equal_approx(float(state.countries[\"JAP\"][\"starting_stats\"][\"stability\"]), 0.8)")
	_smoke_check(checks, Commands.execute(state, "set stability 101").contains("outside"), "Commands.execute(state, \"set stability 101\").contains(\"outside\")")
	Commands.execute(state, "tag pol")
	_update_country_bar()
	_smoke_check(checks, "Stability: 65%" in stats_label.text and "War support: 50%" in stats_label.text, "\"Stability: 65%\" in stats_label.text and \"War support: 50%\" in stats_label.text")
	_smoke_check(checks, "Political power: 100" in stats_label.text, "\"Political power: 100\" in stats_label.text")
	_smoke_check(checks, flags.resolve("JAP", "", "Western Outlook") != null, "flags.resolve(\"JAP\", \"\", \"Western Outlook\") != null")
	for mode: int in [4, 5]:
		_map_changed(mode)
		_smoke_check(checks, map_mode == mode and "GDP" in legend.text, "map_mode == mode and \"GDP\" in legend.text")
	_map_changed(6)
	_smoke_check(checks, resident_terrain.initialized and map_picker.item_count == 8, "resident_terrain.initialized and map_picker.item_count == 8")
	_smoke_check(checks, state.countries["CHI"]["cosmetic"] == "CHI_AUTH_S" and state.countries["VIE"]["cosmetic"] == "VIE_AUTH_S", "state.countries[\"CHI\"][\"cosmetic\"] == \"CHI_AUTH_S\" and state.countries[\"VIE\"][\"cosmetic\"] == \"VIE_AUTH_S\"")
	_smoke_check(checks, state.provinces.size() > state.regions.size() and state.provinces.size() < 65535, "state.provinces.size() > state.regions.size() and state.provinces.size() < 65535")
	for oid: String in state.organizations:
		var logo := _organization_texture(oid)
		if logo == null: printerr("Missing organization graphic: ", oid)
		_smoke_check(checks, logo != null, "logo != null")
		_smoke_check(checks, logo != null and logo.get_image().has_mipmaps(), "logo != null and logo.get_image().has_mipmaps()")
	_smoke_check(checks, _organization_texture("ASEAN").get_width() == 1280, "_organization_texture(\"ASEAN\").get_width() == 1280")
	_smoke_check(checks, _organization_texture("ASEAN", true) is AtlasTexture, "_organization_texture(\"ASEAN\", true) is AtlasTexture")
	_map_changed(7)
	_smoke_check(checks, "Yellow 0" in legend.text and relations_picker.visible, "\"Yellow 0\" in legend.text and relations_picker.visible")
	_smoke_check(checks, Commands.execute(state, "opinion JAP CHI -75").contains("updated"), "Commands.execute(state, \"opinion JAP CHI -75\").contains(\"updated\")")
	_smoke_check(checks, is_equal_approx(state.opinion("JAP", "CHI"), -75), "is_equal_approx(state.opinion(\"JAP\", \"CHI\"), -75)")
	for mode: int in [2, 3]:
		_map_changed(mode)
		_smoke_check(checks, map_mode == mode and not legend.text.is_empty(), "map_mode == mode and not legend.text.is_empty()")
	var zoom_event := InputEventMouseButton.new()
	zoom_event.button_index = MOUSE_BUTTON_WHEEL_UP
	zoom_event.pressed = true
	zoom_event.position = view_container.size * 0.5
	for i: int in 40:
		_globe_input(zoom_event)
	_smoke_check(checks, is_equal_approx(distance, 1.015), "is_equal_approx(distance, 1.015)")
	distance = 3.65
	_update_camera_pose()
	_search_changed("pol")
	_smoke_check(checks, "POL" in country_tags, "\"POL\" in country_tags")
	_search_changed("")
	state.paused = true
	var key := InputEventKey.new()
	key.keycode = KEY_SPACE
	key.pressed = true
	Input.parse_input_event(key)
	await get_tree().process_frame
	_smoke_check(checks, not state.paused, "not state.paused")
	key.pressed = false
	Input.parse_input_event(key)
	state.paused = true
	_show_country("FRA", false)
	_focus_country("FRA", false)
	_smoke_check(checks, "EU" in state.memberships("FRA"), "\"EU\" in state.memberships(\"FRA\")")
	_open_organization("ASEAN")
	_smoke_check(checks, state.organizations["ASEAN"]["members"].size() == 10, "state.organizations[\"ASEAN\"][\"members\"].size() == 10")
	_show_country("JAP", false)
	_focus_country("JAP", false)
	state.hour = 59 * 24 + 17
	_smoke_check(checks, state.date_label() == "17:00  ·  29 February 2000", "state.date_label() == \"17:00  \u00b7  29 February 2000\"")
	var path := "user://tests/ui_smoke.json"
	_smoke_check(checks, state.save_game(path, _view_state()), "state.save_game(path, _view_state())")
	state.hour = 100 * 24
	var view := state.load_game(path)
	if view.is_empty():
		printerr("UI smoke load failed: ", state.last_error)
	_smoke_check(checks, not view.is_empty(), "not view.is_empty()")
	_smoke_check(checks, state.hour == 59 * 24 + 17, "state.hour == 59 * 24 + 17")
	_smoke_check(checks, state.selected_country == "JAP", "state.selected_country == \"JAP\"")
	_enter_menu()
	_smoke_check(checks, state.paused and screen == "menu", "state.paused and screen == \"menu\"")
	_load_from(path)
	_smoke_check(checks, screen == "playing" and state.paused and not country_sidebar.visible and state.player_country == "POL", "screen == \"playing\" and state.paused and not country_sidebar.visible and state.player_country == \"POL\"")
	# Loaded map settings and camera are applied to the actual interface.
	_smoke_check(checks, map_mode == int(view["map_mode"]) and is_equal_approx(distance, float(view["distance"])), "map_mode == int(view[\"map_mode\"]) and is_equal_approx(distance, float(view[\"distance\"]))")
	# Named save catalog and real dialogs use a dedicated test folder.
	var catalog_dir := "user://tests/slots"
	var named_path := Catalog.path_for(catalog_dir, "Poland campaign")
	_smoke_check(checks, state.save_game(named_path, _view_state(), "Poland campaign"), "state.save_game(named_path, _view_state(), \"Poland campaign\")")
	var slots := Catalog.scan(catalog_dir)
	_smoke_check(checks, slots.any(func(entry: Dictionary): return entry["path"] == named_path and "17:00" in entry["label"]), "slots.any(func(entry: Dictionary): return entry[\"path\"] == named_path and \"17:00\" in entry[\"label\"])")
	save_directory = catalog_dir
	var test_name := "Named UI campaign"
	var test_path := Catalog.path_for(catalog_dir, test_name)
	if FileAccess.file_exists(test_path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	_save()
	_smoke_check(checks, save_dialog.visible and state.paused, "save_dialog.visible and state.paused")
	save_name_field.text = "../invalid"
	_confirm_save()
	_smoke_check(checks, save_dialog.visible and not save_feedback.text.is_empty(), "save_dialog.visible and not save_feedback.text.is_empty()")
	save_name_field.text = test_name
	_confirm_save()
	_smoke_check(checks, not save_dialog.visible and FileAccess.file_exists(test_path), "not save_dialog.visible and FileAccess.file_exists(test_path)")
	_save()
	save_name_field.text = test_name
	_confirm_save()
	_smoke_check(checks, overwrite_dialog.visible, "overwrite_dialog.visible")
	overwrite_dialog.confirmed.emit()
	overwrite_dialog.hide()
	_smoke_check(checks, FileAccess.file_exists(test_path + ".bak"), "FileAccess.file_exists(test_path + \".bak\")")
	var damaged_path := catalog_dir.path_join("Damaged campaign.json")
	var damaged_file := FileAccess.open(damaged_path, FileAccess.WRITE)
	damaged_file.store_string('{"format":"BunnyWorldSave","payload":"broken","checksum":"wrong"}')
	damaged_file.close()
	_enter_menu()
	_load()
	_smoke_check(checks, load_dialog.visible and load_dialog.get_ok_button().disabled, "load_dialog.visible and load_dialog.get_ok_button().disabled")
	var damaged_index := load_paths.find(damaged_path)
	if damaged_index >= 0:
		load_entries.select(damaged_index)
		load_entries.item_selected.emit(damaged_index)
		var before_hour := state.hour
		_confirm_load()
		_smoke_check(checks, load_dialog.visible and state.hour == before_hour and not load_feedback.text.is_empty(), "load_dialog.visible and state.hour == before_hour and not load_feedback.text.is_empty()")
	var named_index := load_paths.find(test_path)
	_smoke_check(checks, named_index >= 0, "named_index >= 0")
	if named_index >= 0:
		load_entries.select(named_index)
		load_entries.item_selected.emit(named_index)
		_smoke_check(checks, not load_dialog.get_ok_button().disabled, "not load_dialog.get_ok_button().disabled")
		_confirm_load()
		_smoke_check(checks, not load_dialog.visible and screen == "playing" and state.hour == 59 * 24 + 17 and state.paused, "not load_dialog.visible and screen == \"playing\" and state.hour == 59 * 24 + 17 and state.paused")
	save_directory = SAVE_DIRECTORY
	_focus_country("USA", false)
	distance = 1.5
	_update_camera_pose()
	_process(0.1)
	_update_cities()
	var city_markers: Array = city_layer.get("markers")
	_smoke_check(checks, show_regions and city_markers.any(func(m: Dictionary): return m["capital"]), "show_regions and city_markers.any(func(m: Dictionary): return m[\"capital\"])")
	distance = 3.65
	_update_camera_pose()
	_process(0.1)
	_smoke_check(checks, not show_regions and city_layer.get("markers").is_empty(), "not show_regions and city_layer.get(\"markers\").is_empty()")
	rotation_velocity = Vector2(0.3, 0.0)
	var before_rotation := planet.rotation.y
	_process(0.05)
	_smoke_check(checks, planet.rotation.y > before_rotation and rotation_velocity.x < 0.3, "planet.rotation.y > before_rotation and rotation_velocity.x < 0.3")
	rotation_velocity = Vector2.ZERO
	planet.rotation = Vector3(0, deg_to_rad(30), 0)
	distance = 3.65
	_update_camera_pose()
	_show_country("POL", false)
	var ocean_click := InputEventMouseButton.new()
	ocean_click.button_index = MOUSE_BUTTON_LEFT
	ocean_click.pressed = true
	ocean_click.position = Vector2(world_view.size) / 2.0
	_smoke_check(checks, _region_at(ocean_click.position) == 0, "_region_at(ocean_click.position) == 0")
	_globe_input(ocean_click)
	_smoke_check(checks, not control_panel.visible and not inspection_active and state.selected_sea > 0, "not control_panel.visible and not inspection_active and state.selected_sea > 0")
	# Verify every geographic focus target through the actual 3D ray picker.
	for tag: String in state.countries:
		_focus_country(tag, false)
		var focused_id := _region_at(Vector2(world_view.size) / 2.0)
		_smoke_check(checks, state.regions.get(str(focused_id), {}).get("owner") == tag, "state.regions.get(str(focused_id), {}).get(\"owner\") == tag")
	_focus_country("JAP", false)
	# The ray picker must match the actual focused capital pixel.
	var center := Vector2(world_view.size) / 2.0
	var rid := _region_at(center)
	distance = 1.12
	_update_camera_pose()
	_process(0.0)
	var pid := _province_at(center)
	_smoke_check(checks, pid > 0 and int(state.provinces.get(str(pid), {}).get("region", 0)) == rid, "pid > 0 and int(state.provinces.get(str(pid), {}).get(\"region\", 0)) == rid")
	var province_click := InputEventMouseButton.new()
	province_click.button_index = MOUSE_BUTTON_LEFT
	province_click.pressed = true
	province_click.position = center
	_globe_input(province_click)
	_smoke_check(checks, state.selected_province == pid, "state.selected_province == pid")
	_smoke_check(checks, camera_tilt_degrees > 0.0 and camera_tilt_degrees < 38.0, "camera_tilt_degrees > 0.0 and camera_tilt_degrees < 38.0")
	_smoke_check(checks, planet.get_child(0) is MeshInstance3D, "single globe surface exists")
	var saved_distance := distance
	distance = 1.015
	_update_camera_pose()
	_smoke_check(checks, is_equal_approx(camera_tilt_degrees, 38.0), "is_equal_approx(camera_tilt_degrees, 38.0)")
	var anchor_uv := Surface.uv_of(planet.global_transform.basis.inverse() * Vector3.BACK)
	var anchor := Vector3(0, 0, 1.0 + relief_surface.height_at(anchor_uv))
	_smoke_check(checks, camera.position.distance_to(anchor) >= .01499, "camera.position.distance_to(anchor) >= .01499")
	_smoke_check(checks, _region_at(center) == rid, "_region_at(center) == rid")
	distance = 1.5
	_update_camera_pose()
	_smoke_check(checks, is_zero_approx(camera_tilt_degrees), "is_zero_approx(camera_tilt_degrees)")
	distance = saved_distance
	_update_camera_pose()
	_smoke_check(checks, state.regions.has(str(rid)), "state.regions.has(str(rid))")
	_smoke_check(checks, state.regions.get(str(rid), {}).get("owner") == "JAP", "state.regions.get(str(rid), {}).get(\"owner\") == \"JAP\"")
	# Exercise actual cursor placement, clipping and panel/drag suppression.
	_close_panels()
	Input.warp_mouse(view_container.global_position + center)
	await get_tree().process_frame
	await get_tree().process_frame
	_update_map_hover(center)
	_smoke_check(checks, hover_panel.visible and "Japan" in hover_text.text, "hover_panel.visible and \"Japan\" in hover_text.text")
	var edge_point := view_container.size - Vector2(12, 12)
	Input.warp_mouse(view_container.global_position + edge_point)
	await get_tree().process_frame
	await get_tree().process_frame
	_update_map_hover(edge_point)
	_smoke_check(checks, hover_panel.visible and Rect2(Vector2.ZERO, size).encloses(hover_panel.get_rect()), "hover_panel.visible and Rect2(Vector2.ZERO, size).encloses(hover_panel.get_rect())")
	_show_country("JAP", false)
	await get_tree().create_timer(.2).timeout
	var active_panel := control_panel if control_panel.visible else right_panel
	Input.warp_mouse(active_panel.global_position + Vector2(60, 80))
	await get_tree().process_frame
	await get_tree().process_frame
	_position_map_hover()
	_smoke_check(checks, not hover_panel.visible, "not hover_panel.visible")
	_close_panels()
	Input.warp_mouse(view_container.global_position + center)
	await get_tree().process_frame
	await get_tree().process_frame
	_update_map_hover(center)
	_smoke_check(checks, hover_panel.visible, "hover_panel.visible")
	dragging = true
	_process(0.0)
	_smoke_check(checks, not hover_panel.visible, "not hover_panel.visible")
	dragging = false
	var previous_sound_setting := sound_enabled
	_save_sound_setting(false)
	sound_player.stop()
	_play_ui("click")
	_smoke_check(checks, not sound_player.playing and not bool(JSON.parse_string(FileAccess.get_file_as_string("user://interface_settings.json"))["sounds"]), "not sound_player.playing and not bool(JSON.parse_string(FileAccess.get_file_as_string(\"user://interface_settings.json\"))[\"sounds\"])")
	_save_sound_setting(previous_sound_setting)
	# Exercise the actual close-view scenery manager, not just its data budgets.
	planet.rotation = Vector3(deg_to_rad(48.8584), -deg_to_rad(2.2945), 0)
	distance = 1.10
	_update_camera_pose()
	for tick: int in 18: urban_scenery.update_view(camera, distance, true, .3)
	_smoke_check(checks, urban_scenery.visible and urban_scenery.visibility_alpha > 0.0 and urban_scenery.visibility_alpha < 1.0, "urban_scenery.visible and urban_scenery.visibility_alpha > 0.0 and urban_scenery.visibility_alpha < 1.0")
	_smoke_check(checks, urban_scenery.visible_buildings > 0 and urban_scenery.visible_buildings <= Urban.BUILDING_CAP and urban_scenery.active.size() <= Urban.CLUSTER_CAP, "urban_scenery.visible_buildings > 0 and urban_scenery.visible_buildings <= Urban.BUILDING_CAP and urban_scenery.active.size() <= Urban.CLUSTER_CAP")
	_smoke_check(checks, urban_scenery.active_landmarks.has("eiffel"), "urban_scenery.active_landmarks.has(\"eiffel\")")
	for node: MultiMeshInstance3D in urban_scenery.active.values():
		_smoke_check(checks, node.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF, "node.cast_shadow == GeometryInstance3D.SHADOW_CASTING_SETTING_OFF")
		for i: int in node.multimesh.instance_count:
			var transform := node.multimesh.get_instance_transform(i)
			var base := transform.origin - transform.basis.y * .5
			_smoke_check(checks, absf(base.length() - 1.0 - relief_surface.height_at(Surface.uv_of(base))) < .00001, "absf(base.length() - 1.0 - relief_surface.height_at(Surface.uv_of(base))) < .00001")
	distance = 1.025
	_update_camera_pose()
	urban_scenery.update_view(camera, distance, true, .3)
	_smoke_check(checks, is_equal_approx(urban_scenery.visibility_alpha,1.0), "is_equal_approx(urban_scenery.visibility_alpha,1.0)")
	_process(.01)
	_globe_input(province_click)
	var has_population := false
	for node: Node in territory_details.get_children():
		if node is Label and str(node.text).begins_with("Province population:"): has_population = true
	_smoke_check(checks, has_population and state.selected_province > 0, "has_population and state.selected_province > 0")
	distance = 1.18
	_update_camera_pose()
	urban_scenery.update_view(camera, distance, true, .3)
	_smoke_check(checks, not urban_scenery.visible and urban_scenery.active.is_empty() and urban_scenery.active_landmarks.is_empty(), "not urban_scenery.visible and urban_scenery.active.is_empty() and urban_scenery.active_landmarks.is_empty()")
	distance = 1.025
	urban_scenery.update_view(camera, distance, false, .3)
	_smoke_check(checks, not urban_scenery.visible and urban_scenery.visible_buildings == 0, "not urban_scenery.visible and urban_scenery.visible_buildings == 0")
	print("URBAN_UI_CHECKS buildings_cap=2048 clusters_cap=96 fade_threshold=1.18 terrain_attachment_and_population_panel=true")
	var old_scenery := city_scenery_enabled
	var old_sounds := sound_enabled
	_set_city_scenery(false)
	_save_sound_setting(not old_sounds)
	var settings: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("user://interface_settings.json"))
	_smoke_check(checks, not bool(settings["city_scenery"]) and not urban_scenery.visible and urban_scenery.active.is_empty(), "persistent scenery toggle clears geometry")
	_smoke_check(checks, bool(settings["sounds"]) == not old_sounds and int(settings["graphics"])==graphics_setting and int(settings["frame_limit"])==frame_setting,"settings survive independent sound changes")
	_set_city_scenery(true)
	_save_sound_setting(old_sounds)
	var player_before := state.player_country
	state.paused = false
	_open_place_search()
	_smoke_check(checks, place_dialog.visible and state.paused,"search opens and pauses")
	_open_place_search()
	place_input.text = "Tokyo"
	_find_places("Tokyo")
	_smoke_check(checks, not place_matches.is_empty() and place_matches[0]["kind"]=="City" and not place_dialog.get_ok_button().disabled,"search selects city result")
	place_results.item_activated.emit(0)
	await get_tree().create_timer(.7).timeout
	_smoke_check(checks, not place_dialog.visible and not state.paused and state.player_country==player_before,"search resumes and preserves player country")
	_smoke_check(checks, state.selected_country=="JAP" and state.selected_province>0 and _province_at(Vector2(world_view.size)*.5)==state.selected_province,"search camera and province picking agree")
	state.paused = true
	var colosseum: Dictionary = places.find_places("Colosseum")[0]
	_go_to_place(colosseum,false)
	_smoke_check(checks, state.regions[str(_region_at(Vector2(world_view.size)*.5))]["owner"]=="ITA","Colosseum correctly belongs to Italy")
	_smoke_check(checks, _area_number(.44)=="0.44","small province area is readable")
	_smoke_check(checks,state.regions.size()==1355,"updated State geography")
	_set_city_scenery(old_scenery)
	print("REFINEMENT_UI_CHECKS place_search_camera_pause_and_player=true persistent_scenery=true Colosseum_picking=true population_tooltips=true")
	if false in checks:
		printerr("UI_SMOKE_FAIL checks=", checks)
		get_tree().quit(1)
		return
	map_mode = 0
	map_picker.select(0)
	org_picker.visible = false
	state.day = 0
	_rebuild_palette()
	_show_country("JAP", false)
	_update_clock()
	print("UI_SMOKE_PASS countries=", state.countries.size(), " regions=", state.regions.size(), " center_region=", rid)
	if not capture_path.is_empty():
		await _capture()
	else:
		get_tree().quit()
func _build_menu() -> void:
	menu_background = _space_background(self)
	menu_background.name = "MainMenuBackground"
	menu_screen = CenterContainer.new()
	menu_screen.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# Keep the photograph's Earth and lunar horizon visible beside the menu.
	menu_screen.anchor_right = .45
	menu_screen.offset_left = 32
	add_child(menu_screen)
	menu_screen.visibility_changed.connect(func(): menu_background.visible = menu_screen.visible)
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(440, 420)
	panel.add_theme_stylebox_override("panel", _panel_style(Color("102332"), 18))
	menu_screen.add_child(panel)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 22)
	panel.add_child(column)
	var title := _label("BUNNY WORLD", 38, Color("eff8f7"))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(title)
	var subtitle := _label("A new century. A world of possibilities.", 16, Color("63c9b6"))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(subtitle)
	column.add_child(HSeparator.new())
	column.add_child(_button("Start", _start_selection))
	column.add_child(_button("Load", _load))
	column.add_child(_button("Exit", _quit))
	var version := _label(build_version + "  ·  1 January 2000", 12, Color("8da6b7"))
	version.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	column.add_child(version)
	move_child(info_dialog, get_child_count() - 1)

func _enter_menu() -> void:
	screen = "menu"
	state.paused = true
	game_ui.hide()
	menu_screen.show()
	_update_clock()

func _start_selection() -> void:
	state.reset()
	inspect_region = 0
	search.text = ""
	list_filter = ""
	map_mode = 6
	map_picker.select(6)
	org_picker.hide()
	relations_picker.hide()
	screen = "selection"
	menu_screen.hide()
	game_ui.show()
	country_sidebar.show()
	selection_bar.show()
	session_controls.hide()
	title_label.text = "BUNNY WORLD"
	title_label.show()
	stats_row.hide()
	if foundation != null: foundation.toolbar.hide()
	header_flag.hide()
	subtitle_label.show()
	campaign_label.show()
	stats_label.hide()
	_hide_panel(control_panel)
	details = diplomatic_details
	campaign_label.text = "Choose a country on the globe, then press Play"
	_update_country_list()
	_rebuild_palette()
	_show_country(state.selected_country)
	_update_clock()
	_set_status("Select your country  ·  1 January 2000")

func _begin_campaign() -> void:
	if screen != "selection":
		return
	state.player_country = state.selected_country
	_map_changed(6)
	_enter_campaign(false)

func _enter_campaign(start_clock: bool) -> void:
	screen = "playing"
	menu_screen.hide()
	game_ui.show()
	country_sidebar.hide()
	selection_bar.hide()
	session_controls.show()
	campaign_label.text = "Playing as " + str(state.countries[state.player_country]["name"])
	_update_country_bar()
	_hide_panel(control_panel)
	_hide_panel(right_panel)
	inspection_active = false
	_update_selection_shader()
	state.paused = not start_clock
	_update_clock()
	_set_status("Playing as " + str(state.countries[state.player_country]["name"]))

func _update_legend() -> void:
	legend.visible = map_mode not in [0, 6]
	match map_mode:
		0: legend.text = "Political map"
		1: legend.text = "Teal: members of " + active_org + "  ·  Dark blue: non-members"
		2: legend.text = "State population  ·  Dark blue: fewer people  →  Gold: more people\nTotals per state, on a logarithmic color scale"
		4: legend.text = "GDP · $0.1B → $10T · Continuous logarithmic scale\nPale cream → amber → dark brown. Grey: unavailable."
		6: legend.text = "Physical map · Terrain and waterways"
		5: legend.text = "GDP/capita · $0 → $100k · Continuous logarithmic scale\nPale cream → amber → dark brown. Grey: unavailable."
		7: legend.text = ("Others → " if relations_reverse else str(state.countries[state.selected_country]["name"]) + " → ") + (str(state.countries[state.selected_country]["name"]) if relations_reverse else "others") + " · Dark red −200 · Red −100 · Yellow 0 · Green +100 · Dark green +200\nExact values on hover; white marks the selected country."
		3: legend.text = "Blue: Western  ·  Red: Emerging  ·  Gold: Non-Aligned\nGreen: Salafist  ·  Purple: Nationalist  ·  Grey: Unspecified"

func _build_save_dialogs() -> void:
	save_dialog = ConfirmationDialog.new()
	save_dialog.title = "Save campaign"
	save_dialog.ok_button_text = "Save"
	save_dialog.dialog_hide_on_ok = false
	add_child(save_dialog)
	var save_box := VBoxContainer.new()
	save_dialog.add_child(save_box)
	save_box.add_child(_label("Save name", 14))
	save_name_field = LineEdit.new()
	save_name_field.placeholder_text = "Name your campaign"
	save_name_field.max_length = 80
	save_box.add_child(save_name_field)
	save_feedback = _wrapped("", 13)
	save_box.add_child(save_feedback)
	save_entries = ItemList.new()
	save_entries.custom_minimum_size = Vector2(590, 230)
	save_entries.item_selected.connect(func(index: int): save_name_field.text = save_slots[index]["filename"].get_basename())
	save_box.add_child(save_entries)
	save_dialog.confirmed.connect(_confirm_save)
	save_dialog.canceled.connect(_resume_after_dialog)
	save_name_field.text_submitted.connect(func(_value: String): _confirm_save())
	load_dialog = ConfirmationDialog.new()
	load_dialog.title = "Load campaign"
	load_dialog.ok_button_text = "Load"
	load_dialog.dialog_hide_on_ok = false
	add_child(load_dialog)
	var load_box := VBoxContainer.new()
	load_dialog.add_child(load_box)
	load_feedback = _wrapped("", 13)
	load_box.add_child(load_feedback)
	load_entries = ItemList.new()
	load_entries.custom_minimum_size = Vector2(600, 290)
	load_entries.item_selected.connect(func(_index: int): load_dialog.get_ok_button().disabled = false)
	load_box.add_child(load_entries)
	load_dialog.confirmed.connect(_confirm_load)
	load_dialog.canceled.connect(_resume_after_dialog)
	overwrite_dialog = ConfirmationDialog.new()
	overwrite_dialog.title = "Replace saved campaign?"
	overwrite_dialog.ok_button_text = "Replace"
	save_dialog.add_child(overwrite_dialog)
	overwrite_dialog.confirmed.connect(func(): _write_named_save(pending_overwrite_path))

func _pause_for_dialog() -> void:
	rotation_velocity = Vector2.ZERO
	popup_was_paused = state.paused
	state.paused = true
	_update_clock()

func _resume_after_dialog() -> void:
	state.paused = popup_was_paused if screen == "playing" else true
	_update_clock()

func _confirm_save() -> void:
	var name := save_name_field.text.strip_edges()
	if not Catalog.valid_name(name):
		save_feedback.text = "Use 1–80 characters, without path separators or Windows-reserved names."
		return
	var path := Catalog.path_for(save_directory, name)
	if FileAccess.file_exists(path):
		pending_overwrite_path = path
		overwrite_dialog.dialog_text = "Replace ‘" + name + "’? The previous save will be kept as a backup."
		overwrite_dialog.popup_centered(Vector2i(520, 190))
	else:
		_write_named_save(path)

func _write_named_save(path: String) -> void:
	overwrite_dialog.hide()
	var name := save_name_field.text.strip_edges()
	if state.save_game(path, _view_state(), name):
		last_save_name = name
		save_dialog.hide()
		_resume_after_dialog()
		_set_status("Saved ‘" + name + "’  ·  " + state.date_label())
		_play_ui("confirm")
	else:
		save_feedback.text = state.last_error

func _confirm_load() -> void:
	var selection := load_entries.get_selected_items()
	if selection.is_empty():
		load_feedback.text = "Select a save first."
		return
	if _load_from(load_paths[selection[0]], false):
		load_dialog.hide()
	else:
		load_feedback.text = state.last_error

func _placeholder(caption: String) -> void:
	var button := _button(caption + "  ·  Coming later", func(): pass)
	button.disabled = true
	button.tooltip_text = "This action is not available yet."
	details.add_child(button)

func _close_panels() -> void:
	if screen == "playing":
		_preview_state(0)
		active_feature = ""
		_hide_panel(control_panel)
		_hide_panel(territory_panel)
		inspection_active = false
		inspect_region = 0
		state.selected_region = 0
		state.selected_sea = 0
		state.selected_province = 0
		inspect_province = 0
		_update_selection_shader()

func _update_country_bar() -> void:
	if screen != "playing": return
	var c: Dictionary = state.countries[state.player_country]
	title_label.text = c["name"]
	title_label.hide()
	stats_row.show()
	header_flag.texture = flags.resolve(state.player_country, str(c.get("cosmetic", "")), c["outlook"])
	header_flag.show()
	header_flag.tooltip_text = str(c["name"]) + " · Open country control"
	subtitle_label.hide()
	campaign_label.hide()
	stats_label.show()
	var stats: Dictionary = c.get("starting_stats", {})
	var population: int = state.country_metrics(state.player_country)["population"]
	var pp := str(stats["political_power"]) if stats.has("political_power") else "—"
	var stability := "%.0f%%" % (float(stats["stability"]) * 100) if stats.has("stability") else "—"
	var support := "%.0f%%" % (float(stats["war_support"]) * 100) if stats.has("war_support") else "—"
	var per_capita := float(stats.get("gdp_per_capita_usd", 0))
	var gdp := "$%.1fB" % (per_capita * population / 1000000000.0) if per_capita > 0 else "—"
	stats_label.text = "Political power: %s    Stability: %s    War support: %s    Population: %s    GDP: %s    GDP / capita: %s" % [pp, stability, support, _number(population), gdp, "$" + _number(int(per_capita)) if per_capita > 0 else "—"]
	if foundation != null: foundation.update_bar()
	overlay_layout_dirty = true
	stats_label.tooltip_text = "Population follows state ownership. Other values are starting scenario figures. GDP is derived from population × GDP per capita. — means unavailable."

func _build_game_menu() -> void:
	game_menu = AcceptDialog.new()
	game_menu.title = "Game menu"
	game_menu.ok_button_text = "Resume"
	add_child(game_menu)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(340, 385)
	game_menu.add_child(box)
	box.add_theme_constant_override("separation",5)
	box.add_child(_button("Save", func(): game_menu.hide(); _resume_after_dialog(); _save()))
	box.add_child(_button("Load", func(): game_menu.hide(); _resume_after_dialog(); _load()))
	box.add_child(_button("Help", func(): game_menu.hide(); _help()))
	graphics_picker = OptionButton.new()
	for item: String in ["Graphics: Balanced", "Graphics: Light", "Graphics: High"]: graphics_picker.add_item(item)
	graphics_picker.tooltip_text = "Apply terrain texture quality and anti-aliasing immediately."
	graphics_picker.select(graphics_setting)
	graphics_picker.item_selected.connect(_graphics_changed)
	box.add_child(graphics_picker)
	frame_picker = OptionButton.new()
	frame_picker.add_item("Frame limit: 60 FPS")
	frame_picker.add_item("Frame limit: 30 FPS")
	frame_picker.select(frame_setting)
	frame_picker.item_selected.connect(func(index: int): frame_setting = index; Engine.max_fps = 60 if index == 0 else 30; _persist_interface_settings())
	box.add_child(frame_picker)
	scenery_toggle = CheckButton.new()
	scenery_toggle.text = "City buildings and landmarks"
	scenery_toggle.tooltip_text = "Show close-range 3D scenery. City labels and population information remain available."
	scenery_toggle.button_pressed = city_scenery_enabled
	scenery_toggle.toggled.connect(_set_city_scenery)
	box.add_child(scenery_toggle)
	var sounds := CheckButton.new()
	sounds.text = "Interface sounds"
	sounds.button_pressed = sound_enabled
	sounds.toggled.connect(_save_sound_setting)
	box.add_child(sounds)
	box.add_child(_button("Save folder", _open_save_folder))
	box.add_child(_button("Main menu", func(): game_menu.hide(); _enter_menu()))
	box.add_child(_button("Quit", _quit))
	game_menu.confirmed.connect(_resume_after_dialog)
	game_menu.canceled.connect(_resume_after_dialog)

func _open_game_menu() -> void:
	_play_ui("open")
	_pause_for_dialog()
	game_menu.popup_centered(Vector2i(400, 515))

func _update_cities() -> void:
	var key: Array = [planet.global_transform, camera.global_transform, view_container.size, screen]
	if key == last_city_view: return
	last_city_view = key
	var markers: Array[Dictionary] = []
	if distance > 1.65 or screen == "menu":
		city_layer.set("markers", markers)
		city_layer.queue_redraw()
		return
	var occupied: Array[Rect2] = []
	var indices: Array = city_point_index.candidates(planet.global_transform.affine_inverse()*camera.global_position) if city_point_index != null else range(cities.size())
	var transform := planet.global_transform
	var eye := camera.position
	var view_size := view_container.size
	var ratio := view_size/Vector2(world_view.size)
	for index: int in indices:
		var city: Dictionary = cities[index]
		if not city["capital"] and not city.get("state_capital",false) and distance > 1.35: continue
		city_projection_tests += 1
		var p: Vector3 = transform * city["raised_point"]
		if p.dot(eye - p) <= 0 or camera.is_position_behind(p): continue
		var projected := camera.unproject_position(p) * ratio
		if not Rect2(Vector2.ZERO, view_size).has_point(projected): continue
		var box := Rect2(projected - Vector2(4, 12), Vector2(25 + str(city["name"]).length() * 7, 22))
		var overlaps := false
		for other: Rect2 in occupied:
			if box.intersects(other): overlaps = true; break
		if overlaps: continue
		occupied.append(box)
		markers.append({"name": city["name"], "point": projected, "capital": city["capital"], "state_capital":city.get("state_capital",false)})
		if markers.size() >= 70: break
	city_layer.set("markers", markers)
	city_layer.queue_redraw()

func _entity_heading(caption: String, texture: Texture2D, organization: bool = false) -> void:
	var pinned: VBoxContainer = control_heading if details == control_details else diplomatic_heading
	if details.get_child_count() > 0 and details.get_child(0) is Label:
		details.get_child(0).reparent(pinned)
	var row := HBoxContainer.new()
	row.name = "EntityHeading"
	if texture != null:
		var icon := TextureRect.new()
		icon.texture = texture
		icon.custom_minimum_size = Vector2(108, 72) if organization else Vector2(66, 44)
		icon.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS if organization else CanvasItem.TEXTURE_FILTER_LINEAR
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		if organization and _organization_light_background(active_org):
			var frame := PanelContainer.new()
			var style := _panel_style(Color("e6edf1"), 6, Color("718995"))
			for side: String in ["left", "right", "top", "bottom"]: style.set("content_margin_" + side, 6)
			frame.add_theme_stylebox_override("panel", style)
			icon.custom_minimum_size = Vector2(96, 60)
			frame.add_child(icon)
			row.add_child(frame)
		else:
			row.add_child(icon)
	else:
		var badge := _label("◇", 34, Color("63c9b6"))
		badge.custom_minimum_size.x = 44
		row.add_child(badge)
	var title := _wrapped(caption, 24, Color("f0f7f8"))
	title.custom_minimum_size.x = 100
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(title)
	pinned.add_child(row)
	pinned.add_child(HSeparator.new())

func _overlay_panel() -> PanelContainer:
	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", _button_style(Color("102332"), 6))
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	panel.mouse_force_pass_scroll_events = false
	game_ui.add_child(panel)
	return panel

func _configure_overlay_layout() -> void:
	# The globe is the full-window background. Only the actual control boxes catch input.
	view_container.reparent(game_ui)
	game_ui.move_child(view_container, 0)
	view_container.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	top_left_box = VBoxContainer.new()
	top_left_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top_left_box.add_theme_constant_override("separation", 3)
	game_ui.add_child(top_left_box)
	top_left_box.position = Vector2(8, 0)
	command_frame = PanelContainer.new()
	command_frame.name = "CommandBar"
	command_frame.mouse_force_pass_scroll_events = false
	var command_style := _button_style(Color("102332"), 4)
	command_style.content_margin_left = 8; command_style.content_margin_right = 8
	command_style.content_margin_top = 4; command_style.content_margin_bottom = 4
	command_frame.add_theme_stylebox_override("panel", command_style)
	top_left_box.add_child(command_frame)
	var command_row := HBoxContainer.new()
	command_row.add_theme_constant_override("separation", 9)
	command_frame.add_child(command_row)
	header_flag.reparent(command_row)
	header_flag.custom_minimum_size = Vector2(94, 66)
	header_flag.size_flags_vertical = Control.SIZE_EXPAND_FILL
	command_stack = VBoxContainer.new()
	command_stack.add_theme_constant_override("separation", 4)
	command_row.add_child(command_stack)
	stats_row.reparent(command_stack)
	navigation_row.reparent(command_stack)
	navigation_row.get_child(navigation_row.get_child_count()-1).size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	clock_box = _overlay_panel()
	session_controls.reparent(clock_box)
	map_box = _overlay_panel()
	var map_row := map_picker.get_parent()
	map_row.reparent(map_box)
	for child: Node in map_row.get_children():
		if child.get_class() == "Control": child.queue_free()
	selection_box = _overlay_panel()
	country_sidebar.reparent(selection_box)
	selection_box.size = Vector2(250, 530)
	selection_box.position = Vector2(size.x - 258, 112)
	# Discard the original layout containers after moving every live control.
	for child: Node in game_ui.get_children():
		if child is VBoxContainer and child != top_left_box: child.queue_free()
	legend.position = Vector2(12, 112)
	_position_panels()

func _layout_overlay() -> void:
	if clock_box == null: return
	if not overlay_layout_dirty and overlay_size == size and overlay_screen == screen: return
	overlay_layout_dirty = false; overlay_size = size; overlay_screen = screen
	clock_box.reset_size()
	clock_box.position = Vector2(size.x - clock_box.size.x - 8, 0)
	map_box.reset_size()
	map_box.position = Vector2(size.x - map_box.size.x - 8, clock_box.size.y + 3)
	selection_box.visible = screen == "selection"
	selection_box.size.y = maxf(300, size.y - 122)
	selection_box.position = Vector2(size.x - selection_box.size.x - 8, 112)
	var stats_width := 0.0
	for cell: Control in stats_row.get_children(): stats_width += cell.get_combined_minimum_size().x + 3
	var available := maxf(565.0, clock_box.position.x - 8.0 - 94.0 - 32.0)
	stats_row.custom_minimum_size.x = minf(maxf(0, stats_width - 3), available)
	top_left_box.reset_size()

func _panel_target(panel: PanelContainer) -> float:
	return 8.0 if panel == control_panel else view_container.size.x - 378.0

func _territory_width() -> float:
	return clampf(view_container.size.x * .305, 350.0, 440.0)

func _territory_position(collapsed: bool) -> float:
	return _territory_width() if collapsed else 0.0
func _handle_position(collapsed: bool) -> float:
	return view_container.size.x-34.0-(0.0 if collapsed else _territory_width())

func _position_panels(force: bool = true) -> void:
	if view_container == null: return
	_layout_overlay()
	var key: Array = [view_container.size, top_left_box.size if top_left_box != null else Vector2.ZERO, control_panel.visible, right_panel.visible, territory_collapsed, active_feature]
	if not force and key == last_panel_layout and panel_tweens.is_empty() and (territory_tween == null or not territory_tween.is_running()): return
	last_panel_layout = key
	for panel: PanelContainer in [control_panel]:
		if panel == null or not panel.is_inside_tree(): continue
		var available_height := maxf(240, view_container.size.y - 118)
		panel.size = Vector2(minf(600, view_container.size.x - 24), minf(720, available_height)) if active_feature == "Government" else Vector2(370, available_height)
		if panel.visible and not panel_tweens.has(panel): panel.position = Vector2(_panel_target(panel), 110)
	if territory_clip == null: return
	territory_clip.position = Vector2(view_container.size.x-8-_territory_width(),110)
	territory_clip.size = Vector2(_territory_width(), view_container.size.y-118)
	territory_panel.size = territory_clip.size
	for grid: GridContainer in territory_details.find_children("FacilityGrid","GridContainer",true,false):grid.columns=maxi(4,int((_territory_width()-34)/59))
	if territory_tween == null or not territory_tween.is_running():
		territory_panel.position = Vector2(_territory_position(territory_collapsed), 0)
		territory_handle.position = Vector2(_handle_position(territory_collapsed), territory_clip.position.y + 12)
	_update_territory_handle()

func _update_territory_handle() -> void:
	if territory_handle == null: return
	territory_handle.text = ("›" if territory_collapsed else "‹") if control_panel.visible else ("‹" if territory_collapsed else "›")
	territory_handle.tooltip_text = ("Show" if territory_collapsed else "Hide") + " State / province information"

func _animate_territory() -> void:
	if territory_tween != null: territory_tween.kill()
	territory_tween = create_tween().set_parallel(true)
	territory_tween.tween_property(territory_panel, "position:x", _territory_position(territory_collapsed), .2).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	territory_tween.tween_property(territory_handle, "position:x", _handle_position(territory_collapsed), .2).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	_update_territory_handle()

func _toggle_territory() -> void:
	if not territory_handle.visible: return
	_preview_state(0)
	territory_collapsed = not territory_collapsed
	_animate_territory()

func _reveal_panel(panel: PanelContainer) -> void:
	if panel == null: return
	if panel == territory_panel:
		var opening := not territory_clip.visible
		territory_clip.show()
		territory_handle.show()
		territory_panel.show()
		_position_panels()
		if opening and not territory_collapsed:
			territory_panel.position.x = _territory_position(true)
			territory_handle.position.x = _handle_position(true)
			_animate_territory()
		return
	if panel.visible: return
	if panel_tweens.has(panel): panel_tweens[panel].kill(); panel_tweens.erase(panel)
	panel.show()
	panel.modulate.a = 0
	panel.position = Vector2(_panel_target(panel) + (-370 if panel == control_panel else 370), 110)
	var tween := create_tween().set_parallel(true)
	panel_tweens[panel] = tween
	tween.tween_property(panel, "position:x", _panel_target(panel), .16).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_property(panel, "modulate:a", 1.0, .12)
	tween.finished.connect(func(): panel_tweens.erase(panel); _position_panels())

func _hide_panel(panel: PanelContainer) -> void:
	if panel == null: return
	if panel == territory_panel: _preview_state(0)
	if panel_tweens.has(panel): panel_tweens[panel].kill(); panel_tweens.erase(panel)
	panel.hide()
	if foundation != null: foundation.refresh_active_section()
	if panel == territory_panel:
		if territory_tween != null: territory_tween.kill()
		if territory_clip != null: territory_clip.hide()
		if territory_handle != null: territory_handle.hide()
	_position_panels()

func _build_console() -> void:
	console = AcceptDialog.new()
	console.title = "Developer console"
	console.ok_button_text = "Close"
	add_child(console)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(700, 380)
	console.add_child(box)
	console_log = RichTextLabel.new()
	console_log.custom_minimum_size = Vector2(700, 320)
	console_log.scroll_following = true
	console_log.text = "Type help for commands. Country tags are case-insensitive.\n"
	box.add_child(console_log)
	console_input = LineEdit.new()
	console_input.placeholder_text = "tag jap"
	box.add_child(console_input)
	console_input.text_submitted.connect(_run_command)
	console_input.gui_input.connect(func(event: InputEvent):
		if event is InputEventKey and event.pressed and event.keycode == KEY_QUOTELEFT:
			_toggle_console()
			console_input.accept_event())
	console.confirmed.connect(_resume_after_dialog)
	console.canceled.connect(_resume_after_dialog)

func _toggle_console() -> void:
	if screen != "playing": return
	if console.visible:
		console.hide()
		_resume_after_dialog()
	else:
		_pause_for_dialog()
		console.popup_centered(Vector2i(760, 460))
		console_input.grab_focus()

func _run_command(line: String) -> void:
	var args := line.strip_edges().split(" ", false)
	if not args.is_empty() and args[0].to_lower() == "perf":
		var reply := "Use perf start [120–3600 frames], perf stop, perf status, perf continuous or perf auto."
		if args.size() in [2,3] and args[1] == "start":
			if args.size() == 2 or args[2].is_valid_int(): reply = map_diagnostics.start(int(args[2]) if args.size() == 3 else 600)
		elif args.size() == 2 and args[1] in ["continuous", "auto"]:
			map_frame_policy.force_continuous = args[1] == "continuous"
			map_frame_policy.invalidate()
			reply = "Map redraw: " + ("every application frame" if map_frame_policy.force_continuous else "automatic; 10 Hz when stationary")
		elif args.size() == 2 and args[1] == "stop": reply = map_diagnostics.finish(self)
		elif args.size() == 2 and args[1] == "status": reply = JSON.stringify(map_diagnostics.adapter()) + "\nFrames remaining: %d\nLast report: %s" % [map_diagnostics.remaining, map_diagnostics.last_path]
		console_log.append_text("> " + line + "\n" + reply + "\n")
		console_input.clear()
		return
	console_log.append_text("> " + line + "\n" + Commands.execute(state, line) + "\n")
	console_input.clear()
	inspect_region = 0
	_rebuild_palette()
	_update_country_bar()
	_show_country(state.selected_country, false)

func _smoke_check(checks: Array[bool], condition: bool, label: String) -> void:
	if not condition: printerr("SMOKE_CHECK_FAILED: ", label)
	checks.append(condition)

func _build_place_search() -> void:
	place_dialog = AcceptDialog.new()
	place_dialog.title = "Find a place"
	place_dialog.ok_button_text = "Go to"
	place_dialog.min_size = Vector2i(480, 360)
	add_child(place_dialog)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(540, 350)
	place_dialog.add_child(box)
	place_input = LineEdit.new()
	place_input.placeholder_text = "City, state, country or landmark…"
	place_input.text_changed.connect(_find_places)
	place_input.text_submitted.connect(func(_value: String): _activate_place_selection())
	box.add_child(place_input)
	place_results = ItemList.new()
	place_results.custom_minimum_size = Vector2(540, 280)
	place_results.size_flags_vertical = Control.SIZE_EXPAND_FILL
	place_results.item_activated.connect(func(_index: int): _activate_place_selection())
	box.add_child(place_results)
	place_hint = _label("Type a name, then press Enter or choose Go to.", 12)
	box.add_child(place_hint)
	place_dialog.confirmed.connect(_activate_place_selection)
	place_dialog.canceled.connect(_resume_after_dialog)

func _open_place_search() -> void:
	if screen == "menu" or place_dialog == null: return
	if place_dialog.visible:
		place_input.grab_focus()
		place_input.select_all()
		return
	_pause_for_dialog()
	hover_panel.hide()
	place_dialog.popup_centered(Vector2i(590, 440))
	_find_places(place_input.text)
	place_input.grab_focus()
	place_input.select_all()

func _find_places(query: String) -> void:
	place_matches = places.find_places(query)
	place_results.clear()
	for record: Dictionary in place_matches:
		var country_name := str(record["country_name"])
		var sid := int(record["state"])
		if sid>0 and state.regions.has(str(sid)):
			country_name = str(state.countries.get(state.regions[str(sid)]["owner"],{}).get("name",country_name))
		var label := "%s · %s — %s" % [record["kind"],record["name"],country_name]
		var index := place_results.add_item(label)
		place_results.set_item_tooltip(index,label)
	place_dialog.get_ok_button().disabled = place_matches.is_empty()
	if not place_matches.is_empty(): place_results.select(0)
	place_hint.text = "Type a name, then press Enter or choose Go to." if query.strip_edges().is_empty() else ("No matching places." if place_matches.is_empty() else ("1 result" if place_matches.size()==1 else "%d results" % place_matches.size()) + " · Double-click a place or press Enter")

func _activate_place_selection() -> void:
	if place_matches.is_empty(): return
	var selected := place_results.get_selected_items()
	var index := int(selected[0]) if not selected.is_empty() else 0
	if index<0 or index>=place_matches.size(): return
	place_dialog.hide()
	_resume_after_dialog()
	_go_to_place(place_matches[index])

func _go_to_place(record: Dictionary, animated: bool = true) -> void:
	var sid := int(record["state"])
	var pid := int(record["province"])
	var owner := str(record["country"])
	if sid>0 and state.regions.has(str(sid)): owner = str(state.regions[str(sid)]["owner"])
	inspect_region = sid
	inspect_province = pid
	inspection_active = true
	var target_distance := 2.2 if record["kind"]=="Country" else (1.14 if record["kind"]=="State" else (1.025 if record["kind"]=="Landmark" else 1.06))
	if owner=="HLS": target_distance=1.025
	var uv: Vector2 = record["uv"]
	var target := Vector3(clampf((.5-uv.y)*PI,-1.5,1.5),-(uv.x-.5)*TAU,0)
	rotation_velocity = Vector2.ZERO
	if focus_tween != null: focus_tween.kill()
	target.y = planet.rotation.y + wrapf(target.y-planet.rotation.y,-PI,PI)
	if animated:
		focus_tween = create_tween().set_parallel(true)
		focus_tween.tween_property(planet,"rotation",target,.55).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		focus_tween.tween_property(self,"distance",target_distance,.55).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
		focus_tween.finished.connect(func(): _show_country(owner,false))
	else:
		planet.rotation = target
		distance = target_distance
		_update_camera_pose()
		show_regions = distance<1.65
	_show_country(owner,false)
	_set_status("%s · %s" % [record["kind"],record["name"]])

func _area_number(area: float) -> String:
	return "%.2f" % area if area<10.0 else _number(int(round(area)))

func _menu_photo_texture() -> Texture2D:
	if menu_photo != null: return menu_photo
	var path := "res://assets/ui/menu_background.jpg"
	# Source patches can arrive before the editor refreshes its import cache.
	# Decode the shipped JPEG directly; exports retain an imported fallback.
	if FileAccess.file_exists(path):
		var photo := Image.new()
		if photo.load_jpg_from_buffer(FileAccess.get_file_as_bytes(path)) == OK:
			menu_photo = ImageTexture.create_from_image(photo)
	if menu_photo == null and ResourceLoader.exists(path): menu_photo = load(path)
	if menu_photo == null: push_error("Loading/menu photograph is missing: " + path)
	return menu_photo

func _space_background(parent: Control) -> TextureRect:
	var background := TextureRect.new()
	background.texture = _menu_photo_texture()
	background.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	background.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	parent.add_child(background)
	return background

func _show_feature(caption: String) -> void:
	if screen != "playing": return
	if active_feature == caption and control_panel.visible:
		active_feature = ""
		_hide_panel(control_panel)
		return
	details = control_details
	_clear_details()
	active_feature = caption
	var heading := HBoxContainer.new()
	var title := _label(caption, 23, Color("f0eee2"))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	heading.add_child(title)
	control_heading.add_child(heading)
	if caption == "Government":
		var tag: String = state.player_country
		var country := _label(str(state.countries[tag]["name"]), 14, Color("93a8aa"))
		control_heading.add_child(country)
		var politics := preload("res://scripts/political_panel.gd").new()
		politics.configure(state, tag, _update_country_bar)
		control_details.add_child(politics)
	_reveal_panel(control_panel)
	_position_panels()
	foundation.refresh_active_section()

func _build_loading_screen() -> void:
	loading_overlay = ColorRect.new()
	loading_overlay.color = Color("07151f")
	loading_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	loading_overlay.z_index = 100
	add_child(loading_overlay)
	_space_background(loading_overlay)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	loading_overlay.add_child(center)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(480,0)
	box.add_theme_constant_override("separation",18)
	center.add_child(box)
	var title := Label.new()
	title.text = "Bunny World · " + build_version
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size",28)
	box.add_child(title)
	loading_caption = Label.new()
	loading_caption.text = "Loading world"
	loading_caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(loading_caption)
	loading_progress = ProgressBar.new()
	loading_progress.custom_minimum_size.y = 22
	box.add_child(loading_progress)

func _loading_stage(value: float, caption: String) -> void:
	loading_progress.value = value
	loading_caption.text = caption
	print("STARTUP_PROGRESS ",int(value)," ",caption)

func _water_passage_at(uv: Vector2) -> int:
	var point := Vector2(uv.x*360.0-180.0,90.0-uv.y*180.0)
	for passage: Dictionary in water_passages:
		var coordinates: Array = passage["coordinates"]
		var first: Array = coordinates[0]
		var last: Array = coordinates[-1]
		if point.x<minf(float(first[0]),float(last[0]))-.4 or point.x>maxf(float(first[0]),float(last[0]))+.4 or point.y<minf(float(first[1]),float(last[1]))-.4 or point.y>maxf(float(first[1]),float(last[1]))+.4: continue
		var metric := Vector2(cos(deg_to_rad(point.y))*111.195,111.195)
		for i: int in coordinates.size()-1:
			var a := Vector2(float(coordinates[i][0]),float(coordinates[i][1]))
			var b := Vector2(float(coordinates[i+1][0]),float(coordinates[i+1][1]))
			var delta := (b-a)*metric
			var q := (point-a)*metric
			var t := clampf(q.dot(delta)/maxf(delta.length_squared(),.000001),0,1)
			if (q-delta*t).length()<float(passage["display_width_km"])*.5: return int(passage["ends"][0])
	return 0

func _unify_country_panel() -> void:
	view_container.remove_child(right_panel);right_panel.queue_free();right_panel=control_panel;diplomatic_heading=control_heading;diplomatic_details=control_details;details=control_details;control_panel.name="CountryInspector"
	control_details.size_flags_horizontal = Control.SIZE_EXPAND_FILL

func _focus_state_capital(sid: int) -> void:
	var r: Dictionary=state.regions[str(sid)]
	_go_to_place({"state":sid,"province":int(r["capital_province"]),"country":r["owner"],"kind":"City","name":r["state_capital"],"uv":Vector2(r["capital_uv"][0],r["capital_uv"][1])},true)

# This function only schedules viewport draws. Simulation above always runs,
# including when the viewport is disabled or the other hemisphere is hidden.
func _update_map_rendering(delta: float) -> void:
	if world_view == null or camera == null or planet == null: return
	var key: Array = [map_frame_policy.revision, planet.global_transform, camera.global_transform, world_view.size, camera.fov, hover_owner, hover_blend, dragging, map_mode, active_org, inspection_active, state.selected_country, state.selected_region, state.selected_province, state.selected_sea, screen, country_labels_enabled, city_scenery_enabled, graphics_setting]
	if country_label_layer != null: key.append(country_label_layer.visibility_passes)
	if urban_scenery != null: key.append_array([urban_scenery.visible, urban_scenery.visibility_alpha, urban_scenery.visible_buildings, urban_scenery.visibility_passes])
	var draw: bool = map_frame_policy.request_frame(key, delta)
	world_view.render_target_update_mode = SubViewport.UPDATE_ONCE if draw else SubViewport.UPDATE_DISABLED
	var report: String = map_diagnostics.capture(self, draw)
	if not report.is_empty():
		print(report)
		_set_status(report)

func _graphics_changed(index: int) -> void:
	graphics_setting = clampi(index, 0, 2)
	world_view.msaa_3d = [Viewport.MSAA_2X, Viewport.MSAA_DISABLED, Viewport.MSAA_4X][graphics_setting]
	if resident_terrain != null: resident_terrain.set_light(planet_material, graphics_setting == 1)
	map_frame_policy.invalidate()
	_persist_interface_settings()

func _queue_map_hover(position: Vector2) -> void:
	hover_requests += 1
	pending_hover_position = position
	pending_hover = true

func _flush_map_hover() -> void:
	if not pending_hover: return
	pending_hover = false
	if dragging or screen == "menu" or console != null and console.visible or game_menu != null and game_menu.visible or save_dialog != null and save_dialog.visible or load_dialog != null and load_dialog.visible or overwrite_dialog != null and overwrite_dialog.visible or foundation != null and foundation.modals_visible(): return
	if not Rect2(Vector2.ZERO,view_container.size).has_point(pending_hover_position) or _ui_blocks_globe(pending_hover_position): return
	_update_map_hover(pending_hover_position)

func _select_planet_shader() -> void:
	var target: Shader = physical_shader if map_mode == 6 else political_shader
	if target == null or planet_material == null or planet_material.shader == target: return
	# Shared geography/palette/selection uniforms survive mode changes. No
	# texture decoding, uploading or mesh replacement occurs here.
	var parameters: Dictionary = {}
	for parameter: Dictionary in planet_material.shader.get_shader_uniform_list():
		parameters[parameter["name"]] = planet_material.get_shader_parameter(parameter["name"])
	planet_material.shader = target
	for key: String in parameters: planet_material.set_shader_parameter(key,parameters[key])
