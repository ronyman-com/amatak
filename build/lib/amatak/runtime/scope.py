class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.constants = set()

    def declare(self, name, value, is_const=False):
        """Declare a variable in current scope"""
        if name in self.variables:
            raise NameError(f"Variable '{name}' already declared")
        
        self.variables[name] = value
        if is_const:
            self.constants.add(name)

    def assign(self, name, value):
        """Assign a value to variable"""
        if name in self.variables:
            if name in self.constants:
                raise ValueError(f"Cannot reassign constant '{name}'")
            self.variables[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise NameError(f"Undefined variable '{name}'")

    def get(self, name):
        """Get variable value"""
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Undefined variable '{name}'")

    def create_child(self):
        """Create a new nested scope"""
        return Scope(parent=self)