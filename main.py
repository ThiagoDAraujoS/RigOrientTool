from __future__ import annotations
from maya import cmds

# GLOBAL VARIABLES USED BY THE DYNAMIC EXPRESSIONS
r_bone = ""
r_parent = ""
ex = ""


class Expression:
    def __init__(self, action_delegate, predicate_delegate):
        self._action = action_delegate
        self._predicate = predicate_delegate

    def run(self, bone, *data):
        """ This method checks the predicate then runs the action """
        if self._predicate(bone, *data):
            self._action(bone, *data)


class RecursiveFramework:
    def __init__(self):
        self.root: str = ""
        self.forward_expressions: list[Expression] = []
        self.backward_expressions: list[Expression] = []

    def transverse(self, on_no_bone_selected=None):
        selected_objects = cmds.ls(selection=True, type="joint")
        if not selected_objects:
            if on_no_bone_selected:
                on_no_bone_selected()
            return
        bone = selected_objects[0]
        self.echo(bone, bone)

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
    def _perform_expressions(bone, parent, block):
        global r_bone, r_parent
        r_bone, r_parent = bone, parent
        for expression in block:
            expression.run(bone, parent)

    def echo(self, bone, parent):
        if not bone:
            return None

        RecursiveFramework._perform_expressions(bone, parent, self.forward_expressions)
        children = RecursiveFramework._get_children(bone)
        if children:
            for child in children:
                self.echo(child, bone)
        RecursiveFramework._perform_expressions(bone, parent, self.backward_expressions)


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
        cmds.textFieldGrp(tcc=self.on_predicate_text_changed)
        cmds.button(label="Perform", command=self.on_perform_click)

    def on_perform_click(self, *_):
        self.rf.transverse(on_no_bone_selected=self.on_no_selected_bone)

    def on_predicate_text_changed(self, value, *_):
        global ex
        ex = value

    def on_no_selected_bone(self):
        cmds.confirmDialog(title="Warning", message="No bones were selected.", icon="warning", button=["OK"])


def action(bone: str, *_) -> None:
    cube = cmds.polyCube()[0]
    cmds.matchTransform(cube, bone)


if __name__ == '__main__':
    rf = RecursiveFramework()
    expression = Expression(action_delegate=action, predicate_delegate=lambda b, *_: eval(ex))
    rf.backward_expressions = [expression]
    window = RecursiveToolWindow(rf)
    window.show()


    # fingy_expression = Expression(action_delegate=action, predicate_delegate=lambda b, *_: b.endswith("fingy"))
    # rf = RecursiveFramework()
    # rf.backward_expressions.append(fingy_expression)
    # rf.root = "test"
#
    # rf.transverse(rf.root)
