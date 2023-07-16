from __future__ import annotations
from maya import cmds
from typing import Callable


class Pattern:
    pass


class RecursiveFramework:
    def __int__(self):
        self.root: str = ""
        self.predicates: tuple[Pattern, Callable]

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

        children = RecursiveFramework.get_children(bone)
        if children:
            for child in children:
                self.transverse(child)
                print(child)


if __name__ == '__main__':
    rf = RecursiveFramework()
    rf.root = "test"
    rf.transverse(rf.root)
