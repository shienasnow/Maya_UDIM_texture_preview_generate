# -*- coding: utf-8 -*-

import os

import maya.mel as mel
import maya.cmds as cmds
from PySide2.QtWidgets import QMessageBox
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance


def get_maya_main_window():
    """
    Maya 메인 윈도우 포인터 반환
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QMessageBox)


def show_warning_dialog(message):
    """
    경고 메시지 다이얼로그 표시
    """
    maya_window = get_maya_main_window()
    QMessageBox.warning(maya_window, "경고", message)


def set_working_diretory():
    """
    씬 파일의 디렉토리로 작업 디렉토리를 변경
    """
    scene_path = cmds.file(query=True, sceneName=True)

    if scene_path:
        scene_dir = os.path.dirname(scene_path)

        # 디렉토리가 존재하는지 확인
        if os.path.isdir(scene_dir):
            os.chdir(scene_dir)
            print(f"\n작업 디렉토리를 변경했습니다: {scene_dir}")
        else:
            print(f"\n작업 디렉토리 변경 실패: 디렉토리가 존재하지 않습니다: {scene_dir}")
    else:
        print("\n씬 파일이 저장되지 않았습니다.")


def get_textures_from_selection():
    """
    선택된 그룹의 메시들에 연결된 텍스처 노드들을 찾아서 반환
    """
    # 선택된 객체 확인
    selection = cmds.ls(selection=True, long=True)

    if not selection:
        show_warning_dialog("객체가 선택되지 않았습니다.\n하나 이상의 그룹이나 메시를 선택해주세요.")
        return set()

    # 선택된 객체들의 모든 하위 메시 찾기
    meshes = cmds.listRelatives(selection, allDescendents=True, type="mesh", fullPath=True) or []

    if not meshes:
        show_warning_dialog("선택된 그룹 내에 메시가 없습니다.\n메시가 포함된 그룹을 선택해주세요.")
        return set()

    # 연결된 텍스처를 저장할 set
    connected_textures = set()

    # 각 메시에 대해 처리
    for mesh in meshes:
        # 메시에 할당된 쉐이딩 그룹(Shading Engine) 찾기
        shading_engines = cmds.listConnections(mesh, type="shadingEngine") or []
        
        for se in shading_engines:
            # Shading Engine에서 머터리얼 찾기
            materials = cmds.listConnections(f"{se}.surfaceShader", source=True, destination=False) or []
            
            for material in materials:
                # 머터리얼에 연결된 모든 file 노드 찾기
                textures = cmds.listConnections(material, type="file") or []
                connected_textures.update(textures)
    
    
    if not connected_textures:
        show_warning_dialog("선택된 메시에 연결된 텍스처가 없습니다.")
        return set()
    
    return connected_textures


def set_texture_preview_quality(textures):
    """
    주어진 텍스처들의 프리뷰 퀄리티를 1k로 설정하고 프리뷰 생성
    """
    if not textures:
        return

    print("\n=== 텍스처 프리뷰 설정 ===")
    for texture in textures:
        if texture:
            # Preview Quality 1k로 설정 및 프리뷰 생성
            cmds.setAttr(f"{texture}.uvTileProxyQuality", 1)
            print(f"{texture} : uvTileProxyQuality 1k 설정 완료")
    
            # Generate Preview (MEL 명령어 사용)
            mel.eval(f'generateUvTilePreview "{texture}"')
            print(f"{texture} : 프리뷰 설정 완료")

        else:
            error_msg = f"{texture} : 텍스처 없음"
            print(error_msg)

    print("=== 텍스처 프리뷰 설정 완료 ===\n")


def update_selected_group_textures():
    """
    선택된 그룹의 텍스처들에 대해 프리뷰 설정을 업데이트
    """
    set_working_diretory()

    # 연결된 텍스처 찾기
    textures = get_textures_from_selection()
    
    if textures:
        print(f"\n발견된 텍스처 노드 ({len(textures)}개):")
        for tex in textures:
            print(f"- {tex}")
        
        # 프리뷰 설정 업데이트
        set_texture_preview_quality(textures)
