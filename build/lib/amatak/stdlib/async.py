class Promise:
    def __init__(self, executor):
        self.state = 'pending'
        self.value = None
        self.handlers = []
        
        def resolve(value):
            self.state = 'fulfilled'
            self.value = value
            for handler in self.handlers:
                handler(value)
                
        executor(resolve)

    def then(self, handler):
        if self.state == 'fulfilled':
            handler(self.value)
        else:
            self.handlers.append(handler)
        return self