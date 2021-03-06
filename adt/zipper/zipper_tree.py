from __future__ import annotations

from dataclasses import dataclass
from functools import reduce
from typing import Iterator, Sequence, Tuple, TypeVar

from adt.tree import Tree
from adt.zipper.base_zipper import BaseContext, BaseContexts, BaseZipper

T = TypeVar('T')


@dataclass(frozen=True)
class TreeContext(BaseContext[T]):
    root: T
    left: Tuple[Tree[T], ...]
    right: Tuple[Tree[T], ...]

    def __str__(self):
        left_str = '\n'.join(map(repr, self.left))
        right_str = '\n'.join(map(repr, self.right))
        return '\n'.join((
            f'root: {repr(self.root)}',
            f'left: {left_str}',
            f'right: {right_str}',
        ))

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class TreeContexts(BaseContexts, TreeContext[T]):
    rec: TreeContexts = None

    @property
    def context(self) -> TreeContext[T]:
        return TreeContext(self.root, self.left, self.right)

    def __str__(self):
        return 'Tree contexts:\n' + super().__str__()

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class ZipperTree(BaseZipper[T]):
    tree: Tree[T]
    contexts: TreeContexts[T]

    @classmethod
    def from_tree(cls, tree: Tree[T]):
        return cls(tree=tree, contexts=None)

    @property
    def _body(self) -> Tree[T]:
        return self.tree

    @property
    def _contexts(self) -> TreeContexts:
        return self.contexts

    def __str__(self):
        return 'Tree with Zipper:\n' + super().__str__()

    def __repr__(self):
        return self.__str__()

    @property
    def bottom(self) -> bool:
        if not self.tree.children:
            return True
        return False

    def go_up(self) -> ZipperTree[T]:
        if self.top:
            return self
        return type(self)(
            type(self.tree)(
                self.contexts.root,
                (
                    *self.contexts.left,
                    self.tree,
                    *self.contexts.right,
                ),
            ),
            self.contexts.rec,
        )

    def go_down(self, *args, **kwargs) -> ZipperTree[T]:
        idx = kwargs.get('idx', 0)
        if self.bottom:
            return self
        if idx < 0:
            idx_ = len(self.tree.children) + idx
        else:
            idx_ = idx
        subtree = self.tree.children[idx_]
        return type(self)(
            subtree,
            TreeContexts(
                self.tree.root,
                self.tree.children[:idx_],
                self.tree.children[idx_ + 1:],
                self.contexts,
            ),
        )

    @property
    def left_most(self) -> bool:
        if not self.contexts:
            return True
        return not self.contexts.left

    @property
    def right_most(self) -> bool:
        if not self.contexts:
            return True
        return not self.contexts.right

    def go_left(self) -> ZipperTree[T]:
        if self.left_most:
            return self
        tr = self.contexts.left[-1]
        left = self.contexts.left[:-1]
        right = (self.tree, *self.contexts.right)
        return (type(self))(tr,
                            TreeContexts(
                                self.contexts.root,
                                left,
                                right,
                                self.contexts.rec,
                            ))

    def go_right(self) -> ZipperTree[T]:
        if self.right_most:
            return self
        tr = self.contexts.right[0]
        left = (*self.contexts.left, self.tree)
        right = self.contexts.right[1:]
        return (type(self))(tr,
                            TreeContexts(
                                self.contexts.root,
                                left,
                                right,
                                self.contexts.rec,
                            ))

    def go_down_most(self, *args, **kwargs) -> ZipperTree[T]:
        """go local bottom
        """
        left = kwargs.get('left', True)
        if self.bottom and ((left and self.left_most) or
                            (not left and self.right_most)):
            return self
        if self.bottom and left:
            return self.go_left().go_down_most(left=left)
        if self.bottom and not left:
            return self.go_right().go_down_most(left=left)
        if left:
            idx = 0
        else:
            idx = -1
        return self.go_down(idx=idx).go_down_most(left=left)

    def go_bottomleft(self) -> ZipperTree[T]:
        """go global bottom-left
        """
        return self.go_up_most().go_down_most(left=True)

    def go_bottomright(self) -> ZipperTree[T]:
        """go global bottom-right
        """
        return self.go_up_most().go_down_most(left=False)

    def dfs_pre(self) -> Iterator[T]:
        """pre-order deep first search

        0. start from top
        1. if bottom-right most, all finished
        2. if right most and bottom most (not bottom-right most,
           meaning parent tree finished), repeat until succeed:
           **go for parent's right siblings**
        3. if right most but not bottom most, go down-left
        4. if bottom most but not right most, go for right siblings
        :return: ZTree generator
        """
        tr = self.go_up_most()
        bottomright = tr.go_bottomright()
        while True:
            yield tr.tree.root
            if tr == bottomright:
                break
            if tr.bottom and tr.right_most:
                while True:
                    # print('up')
                    tr = tr.go_up()
                    if not tr.right_most:
                        tr = tr.go_right()
                        break
            elif tr.bottom and not tr.right_most:
                tr = tr.go_right()
                # print('right')
            else:
                tr = tr.go_down(idx=0)
                # print('down left')

    def dfs_post(self) -> Iterator[T]:
        """post-order deep first search

        0. start from bottom-left most
        1. if top, all finished
        2. if right most, go up
        3. if bottom most and not right most, go right
        4. if bottom most but not right most, go for right siblings
        5. if not bottom most and not right most:
           go to the bottom-left of its right sibling
        :return: ZTree generator
        """
        tr = self.go_bottomleft()
        top = tr.go_up_most()
        while True:
            yield tr.tree.root
            if tr == top:
                break
            if tr.right_most:
                tr = tr.go_up()
            elif tr.bottom:
                tr = tr.go_right()
            else:
                tr = tr.go_right().go_down_most(left=True)

    def children(self) -> Tuple[ZipperTree[T], ...]:
        """all children Zipper Trees
        """
        def helper(
            zt: ZipperTree[T],
            acc: Tuple[ZipperTree[T], ...],
        ) -> Sequence[ZipperTree[T]]:
            if zt.right_most:
                return (*acc, zt)
            return helper(zt.go_right(), (*acc, zt))

        if self.bottom:
            return ()
        return helper(self.go_down(idx=0), ())

    @classmethod
    def generation(
        cls,
        seq: Sequence[ZipperTree[T]],
    ) -> Tuple[ZipperTree[T], ...]:
        return reduce(lambda x, y: x + y, map(cls.children, seq))

    def bfs(self) -> Iterator[ZipperTree[T]]:
        def helper(inputs: Tuple[ZipperTree[T], ...],
                   outputs: Iterator[ZipperTree[T]]):
            seq = self.generation(inputs)
            if not seq:
                return iter(map(lambda x: x.tree.root, outputs))
            return helper(seq, (*outputs, *seq))

        return helper((self, ), (self, ))
