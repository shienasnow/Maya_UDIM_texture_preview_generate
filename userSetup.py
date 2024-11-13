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

    # 모든 쉘프 탭 가져오기
    gShelfTopLevel = mel.eval('$tmp = $gShelfTopLevel')
    
    # 기존 CustomTools 쉘프가 있다면 완전히 삭제
    if cmds.shelfLayout(shelf_name, exists=True):
        # 쉘프의 모든 버튼 삭제
        existing_buttons = cmds.shelfLayout(shelf_name, q=True, childArray=True) or []
        for btn in existing_buttons:
            if cmds.objExists(btn):
                cmds.deleteUI(btn)
    else:
        # 쉘프가 없는 경우에만 새로 생성
        mel.eval('addNewShelfTab "%s"' % shelf_name)
    
    # 버튼이 이미 존재하는지 확인
    shelf_buttons = cmds.shelfLayout(shelf_name, q=True, childArray=True) or []
    button_exists = False
    for btn in shelf_buttons:
        if cmds.shelfButton(btn, q=True, label=True) == 'Generate Preview':
            button_exists = True
            break
    
    # 버튼이 없을 때만 새로 생성
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

# Maya UI가 로드된 후 실행되도록 설정
cmds.evalDeferred(initializePlugin)
