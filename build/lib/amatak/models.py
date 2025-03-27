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




class ArrayNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class ArrayAccessNode(ASTNode):
    def __init__(self, array, index):
        self.array = array
        self.index = index

class ArrayAssignNode(ASTNode):
    def __init__(self, array, index, value):
        self.array = array
        self.index = index
        self.value = value

class ArrayMethodNode(ASTNode):
    def __init__(self, array, method, args=None):
        self.array = array
        self.method = method  # 'push' or 'pop'
        self.args = args or []

class ForNode(ASTNode):
    def __init__(self, var_name, start, end, step, body):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.step = step
        self.body = body