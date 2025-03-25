from amatak.error_handling import error_handler
from amatak.security.middleware import security_middleware

def create_component(name, definition):
    """
    Create a new component type dynamically
    
    Args:
        name: Component name
        definition: Dictionary with:
            - template: HTML template
            - styles: CSS styles
            - methods: Component methods
    """
    @error_handler.wrap_operation
    def constructor(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)
        self.template = definition.get('template', '')
        self.styles = definition.get('styles', {})
        
        # Add methods
        for method_name, method in definition.get('methods', {}).items():
            setattr(self, method_name, method)
    
    # Create new component class
    new_class = type(
        name,
        (Component,),
        {
            '__init__': constructor,
            'render': lambda self: self.template
        }
    )
    
    return security_middleware.secure_operation(new_class)

def hydrate(element, component_class):
    """
    Hydrate server-rendered HTML with component functionality
    
    Args:
        element: DOM element to hydrate
        component_class: Component class to use
    """
    @error_handler.wrap_operation
    def do_hydrate():
        props = {}
        data_attrs = element.dataset
        for key in data_attrs:
            try:
                props[key] = JSON.parse(data_attrs[key])
            except:
                props[key] = data_attrs[key]
        
        component = component_class(element=element, props=props)
        return component
    
    return do_hydrate()

# Export component utilities
export create_component, hydrate