from __future__ import annotations
from maya import cmds
from abc import abstractmethod


class Expression:
    def __init__(self, action_delegate, predicate_delegate):
        self._action = action_delegate
        self._predicate = predicate_delegate

    def run(self, bone, *data):
        """ This method checks the predicate then runs the action """
        if self._predicate(bone, *data):
            self._action(bone, *data)


class RecursiveFramework:
    def __int__(self):
        self.root: str = ""
        self.forward_expressions: list[Expression] = []
        self.backward_expressions: list[Expression] = []

    # TODO: make sure the base joint has its values 0ed and the original values are added to the joint orient
    # TODO: all joint orient values are 0ed and they were moved to the rotate
    # TODO: make iteration to return how long from the end
    # TODO: make iteration to return depth level
    # TODO: make iteration to return branch id
    # TODO? make iteration to perform predication and expression
    @staticmethod
    def get_children(joint_name):
        return cmds.listRelatives(joint_name, children=True, type="joint") or []

    def transverse(self, bone):
        if not bone:
            return None

        for expression in self.forward_expressions:
            expression.run(bone, None)

        children = RecursiveFramework.get_children(bone)
        if children:
            for child in children:
                self.transverse(child)
                print(child)

        for expression in self.backward_expressions:
            expression.run(bone, None)


if __name__ == '__main__':
    rf = RecursiveFramework()
    rf.root = "test"
    rf.transverse(rf.root)
