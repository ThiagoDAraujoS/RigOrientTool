from __future__ import annotations
from maya import cmds
from functools import partial

# GLOBAL VARIABLES USED BY THE DYNAMIC EXPRESSIONS
r_bone = ""
r_parent = ""
ex = ""


class Expression:
    def __init__(self, action, predicate):
        self._action = action
        self._predicate = predicate

    def run(self, bone, *data):
        """ This method checks the predicate then runs the action """
        if self._predicate(bone, *data):
            self._action(bone, *data)


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
        self._echo(bone, bone)

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
    def _perform_expressions(block, bone, parent):
        global r_bone, r_parent
        r_bone, r_parent = bone, parent
        for expression in block:
            expression.run(bone, parent)

    def _echo(self, bone, parent):
        if not bone:
            return

        RecursiveFramework._perform_expressions(bone, parent, self.forward_expressions)
        children = RecursiveFramework._get_children(bone)
        if children:
            for child in children:
                self._echo(child, bone)
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


def action(bone: str, *_) -> None:
    cube = cmds.polyCube()[0]
    cmds.matchTransform(cube, bone)


if __name__ == '__main__':
    rf = RecursiveFramework()
    expression = Expression(action=action, predicate=lambda b, *_: eval(ex))
    rf.backward_expressions = [expression]
    window = RecursiveToolWindow(rf)
    window.show()

    # fingy_expression = Expression(action_delegate=action, predicate_delegate=lambda b, *_: b.endswith("fingy"))
    # rf = RecursiveFramework()
    # rf.backward_expressions.append(fingy_expression)
    # rf.root = "test"
#
# rf.transverse(rf.root)
