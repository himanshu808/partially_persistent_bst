class FatNode:
    def __init__(self, ephemeral_node, version):
        for attr in ephemeral_node.__dict__:
            setattr(self, attr, dict())
            getattr(self, attr)[version] = getattr(ephemeral_node, attr)

        self.version = version
