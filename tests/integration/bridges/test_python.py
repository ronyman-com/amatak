import pytest
from amatak.bridges.python import PythonImporter
import math

class TestPythonBridge:
    @pytest.fixture
    def importer(self):
        return PythonImporter()

    def test_import_module(self, importer):
        # Test standard module import
        math_module = importer.import_module('math')
        assert 'sqrt' in math_module
        assert math_module['sqrt'](4) == 2.0

    def test_import_from(self, importer):
        # Test selective imports
        imports = importer.import_from('math', ['pi', 'e'])
        assert abs(imports['pi'] - 3.14159) < 0.0001
        assert abs(imports['e'] - 2.71828) < 0.0001

    def test_function_calling(self, importer):
        # Test function calls with conversion
        math_module = importer.import_module('math')
        sqrt = math_module['sqrt']
        assert sqrt(9) == 3.0

    def test_object_marshaling(self, importer):
        # Test Python object marshaling
        class TestClass:
            def __init__(self, x):
                self.x = x
            
            def get_x(self):
                return self.x
        
        obj = TestClass(5)
        marshaled = importer._marshal.marshal(obj)
        assert marshaled['x'] == 5
        assert marshaled['get_x']() == 5

    def test_error_handling(self, importer):
        # Test error handling for invalid imports
        with pytest.raises(RuntimeError):
            importer.import_module('nonexistent_module')