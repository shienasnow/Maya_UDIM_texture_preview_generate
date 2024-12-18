import maya.cmds as cmds
import maya.mel as mel
import sys
import os


def addScriptPath():
    file_path = cmds.file(q=True, sceneName=True)
    script_path = os.path.dirname(file_path)
    if script_path not in sys.path:
        sys.path.append(script_path)

def createCustomShelf():
    shelf_name = 'TextureGenerator'

    # Get all shelf tabs
    gShelfTopLevel = mel.eval('$tmp = $gShelfTopLevel')
    
    # If you have an existing CustomTools shelf, delete it completely
    if cmds.shelfLayout(shelf_name, exists=True):
        # Delete all buttons on the shelf
        existing_buttons = cmds.shelfLayout(shelf_name, q=True, childArray=True) or []
        for btn in existing_buttons:
            if cmds.objExists(btn):
                cmds.deleteUI(btn)
    else:
        # If there is no shelf, create a new one
        mel.eval('addNewShelfTab "%s"' % shelf_name)
    
    # Check the button already exists
    shelf_buttons = cmds.shelfLayout(shelf_name, q=True, childArray=True) or []
    button_exists = False
    for btn in shelf_buttons:
        if cmds.shelfButton(btn, q=True, label=True) == 'Generate Preview':
            button_exists = True
            break
    
    # Create a new button only when there is no button
    if not button_exists:
        button_command = '''
import generate_preview_by_grp
generate_preview_by_grp.update_selected_group_textures()
'''
        cmds.shelfButton(
            parent=shelf_name,
            label='Generate Preview',
            image='commandButton.png',
            command=button_command,
            sourceType='python',
            width=32,
            height=32
        )

def initializePlugin(*args):
    addScriptPath()
    createCustomShelf()

# Set Maya UI to run after it is loaded
cmds.evalDeferred(initializePlugin)
