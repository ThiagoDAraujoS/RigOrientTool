from maya import cmds
from typing import Callable


class RecursiveFramework:
    def __int__(self):
        self.root_bone: str = ""
        self.predicates: tuple[Pattern, Callable]

    # TODO: make sure the base joint has its values 0ed and the original values are added to the joint orient
    # TODO: all joint orient values are 0ed and they were moved to the rotate

    # TODO: Create a recursion that travels through a bone structure


    def transverse(self, bone):
        """
        this method goes through a tree
        :param bone:
        :return:
        """

        children = cmds.listRelatives(bone)
        if children:
            for child in children:
                self.transverse(child)


class Pattern:
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')
