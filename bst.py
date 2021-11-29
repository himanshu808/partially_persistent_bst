class BSTNode:
    def __init__(self, value, level, left=None, right=None, parent=None):
        self.value = value
        self.level = level
        self.right = right
        self.left = left
        self.parent = parent

    def __repr__(self):
        return str(self.value)


class BST:
    def __init__(self):
        self.root = None
        self.max_level = -1

    def find_parent_node(self, value):
        parent_node = None
        node = self.root
        while node is not None:
            parent_node = node
            if value <= node.value:
                node = node.left
            else:
                node = node.right
        return parent_node

    def find_node(self, value):
        node = self.root
        while node is not None:
            if value == node.value:
                return node
            elif value < node.value:
                node = node.left
            else:
                node = node.right
        return None

    def postorder_traversal(self, node, tree, level):
        if node is None:
            tree[level].append(None)
        else:
            tree = self.postorder_traversal(node.left, tree, node.level+1)
            tree = self.postorder_traversal(node.right, tree, node.level+1)
            tree[level].append(node.value)
        return tree

    def insert_node(self, value):
        if self.root is None:
            self.root = BSTNode(value, 0)
            self.max_level = 0
        else:
            parent_node = self.find_parent_node(value)
            node = BSTNode(value, parent_node.level + 1, parent=parent_node)
            if value <= parent_node.value:
                parent_node.left = node
            else:
                parent_node.right = node
            if node.level > self.max_level:
                self.max_level = node.level

    def delete_leaf_node(self, node):
        if node is self.root:
            self.root = None
            return
        parent_node = node.parent
        if node.value > parent_node.value:
            parent_node.right = None
        else:
            parent_node.left = None

    def delete_node_with_single_child(self, node):
        parent_node = node.parent
        if node is self.root:
            self.root = node.left if node.left else node.right
        else:
            if node.value > parent_node.value:
                if node.left:
                    parent_node.right = node.left
                else:
                    parent_node.right = node.right
            else:
                if node.left:
                    parent_node.left = node.left
                else:
                    parent_node.left = node.right

        if node.left:
            node.left.parent = parent_node
            self.recalculate_subtree_levels(node.left)
        else:
            node.right.parent = parent_node
            self.recalculate_subtree_levels(node.right)

    def find_min_value_node(self, node):
        while node.left is not None:
            node = node.left
        return node

    def delete_node_with_two_children(self, node):
        inorder_successor = self.find_min_value_node(node.right)

        node.value = inorder_successor.value

        if inorder_successor is node.right:
            inorder_successor.parent.right = inorder_successor.right
        else:
            inorder_successor.parent.left = inorder_successor.right
            self.recalculate_subtree_levels(inorder_successor.right)
        inorder_successor.parent = None
        return inorder_successor

    def recalculate_subtree_levels(self, node):
        if node is None:
            return
        else:
            node.level -= 1
            self.recalculate_subtree_levels(node.left)
            self.recalculate_subtree_levels(node.right)

    def recalculate_max_level(self, node):
        # todo: check alternate implementation using node.level
        def inorder_traversal(node):
            if node is None:
                return
            self.max_level = max(self.max_level, node.level)
            inorder_traversal(node.left)
            inorder_traversal(node.right)
        inorder_traversal(node)

        # if node is None:
        #     return 0
        # else:
        #     left_level = self.recalculate_max_level(node.left)
        #     right_level = self.recalculate_max_level(node.right)
        #
        #     if left_level > right_level:
        #         return left_level + 1
        #     else:
        #         return right_level + 1

    def delete_node(self, value):
        node_to_delete = self.find_node(value)
        if node_to_delete is None:
            print('no such node')
        elif node_to_delete.left is None and node_to_delete.right is None:
            self.delete_leaf_node(node_to_delete)
        elif (node_to_delete.left is not None) ^ (node_to_delete.right is not None):
            self.delete_node_with_single_child(node_to_delete)
        else:
            node_to_delete = self.delete_node_with_two_children(node_to_delete)

        del node_to_delete
        self.max_level = -1
        # self.max_level = self.recalculate_max_level(self.root) - 1
        self.recalculate_max_level(self.root)

    def print_tree(self):
        if self.root is None:
            print("empty tree")
            return
        # +1 because max_level of root is 0 and +1 because we also print the null nodes
        tree = self.postorder_traversal(self.root, [[] for _ in range(self.max_level+2)], 0)
        print(tree)

    def print_nodes(self):
        if self.root is None:
            print("empty tree")
            return
        node = self.root

        def preorder_traversal(node):
            if node is None:
                return
            print(f"(v: {node.value}, p: {node.parent.value if node.parent else None}, lv: {node.level})")
            preorder_traversal(node.left)
            preorder_traversal(node.right)

        preorder_traversal(node)
        print(f"max: {self.max_level}")


if __name__ == '__main__':
    import sys
    bst = BST()

    while True:
        x = input()
        op = int(x if x else 0)

        if op == 1:
            bst.insert_node(int(input("val: ")))
        elif op == 2:
            bst.delete_node(int(input("del val: ")))
        elif op == 3:
            bst.print_tree()
        elif op == 4:
            bst.print_nodes()
        elif op == 9:
            sys.exit()
