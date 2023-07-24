from __future__ import annotations
from maya import cmds
from functools import partial
from maya.api.OpenMaya import MVector, MEulerRotation

# GLOBAL VARIABLES USED BY THE DYNAMIC EXPRESSIONS
BONE: Bone = None
NAME: str = ""
PATH = []
ex = ""


class Bone:
    def __init__(self, name, parent_name, index):
        self.name = name
        self.translation = cmds.xform(name, query=True, translation=True, worldSpace=True)
        self.rotation = cmds.xform(name, query=True, rotation=True, worldSpace=True)
        self.scale = cmds.xform(name, query=True, scale=True)
        self.child_count = len(cmds.listRelatives(name, children=True, type="joint") or [])
        self.parent_name = parent_name
        self.index = index


def endswith(string):
    return BONE.name.endswith(string)


def startswith(string):
    return BONE.name.startswith(string)


def has_past(predicate):
    return any([predicate(bone) for bone in PATH])


def is_between(start_predicate, end_predicate):
    global NAME, BONE
    print(NAME, BONE)
    temp_name, temp_bone = NAME, BONE
    result = False
    for bone in reversed(PATH):
        NAME, BONE = BONE.name, bone
        if end_predicate(bone):
            break
        if start_predicate(bone):
            result = True
            break
        NAME, BONE = temp_name, temp_bone
    return result


class Expression:
    def __init__(self, action, predicate):
        self._action = action
        self._predicate = predicate

    def run(self, bone, *data):
        """ This method checks the predicate then runs the action """
        if self._predicate(bone, *data):
            self._action(bone, *data)


# TODO ENSURE ROTATE GETS SUMMED TO JOINT ORIENT

class RecursiveFramework:
    def __init__(self):
        self.root: str = ""
        self.forward_expressions: list[Expression] = []
        self.backward_expressions: list[Expression] = []

    def transverse(self, on_no_bone_selected_callback=None):
        """ Initiate a recursion starting the Selected bone

        :param on_no_bone_selected_callback: if no bones are selected this callback will trigger defaults to none
        """

        selected_objects = cmds.ls(selection=True, type="joint")
        if not selected_objects:
            if on_no_bone_selected_callback:
                on_no_bone_selected_callback()
            return
        bone = selected_objects[0]
        self._echo(bone, bone, [])

    # TODO: make sure the base joint has its values 0ed and the original values are added to the joint orient
    # TODO: all joint orient values are 0ed and they were moved to the rotate
    # TODO: make iteration to return how long from the end
    # TODO: make iteration to return depth level
    # TODO: make iteration to return branch id
    # TODO? make iteration to perform predication and expression
    @staticmethod
    def _get_children(joint_name):
        return cmds.listRelatives(joint_name, children=True, type="joint") or []

    @staticmethod
    def _perform_expressions(block, bone, path):
        global BONE, NAME, PATH
        BONE, NAME, PATH = bone, bone.name, path

        for expression in block:
            expression.run(bone)

    def _echo(self, bone, parent, path, index=0):
        global BONE

        if not bone:
            return

        path.append(bone)
        index += 1
        bone_instance = Bone(bone, parent, index)

        RecursiveFramework._perform_expressions(self.forward_expressions, bone_instance, path)
        children = RecursiveFramework._get_children(bone)
        if children:
            for child in children:
                self._echo(child, bone, path)
        path.pop()
        RecursiveFramework._perform_expressions(self.backward_expressions, bone_instance, path)


class RecursiveToolWindow(object):
    WINDOW_NAME = "BONE_SWIPE"

    def __init__(self, tool_ref):
        self.rf: RecursiveFramework = tool_ref
        self.window = None

    def show(self):
        if cmds.window(RecursiveToolWindow.WINDOW_NAME, exists=True):
            cmds.deleteUI(RecursiveToolWindow.WINDOW_NAME, window=True)
        self.window = cmds.window(RecursiveToolWindow.WINDOW_NAME, title="Bone Swipe", widthHeight=(300, 100))
        self._build()
        cmds.showWindow(self.window)

    def _build(self):
        root_element = cmds.columnLayout(adjustableColumn=True)
        cmds.textFieldGrp(tcc=self._on_predicate_text_changed)
        cmds.button(label="Perform", command=self._on_perform_click)
        return root_element

    def _on_perform_click(self, *_):
        self.rf.transverse(on_no_bone_selected_callback=self._on_no_bone_selected)

    def _on_predicate_text_changed(self, value, *_):
        global ex
        ex = value

    def _on_no_bone_selected(self):
        cmds.confirmDialog(title="Warning", message="No bones were selected.", icon="warning", button=["OK"])


class RecursiveToolWindowMk2(object):
    WINDOW_NAME = "BONE_SWIPEMk2"

    def __init__(self, tool_ref, expressions):
        self.rf: RecursiveFramework = tool_ref
        self.expressions = expressions
        self.window = None
        self.stack_layout = None

    def show(self):
        if cmds.window(RecursiveToolWindow.WINDOW_NAME, exists=True):
            cmds.deleteUI(RecursiveToolWindow.WINDOW_NAME, window=True)
        self.window = cmds.window(RecursiveToolWindow.WINDOW_NAME, title="Bone Swipe", widthHeight=(300, 100))
        self._build()
        cmds.showWindow(self.window)

    def _build(self) -> str:
        """ Builds the window's base elements and layouts """
        root_element = cmds.columnLayout(adjustableColumn=True)
        form_layout = cmds.formLayout()
        grid_element = self._build_expression_grid()
        stack_element = self._build_expression_stack()
        cmds.formLayout(form_layout,
                        edit=True,
                        attachForm=[
                            (grid_element, 'left', 5),
                            (stack_element, 'right', 5)],
                        attachPosition=[
                            (grid_element, 'right', 35, 0),
                            (stack_element, 'left', 35, 100)],
                        attachNone=[
                            (grid_element, 'top'), (grid_element, 'bottom'),
                            (stack_element, 'top'), (stack_element, 'bottom')])
        return root_element

    def _build_expression_grid(self) -> str:
        """ Build a grid element filled with buttons, each button represents an action """
        root_element = cmds.scrollLayout(childResizable=True, height=300)
        cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(100, 50))
        for name, expression in self.expressions.items():
            cmds.button(label=name, command=partial(self._on_expression_btn_clicked, expression))
        return root_element

    def _build_expression_stack(self) -> str:
        root_element = cmds.scrollLayout(childResizable=True, height=300)
        self.stack_layout = cmds.columnLayout(adjustableColumn=True)
        return root_element

    def _build_expression_widget(self):
        cmds.rowLayout(numberOfColumns=3)
        cmds.text()
        pass

    def _on_add_expression_btn_clicked(self):
        pass

    def _on_remove_expression_btn_clicked(self):
        pass

    def _on_move_expression_up_btn_clicked(self):
        pass

    def _on_move_expression_down_btn_clicked(self):
        pass

    def _on_expression_btn_clicked(self, *_):
        self.rf.transverse(on_no_bone_selected_callback=self._on_no_bone_selected_cb_triggered)

    def _on_predicate_text_changed(self, value, *_):
        global ex
        ex = value

    def _on_no_bone_selected_cb_triggered(self):
        cmds.confirmDialog(title="Warning", message="No bones were selected.", icon="warning", button=["OK"])


def action(bone: Bone, *_) -> None:
    cube = cmds.polyCube()[0]
    cmds.matchTransform(cube, bone.name)


def jointOrient(bone: Bone, *_) -> None:
    cmds.xform(bone.name, relative=True, objectSpace=True, rotation=[0.0, 0.0, 0.0])
    cmds.joint(bone.name, edit=True, zeroScaleOrient=True)
    cmds.makeIdentity(bone.name, apply=True)


if __name__ == '__main__':
    rf = RecursiveFramework()
    expression = Expression(action=jointOrient, predicate=lambda b, *_: eval(ex))
    rf.backward_expressions = [expression]
    window = RecursiveToolWindow(rf)
    window.show()

    # fingy_expression = Expression(action_delegate=action, predicate_delegate=lambda b, *_: b.endswith("fingy"))
    # rf = RecursiveFramework()
    # rf.backward_expressions.append(fingy_expression)
    # rf.root = "test"
#
# rf.transverse(rf.root)
