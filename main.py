from datastructures.bin_tree.binary_tree import BinaryTree
from datastructures.bin_tree.search_binary_tree import SearchBinaryTree
from datastructures.bin_tree.expression_tree import ExpressionTree
from datastructures.bin_tree.avl_tree import AVLTree
from exercices.tic_tac_toe import Tree

#tree = BinaryTree()

# # Create the root
# root = tree.create_node(10)

# # Add children
# root.left_child = tree.create_node(5)
# root.right_child = tree.create_node(15)

# # Assign root to the tree
# tree.root = root

# # Basic tests
# print("Tree empty:", tree.is_empty_tree())
# print("Root:", tree.root.data)
# print("Left child:", tree.root.left_child.data)
# print("Right child:", tree.root.right_child.data)
# print("Is root a leaf?", tree.is_leaf(root))
# print("Is left node a leaf?", tree.is_leaf(root.left_child))

#############################################

# tree = Tree()

# # Place a move directly
# tree.root.set_cell(1, 1, "X")
# print("Board:")
# tree.print_tree()

# # Expand into possible next moves
# tree.expand(tree.root, "O")
# print(f"\n{len(tree.root.children)} children generated:")
# tree.print_children(tree.root)

###############################################

"""Testing the BinaryTree class."""

# tree = BinaryTree()

# values = [6, 2, 11, 3, 9, 30, 13, 18, 10, 5, 15, 4, 7, 20, 12, 25]

# for v in values:
#     tree.insert(v)

# tree.print_tree_recursive()

# print("High:", tree.high())
# print("Size:", tree.size())
# print("Iteration by level:", tree.iteration_by_levels())

# print("Pre-order (recursive): ", tree.pre_order())
# print("Pre-order (iterative): ", tree._pre_order_iter())

# print("In-order (recursive):  ", tree.in_order())
# print("In-order (iterative):  ", tree._in_order_iter())

# print("Post-order (recursive):", tree.post_order())
# print("Post-order (iterative):", tree._post_order_iter())

# print("has(9):  ", tree.has(9))
# print("has(99): ", tree.has(99))
# print("search(9):", tree.search(9))
# print("is_empty_tree():", tree.is_empty_tree())
# print("is_leaf(root):", tree.is_leaf(tree.root))

###########################################

"""Testing the SearchBinaryTree class."""

# tree = SearchBinaryTree()

# values = [50, 30, 70, 20, 40, 60, 80, 10]
# for value in values:
#     tree.insert(value)

# print("Tree (right on top, left on bottom):")
# tree.print_tree_recursive()

# print("\nIn-order:", tree.in_order())
# print("Pre-order:", tree.pre_order())
# print("Post-order:", tree.post_order())
# print("By levels:", tree.iteration_by_levels())

# print("\nHigh:", tree.high())
# print("Size:", tree.size())

# print("\nHas 40?", tree.has(40))
# print("Has 99?", tree.has(99))
# print("Search 60:", tree.search(60))
# print("Search 99:", tree.search(99))

# root = tree.root
# print("\nIs root a leaf?", tree.is_leaf(root))
# print("Is left-left a leaf?", tree.is_leaf(root.left_child.left_child))


###########################################

"""Testing the ExpressionTree class."""

# - (7 + 3) * (5 - 2)
# expression = ["7", "3", "+", "5", "2", "-", "*"]  # 30

# - (10 / (2 + 3)) + 6
# expression = ["10", "2", "3", "+", "/", "6", "+"]  # 8

# - (8 - 4) ^ 2
# expression = ["8", "4", "-", "2", "^"]  # 16

# - (15 / 3) * (2 + 7)
# expression = ["15", "3", "/", "2", "7", "+", "*"]  # 45

# - ((2 + 3) * (4 + 5)) - 6
# expression = [
#     "2", "3", "+", "4", "5", "+", "*", "6", "-"
# ]  # Expected: ((5 * 9) - 6) = 39

# tree = ExpressionTree(expression)
# tree.print_tree_recursive()
# result = tree.evaluate()
# print("Result: " + str(result))
# print(
#     "Infix expression: "
#     + ExpressionTree.list_to_string(tree.in_order())
# )
# print(
#     "Prefix expression: "
#     + ExpressionTree.list_to_string(tree.pre_order())
# )
# print(
#     "Postfix expression: "
#     + ExpressionTree.list_to_string(tree.post_order())
# )

# print()
# print("---- from_infix demo (Shunting Yard) ----")
# infix_text = "(((3 + 6) * (2 - 4)) + 7)"
# infix_tree = ExpressionTree.from_infix(infix_text)
# infix_tree.print_tree_recursive()
# print("Infix input:  " + infix_text)
# print(
#     "Postfix used: "
#     + ExpressionTree.list_to_string(
#         ExpressionTree.infix_to_postfix(
#             ExpressionTree.tokenize_infix(infix_text)
#         )
#     )
# )
# print("tokenize_infix: " + str(ExpressionTree.tokenize_infix(infix_text)))
# print("infix_to_postfix: " + str(ExpressionTree.infix_to_postfix(
#     ExpressionTree.tokenize_infix(infix_text)
# )))
# print("Result: " + str(infix_tree.evaluate()))  # Expected: -11.0


###########################################

"""Testing the AVLTree class."""

# ------------------------------------------------------------------
# Demo (mirrors AVLTree.generateAVLTree() from the Java version)
# ------------------------------------------------------------------

tree = AVLTree()
tree.insert(10)
tree.insert(20)
tree.insert(30)
tree.insert(40)
tree.insert(50)
tree.insert(60)
tree.insert(70)
tree.insert(80)
tree.insert(90)
tree.print_tree_recursive()
print("Balanced: " + str(tree.is_balanced()))
tree.insert(100)
tree.insert(110)
tree.insert(120)
tree.insert(130)
tree.insert(140)
tree.insert(150)
tree.print_tree_recursive()
tree.delete(50)
tree.print_tree_recursive()
print("Balanced: " + str(tree.is_balanced()))