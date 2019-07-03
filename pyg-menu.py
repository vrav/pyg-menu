import os
import sys
import json
import time

import pygame

from Xlib import display
from screeninfo import get_monitors

default_settings = {
  "font-file":"Nunito-Regular.ttf",
  "font-size":18,
  "outer-padding":10,
  "line-padding":5,
  "bg-color":[48,48,48],
  "highlight-color":[85, 85, 85],
  "text-color":[255,255,255]
}

def cur_ms():
    return int(round(time.time() * 1000))

def el_ms():
    return cur_ms() - start_time

start_time = cur_ms()
script_path = os.path.dirname(os.path.realpath(__file__))

def load_json(fname):
    with open(fname, 'r') as f:
        return json.loads(f.read())

def read_argv():
    settings = None
    items = None
    
    current_arg = ""
    for arg in sys.argv:
        if arg.startswith("-"):
            current_arg = arg.strip("-")
        elif current_arg == "s" or current_arg == "settings":
            if os.path.exists(arg):
                settings = load_json(arg)
            else:
                settings_path = os.path.join(script_path, arg)
                if os.path.exists(settings_path):
                    settings = load_json(settings_path)
        elif current_arg == "m" or current_arg == "menu":
            if os.path.exists(arg):
                items = load_json(arg)
            else:
                menu_path = os.path.join(script_path, arg)
                if os.path.exists(menu_path):
                    items = load_json(menu_path)
    
    return (settings, items)

(settings, items) = read_argv()
if not settings:
    print("No settings file passed. Use -s file.json to pass a settings file.")
    base_settings_path = os.path.join(script_path, "settings.json")
    if os.path.exists(base_settings_path):
        print("Loading base settings file: %s"%base_settings_path)
        settings = load_json(base_settings_path)
    else:
        print("Using default settings.")
        settings = default_settings
if not items:
    print("No menu items file passed. Use -m file.json to pass a menu items file.")
    base_menu_path = os.path.join(script_path, "menu-base.json")
    if os.path.exists(base_menu_path):
        print("Loading base menu in script path: %s"%base_menu_path)
        items = load_json(base_menu_path)
    else:
        print("No menu file found. Exiting.")
        sys.exit()

for setting in default_settings:
    if setting not in settings:
        settings[setting] = default_settings[setting]

def prerender_menu_text():
    for item in items:
        text = item["text"] if "text" in item else item["command"]
        item["texture"] = font.render(text, True, settings["text-color"])
        size = item["texture"].get_size()
        item["size"] = [size[0], size[1]]
        item["size"][1] += settings["line-padding"] * 2
    
    offs = settings["outer-padding"]
    for item in items:
        item["pos"] = (0, 0 + offs)
        offs += item["size"][1]

def render_menu_items():
    pad = settings["outer-padding"]
    offs = pad
    for item in items:
        screen.blit(item["texture"], (pad, 0 + offs + settings["line-padding"]))
        offs += item["size"][1]

def calc_menu_size():
    pad = settings["outer-padding"]
    
    x = 0
    y = pad + pad
    for item in items:
        if item["size"][0] > x:
            x = item["size"][0]
        y += item["size"][1]
    x += pad + pad
    
    return (x, y)

def get_hover_item(y):
    for item in items:
        if y > item["pos"][1] and y < item["pos"][1] + item["size"][1]:
            return item
    return None

# figure out which monitor the cursor is in and position the window accordingly
xlib_screen = display.Display().screen()
pointer_data = xlib_screen.root.query_pointer()._data
pointer_pos = (pointer_data["root_x"], pointer_data["root_y"])

monitors = get_monitors()
current_monitor = None
for m in monitors:
    if pointer_pos[0] > m.x and pointer_pos[1] > m.y and pointer_pos[0] < m.x+m.width and pointer_pos[1] < m.y+m.height:
        current_monitor = m

if not current_monitor:
    if monitors:
        print("Couldn't find current monitor. Using first found.")
        current_monitor = monitors[0]
    else:
        print("Couldn't find any monitors. Exiting.")
        sys.exit()

pygame.font.init()

font = None
if os.path.exists(settings["font-file"]):
    # full path in settings var
    font = pygame.font.Font(settings["font-file"], settings["font-size"])
else:
    # try to find the font in the script directory
    font_file = os.path.join(script_path, settings["font-file"])
    if os.path.exists(font_file):
        font = pygame.font.Font(font_file, settings["font-size"])
    else:
        # go with None, this is slower but works
        font = pygame.font.Font(None, settings["font-size"])
if not font:
    print("Couldn't initialize font. Exiting.")
    sys.exit()

prerender_menu_text()
window_size = calc_menu_size()
for item in items:
    item["size"][0] = window_size[0]

rel_pointer_pos = (
    pointer_pos[0] - current_monitor.x,
    pointer_pos[1] - current_monitor.y
)

flip_up = False
flip_left = False

if rel_pointer_pos[0] > current_monitor.width - window_size[0]:
    flip_left = True

if rel_pointer_pos[1] > current_monitor.height - window_size[1]:
    flip_up = True

left_adj = settings["outer-padding"] if flip_left else -settings["outer-padding"]
up_adj = settings["outer-padding"] if flip_up else -settings["outer-padding"]

window_pos = (
    pointer_pos[0] - (window_size[0] if flip_left else 0) + left_adj,
    pointer_pos[1] - (window_size[1] if flip_up else 0) + up_adj
)

os.environ['SDL_VIDEO_WINDOW_POS'] = str(window_pos[0]) + "," + str(window_pos[1])

pygame.display.init()
screen = pygame.display.set_mode(window_size, pygame.NOFRAME)
pygame.display.set_caption('pyg-menu')
mouse_pos = pygame.mouse.get_pos()
hover_item = get_hover_item(mouse_pos[1])
prev_hover_item = hover_item

def render_highlight(item):
    pos = item["pos"]
    size = item["size"]
    pygame.draw.rect(screen, settings["highlight-color"],
        pygame.Rect(pos[0], pos[1], size[0], size[1])
    )

def render_window():
    screen.fill(settings["bg-color"])
    if hover_item:
        render_highlight(hover_item)
    render_menu_items()
    pygame.display.flip()

render_window()
running = True
while running:    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        elif event.type == pygame.ACTIVEEVENT and event.gain == 0:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            hover_item = get_hover_item(mouse_pos[1])
            if hover_item != prev_hover_item:
                render_window()
                prev_hover_item = hover_item
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pressed = pygame.mouse.get_pressed()
            if 1 in pressed:
                if hover_item and "command" in hover_item:
                    command = hover_item["command"]
                    if not command.endswith("&"):
                        command += " &"
                    os.system(command)
                    running = False

pygame.display.quit()
pygame.quit()
sys.exit()
