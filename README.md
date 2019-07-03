# pyg-menu.py
Opens a simple visual shortcut menu, configured with JSON. Designed to be portable and hackable.

![img1](https://i.imgur.com/PNFOV6u.jpg)

This is a quick and dirty menu system I created in an evening because I wanted a menu when right-clicking i3bar on my linux install. Note, this only works on linux (and possibly OSX running X11, if Xlib does the same things there).

## Prerequisites
Before you can run the script, you need a few things.

First, install python 3 and pip with your package manager. Then,
```
pip install pygame
pip install Xlib
pip install screeninfo
```
Finally, edit menu-base.json to suit your needs.

## Running the script
```
cd pyg-menu
python ./pyg-menu.py
```
Simply passing the script to python will try to load the menu-base.json file in the script directory. If you want to pass a different menu file,
```
python ./pyg-menu.py -m /path/to/menu-file.json
```
If you want to pass in a different settings file as well,
```
python ./pyg-menu.py -s /path/to/settings-file.json -m /path/to/menu-file.json
```
Excluding the path and simply passing filenames will search the script directory.

Pressing escape or moving the cursor out of the menu will exit the menu.

## Settings
```
{
  "font-file":"Nunito-Regular.ttf",
  "font-size":18,
  "outer-padding":10,
  "line-padding":5,
  "bg-color":[48,48,48],
  "highlight-color":[85, 85, 85],
  "text-color":[255,255,255]
}
```
The font-file can be a full path or simply a filename in the script directory. If not found, pygame will use None, which still works, but is somewhat slower on startup.

Outer padding surrounds the entire menu window, and the window is positioned so the cursor is inside it. Line padding adds extra padding to the top and bottom of menu items. Measurements are in pixels for both padding values.

## Menu files
As an example, here's my base menu.
```
[
  {
    "text":"workspaces",
    "command":"python /path/to/pyg-menu.py -m menu-workspace.json"
  },
  {
    "text":"apps",
    "command":"python /path/to/pyg-menu.py -m menu-apps.json"
  },
  {
    "text":"xeyes!",
    "command":"xeyes"
  }
]
```
The JSON consists of a list of dicts containing two keys: text and command, with text being optional. If left out, menu item text will be the command value. Note, command fields have " &" added onto them by the script, so the menu can exit after the command launches.

## Using with i3
I made pyg-menu.py to be used with i3, notably when right-clicking the bar it provides. To enable this, add a command like this to your bar block in your i3 config file:
```
bar {
  bindsym button3 exec --no-startup-id "python /path/to/pyg-menu.py -m menu-base.json"
}
```

## License
The code for the script itself is released under MIT license. The libraries it uses and the font license may have different licenses. Consider this accordingly.
