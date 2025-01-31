from fat_node import FatNode


class BSTNode:
    def __init__(self, value, level, version, left=None, right=None, parent=None):
        self.value = value
        self.level = level
        self.right = right
        self.left = left
        self.parent = parent
        self.fat_node = FatNode(self, version)

    def __repr__(self):
        return str(self.value)

    '''
    TODO: possible optimizations - 
        1. add new versions for only those attributes that have changed
        2. update all nodes after completing the entire operation; each node will have to be updated only once
    '''
    def update_fat_node(self, version):
        # TODO: alternatively, check observer pattern and some sort of change detection mechanism
        for attr in self.fat_node.__dict__:
            if attr in self.__dict__:
                getattr(self.fat_node, attr)[version] = getattr(self, attr)
        self.fat_node.version_list.append(version)

class BST:
    def __init__(self):
        self.root = None
        self.max_level = -1
        self.current_version = 0
        self.access_pointers = dict()
        self.version_max_level = dict()

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
        self.current_version += 1
        if self.root is None:
            self.root = BSTNode(value, 0, self.current_version)
            self.max_level = 0
        else:
            parent_node = self.find_parent_node(value)
            node = BSTNode(value, parent_node.level + 1, self.current_version, parent=parent_node)
            if value <= parent_node.value:
                parent_node.left = node
            else:
                parent_node.right = node
            parent_node.update_fat_node(self.current_version)
            if node.level > self.max_level:
                self.max_level = node.level
        self.version_max_level[self.current_version] = self.max_level
        self.access_pointers[self.current_version] = self.root

    def delete_leaf_node(self, node):
        if node is self.root:
            self.root = None
            return
        parent_node = node.parent
        if node.value > parent_node.value:
            parent_node.right = None
        else:
            parent_node.left = None
        parent_node.update_fat_node(self.current_version)

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
            parent_node.update_fat_node(self.current_version)

        if node.left:
            node.left.parent = parent_node
            self.recalculate_subtree_levels(node.left)
            node.left.update_fat_node(self.current_version)
        else:
            node.right.parent = parent_node
            self.recalculate_subtree_levels(node.right)
            node.right.update_fat_node(self.current_version)

    def find_min_value_node(self, node):
        while node.left is not None:
            node = node.left
        return node

    def delete_node_with_two_children(self, node):
        inorder_successor = self.find_min_value_node(node.right)

        if inorder_successor is node.right:
            inorder_successor.parent.right = inorder_successor.right
        else:
            inorder_successor.parent.left = inorder_successor.right

        if inorder_successor.right:
            inorder_successor.right.parent = inorder_successor.parent
            inorder_successor.right.update_fat_node(self.current_version)  # updating right child

        inorder_successor.parent.update_fat_node(self.current_version)  # updating old parent
        self.recalculate_subtree_levels(inorder_successor.right)

        inorder_successor.left = node.left
        inorder_successor.right = node.right
        inorder_successor.parent = node.parent
        inorder_successor.level = node.level

        if inorder_successor.left:
            inorder_successor.left.parent = inorder_successor
            inorder_successor.left.update_fat_node(self.current_version)

        if inorder_successor.right:
            inorder_successor.right.parent = inorder_successor
            inorder_successor.right.update_fat_node(self.current_version)

        if node is self.root:
            self.root = inorder_successor
        else:
            if node.value > node.parent.value:
                node.parent.right = inorder_successor
            else:
                node.parent.left = inorder_successor
            inorder_successor.parent.update_fat_node(self.current_version)  # updating new parent

        inorder_successor.update_fat_node(self.current_version)

    def recalculate_subtree_levels(self, node):
        if node is None:
            return
        else:
            node.level -= 1
            node.update_fat_node(self.current_version)
            self.recalculate_subtree_levels(node.left)
            self.recalculate_subtree_levels(node.right)

    def recalculate_max_level(self, start_node):
        # todo: check alternate implementation using node.level
        self.max_level = -1

        def inorder_traversal(node):
            if node is None:
                return
            self.max_level = max(self.max_level, node.level)
            inorder_traversal(node.left)
            inorder_traversal(node.right)
        inorder_traversal(start_node)

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
        self.current_version += 1
        node_to_delete = self.find_node(value)
        if node_to_delete is None:
            self.current_version -= 1
            print('no such node')
            return
        elif node_to_delete.left is None and node_to_delete.right is None:
            self.delete_leaf_node(node_to_delete)
        elif (node_to_delete.left is not None) ^ (node_to_delete.right is not None):
            self.delete_node_with_single_child(node_to_delete)
        else:
            self.delete_node_with_two_children(node_to_delete)

        node_to_delete.left = None
        node_to_delete.right = None
        node_to_delete.parent = None
        node_to_delete.update_fat_node(self.current_version)

        self.recalculate_max_level(self.root)
        self.version_max_level[self.current_version] = self.max_level
        self.access_pointers[self.current_version] = self.root

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
        root_node = self.root

        def preorder_traversal(node):
            if node is None:
                return
            print(f"(v: {node}, p: {node.parent if node.parent else None}, l: {node.left}, r: {node.right}, "
                  f"lv: {node.level}, )")
            preorder_traversal(node.left)
            preorder_traversal(node.right)

        preorder_traversal(root_node)
        print(f"max: {self.max_level}")

    def version_specific_postorder_traversal(self, node, tree, level, version):
        if node is None:
            tree[level].append(None)
        else:
            node_version = max(filter(lambda z: z <= version, node.fat_node.version_list))
            tree = self.version_specific_postorder_traversal(node.fat_node.left[node_version], tree,
                                                             node.fat_node.level[node_version]+1, version)
            tree = self.version_specific_postorder_traversal(node.fat_node.right[node_version], tree,
                                                             node.fat_node.level[node_version]+1, version)
            tree[level].append(node.fat_node.value[node_version])
        return tree

    def print_version_specific_tree(self, version):
        if self.current_version < version:
            print(f'Input version cannot be greater than the latest version: {self.current_version}')
            return

        root_node = self.access_pointers.get(version)
        if root_node is None:
            print("empty tree")
            return

        tree = self.version_specific_postorder_traversal(root_node,
                                                         [[] for _ in range(self.version_max_level[version]+2)], 0,
                                                         version)
        print(tree)

    def print_version_specific_nodes(self, version):
        if self.current_version < version:
            print(f'Input version cannot be greater than the latest version: {self.current_version}')
            return

        root_node = self.access_pointers.get(version)
        if root_node is None:
            print("empty tree")
            return

        def preorder_traversal(node):
            if node is None:
                return
            node_version = max(filter(lambda z: z <= version, node.fat_node.version_list))
            parent_version = None
            version_specific_parent = node.fat_node.parent[node_version]
            if version_specific_parent:
                parent_version = max(filter(lambda z: z <= version, version_specific_parent.fat_node.version_list))
            print(f"(v: {node.fat_node.value[node_version]}, "
                  f"p: {version_specific_parent.fat_node.value[parent_version] if parent_version else None}, "
                  f"l: {node.fat_node.left[node_version]}, "
                  f"r: {node.fat_node.right[node_version]}, "
                  f"lv: {node.fat_node.level[node_version]})")

            preorder_traversal(node.fat_node.left[node_version])
            preorder_traversal(node.fat_node.right[node_version])

        preorder_traversal(root_node)
        print(f"max: {self.version_max_level[version]}")

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
        elif op == 5:
            bst.print_version_specific_tree(int(input("version: ")))
        elif op == 6:
            bst.print_version_specific_nodes(int(input("version: ")))
        elif op == 9:
            sys.exit()
