import os

import maya.mel as mel
import maya.cmds as cmds
from PySide2.QtWidgets import QMessageBox
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance


def get_maya_main_window():
    """
    Maya Main Window Pointer Returns
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QMessageBox)


def show_warning_dialog(message):
    """
    Display alert message dialog
    """
    maya_window = get_maya_main_window()
    QMessageBox.warning(maya_window, "경고", message)


def set_working_diretory():
    """
    Change the working directory to the directory of the thin file.
    """
    scene_path = cmds.file(query=True, sceneName=True)

    if scene_path:
        scene_dir = os.path.dirname(scene_path)

        # Verify that the directory exists
        if os.path.isdir(scene_dir):
            os.chdir(scene_dir)
            print(f"\nChanged working directory : {scene_dir}")
        else:
            print(f"\nFailed to change working directory. directory does not exist : {scene_dir}")
    else:
        print("\nThe scene file has not been saved.")


def get_textures_from_selection():
    """
    Find and return texture nodes associated with meshes in the selected group
    """
    # Check Selected Objects
    selection = cmds.ls(selection=True, long=True)

    if not selection:
        show_warning_dialog("No object selected.\nPlease select at least one group or mesh.")
        return set()

    # Find all child meshes of selected objects
    meshes = cmds.listRelatives(selection, allDescendents=True, type="mesh", fullPath=True) or []

    if not meshes:
        show_warning_dialog("There are no meshes within the selected group.\nPlease select a group that includes mesh.")
        return set()

    # set to store linked textures
    connected_textures = set()

    # Processing for each mesh
    for mesh in meshes:
        # Find the Shading Engine assigned to the mesh
        shading_engines = cmds.listConnections(mesh, type="shadingEngine") or []
        
        for se in shading_engines:
            # Finding Materials in Shading Engine
            materials = cmds.listConnections(f"{se}.surfaceShader", source=True, destination=False) or []
            
            for material in materials:
                # Find all file nodes connected to the material
                textures = cmds.listConnections(material, type="file") or []
                connected_textures.update(textures)
    
    
    if not connected_textures:
        show_warning_dialog("There are no textures associated with the selected mesh.")
        return set()
    
    return connected_textures


def set_texture_preview_quality(textures):
    """
    Set the preview quality of the given textures to 1k and generate previews
    """
    if not textures:
        return

    print("\n=== Texture Preview Settings ===")
    for texture in textures:
        if texture:
            # Set to Preview Quality 1k and Create Preview
            cmds.setAttr(f"{texture}.uvTileProxyQuality", 1)
            print(f"{texture} : uvTileProxyQuality 1k 설정 완료")
    
            # Generate Preview (Using MEL Commands)
            mel.eval(f'generateUvTilePreview "{texture}"')
            print(f"{texture} : Preview set up")

        else:
            error_msg = f"{texture} : No Texture"
            print(error_msg)

    print("=== Texture preview settings complete ===\n")


def update_selected_group_textures():
    """
    Update preview settings for textures in selected groups
    """
    set_working_diretory()

    # Find linked textures
    textures = get_textures_from_selection()
    
    if textures:
        print(f"\nFound Texture Nodes : Total ({len(textures)})")
        for tex in textures:
            print(f"- {tex}")
        
        # Update preview settings
        set_texture_preview_quality(textures)
