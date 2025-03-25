import { Component, Router, App } from amatak.web.components.core

# Create components
class Header(Component):
    def render(self):
        return '''
            <header>
                <h1>{self.props.title}</h1>
            </header>
        '''

class HomePage(Component):
    def render(self):
        return '''
            <div>
                <h2>Welcome</h2>
                <p>{self.props.content}</p>
            </div>
        '''

# Setup application
app = App()
router = Router()

router.add_route('/', HomePage(props={
    content: "This is the home page" 
}))

app.register_component('header', Header(props={
    title: "My Amatak App"
}))

# Start the app
app.start()