"""test for ADT.tree
Test Cases:

BTree1:

    3
   / \
  9  20
    /  \
   15   7

BTree2:

        1
       / \
      2  5
     /  / \
    3  6   7
   /      / \
  4      8   9

Tree1:

        1
       /|\
      2 3 4
     /  |  \
    5   6   7
   /      / | \
  8      9 10  11

"""
import unittest

from adt.tree import BTree, Tree


class TreeTest(unittest.TestCase):
    tr1 = Tree(node=1,
               children=(
                   Tree(
                       node=2,
                       children=(Tree(node=5, children=(Tree(node=8), )), ),
                   ),
                   Tree(node=3, children=(Tree(node=6), )),
                   Tree(node=4,
                        children=(Tree(node=7,
                                       children=(Tree(node=9), Tree(node=10),
                                                 Tree(node=11))), )),
               ))
    ibt1 = BTree(node=3,
                 left=BTree(node=9),
                 right=BTree(node=20, left=BTree(node=15),
                             right=BTree(node=7)))
    ibt2 = BTree(node=1,
                 left=BTree(node=2, left=BTree(node=3, left=BTree(node=4))),
                 right=BTree(node=5,
                             left=BTree(node=6),
                             right=BTree(node=7,
                                         left=BTree(node=8),
                                         right=BTree(9))))
    ibt1_depth = 3
    ibt2_depth = 4
    ibt2_bfs = (1, 2, 5, 3, 6, 7, 4, 8, 9)
    ibt2_dfs_pre = (1, 2, 3, 4, 5, 6, 7, 8, 9)
    ibt2_dfs_in = (4, 3, 2, 1, 6, 5, 8, 7, 9)
    ibt2_dfs_post = (4, 3, 2, 6, 8, 9, 7, 5, 1)
    tr1_bfs = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    tr1_dfs_pre = (1, 2, 5, 8, 3, 6, 4, 7, 9, 10, 11)
    tr1_dfs_post = (8, 5, 2, 6, 3, 9, 10, 11, 7, 4, 1)
    tr1_str = (
        'tree:',
        '1',
        '- 2',
        '- - 5',
        '- - - 8 (leaf)',
        '- 3',
        '- - 6 (leaf)',
        '- 4',
        '- - 7',
        '- - - 9 (leaf)',
        '- - - 10 (leaf)',
        '- - - 11 (leaf)',
    )
    ibt2_str = (
        'binary tree:',
        '1',
        '- 2',
        '- - 3',
        '- - - 4 (leaf)',
        '- 5',
        '- - 6 (leaf)',
        '- - 7',
        '- - - 8 (leaf)',
        '- - - 9 (leaf)',
    )

    def test_btree(self):
        self.assertEqual(self.ibt1_depth, self.ibt1.depth())
        self.assertEqual(self.ibt2_depth, self.ibt2.depth())
        self.assertEqual(self.ibt2_bfs, self.ibt2.bfs())
        self.assertEqual(self.ibt2_dfs_pre, self.ibt2.dfs_pre())
        self.assertEqual(self.ibt2_dfs_in, self.ibt2.dfs_in())
        self.assertEqual(self.ibt2_dfs_post, self.ibt2.dfs_post())

    def test_tree(self):
        self.assertEqual(self.tr1_bfs, self.tr1.bfs())
        self.assertEqual(self.tr1_dfs_pre, self.tr1.dfs_pre())
        self.assertEqual(self.tr1_dfs_post, self.tr1.dfs_post())
        self.assertEqual(repr(self.tr1), '\n'.join(self.tr1_str))
        self.assertEqual(repr(self.ibt2), '\n'.join(self.ibt2_str))


if __name__ == '__main__':
    unittest.main(verbosity=2)
