# Keyboard-Layout-Editor-for-Blender
Allows you to import keyboard layouts into blender and render them in 3d

### Examples:

![Example 1](examples/1.jpg)

<sup>Courtesy of [/u/jacopods](https://reddit.com/u/jacopods)</sup>

&nbsp;

![Example 2](examples/2.jpg)

<sup>Courtesy of [/u/zzubnik](https://reddit.com/u/zzubnik)</sup>

&nbsp;

![Example 3](examples/3.jpg)

<sup>Courtesy of [/u/zzubnik](https://reddit.com/u/zzubnik)</sup>

&nbsp;

![Example 4](examples/4.jpg)

<sup>Courtesy of [@kirpal](https://github.com/kirpal)</sup>

*Please open a pull request if you'd like to add more examples*

### How to install Addon:
1. Download the zip ([releases](https://github.com/kirpal/keyboard-layout-editor-for-blender/releases))
2. Open Blender
3. Go to *Edit > Preferences*
4. Select the "Add-ons" tab on the left.
5. Click `Install...` in the top right corner
6. Select the zip archive that you downloaded and click `Install Add-on`
7. Check the checkbox next to `Import-Export: Import: KLE Raw JSON format (.json)`
8. Cose the preferences window. It should auto-save, but you may have to save preferences manually if auto-save is off.
9. Now the addon is ready to use

### How to use Addon:
1. Open Blender
2. Go to *File > Import > KLE Raw Data (.json)*
3. Select the json file that you downloaded from [Keyboard Layout Editor](http://keyboard-layout-editor.com) and click `Import KLE Raw JSON`
4. All Done!

### How to add LEDs:
+ Add the following lines to the keyboard "Notes" section

    ```
    led_color: #RRGGBB
    led_brightness: 1
    ```
    + Where `led_brightness` is any number from 0 to 1 and `led_color` is a hex color

+ To make the keycap legends backlit, make the legend color the same as the LED color.

### Blender scene file
A basic scene for blender can be found in [this gist](https://gist.github.com/wilderjds/5e43cc04f202fe71c51f69e4775a3c4e).  Open the scene in blender before importing. Please note that lighting, camera and render setup will most probably require some tweaking to fit with your specific layout.

### Special Thanks To:

[@zslane](https://deskthority.net/zslane-u8694/) on Deskthority for the SA models

[@Kaporkle](https://geekhack.org/index.php?PHPSESSID=mhqa0bak1to87brcdbp6ch0timqstntl&action=profile;u=20953) on Geekhack for the DSA models

[@wilderjds](https://github.com/wilderjds) for implementing SA support
