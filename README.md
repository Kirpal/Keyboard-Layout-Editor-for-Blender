# Keyboard-Layout-Editor-for-Blender
Allows you to import keyboard layouts into blender and have them render in 3d
####To-Do
- [x] Add support for ISO enter
- [x] Add key labels
- [ ] Add more key profiles (DSA and DCS are done)
- [ ] Add support for fonts and other CSS styles
- [ ] Add legend alignment and front legends


##How to install Addon:
1. Download zip
2. Open Blender
3. Go to File>User Preferences (Ctrl + Alt + U)
4. Select the "Add-ons" tab.
5. Click “Install from File...” at the bottom of the panel
6. Select the zip archive that you downloaded and click “Install from File…” at the top right
7. Check the checkbox next to “Import-Export: Import: KLE Raw JSON format (.json)”
8. Click “Save User Settings” and close the preferences window
9. Now the addon is ready to use

##How to use Addon:
1. Open Blender
2. Go to File>Import>KLE Raw Data (.json)
3. Select the “keyboard-layout.json” that you downloaded from [Keyboard Layout Editor](http://keyboard-layout-editor.com) and click “Import KLE Raw JSON” at the top right
4. All Done!

##How to add LEDs:
+ Add the following line to the object at the beginning (the one with "backcolor" in it):

    `"led" : [RED, GREEN, BLUE, BRIGHTNESS]` *(you may need to add a comma to the line above)*
    + RED, GREEN, and BLUE are out of 255, and BRIGHTNESS is from 0 to 1




##Examples:

|Render|Layout|
|---------|---------|
|[Imgur](http://i.imgur.com/oouyHOU.png)|[Layout](http://www.keyboard-layout-editor.com/#/gists/92d9daa6db42bb8f39dadec3ef0e299b)|
|[Imgur](http://i.imgur.com/y5Uzhqd.png)|[Layout](http://www.keyboard-layout-editor.com/#/gists/49b89881ec3ff9e048d0ad05d83e1b46)|
|[Imgur](http://i.imgur.com/sUVdJex.png)|[Layout](http://www.keyboard-layout-editor.com/#/gists/6861d5d0070a788ad4f9d57f0c0fb9af)|
|[Imgur](http://i.imgur.com/GiPgGKe.png)|[Layout](http://www.keyboard-layout-editor.com/#/gists/10fab2ecc41b32e92e7331c54f943d73)|
|[Imgur](http://i.imgur.com/8lL7dAR.png)|[Layout](http://www.keyboard-layout-editor.com/#/gists/38f7920dbbbc144d1a87692f18edc8d8)|
|[Imgur](http://i.imgur.com/7KKlx9L.png)|[Layout](http://www.keyboard-layout-editor.com/#/gists/53767e112a7bb65e3b7df17c4301030f)|
