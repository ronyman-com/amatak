class ASTNode:
    pass

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value