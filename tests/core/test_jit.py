import pytest
from amatak.core.jit import JITCompiler
from amatak.core.ast import BinOpNode, NumberNode

class TestJITCompiler:
    @pytest.fixture
    def jit(self):
        return JITCompiler()

    def test_compile_simple_expression(self, jit):
        # Test basic arithmetic compilation
        ast = BinOpNode(
            left=NumberNode(5),
            op='+',
            right=NumberNode(3)
        )
        
        compiled_fn = jit.compile(ast)
        assert compiled_fn() == 8

    def test_compile_with_variables(self, jit):
        # Test compilation with variable access
        ast = BinOpNode(
            left=VariableNode('x'),
            op='*',
            right=NumberNode(2)
        )
        
        compiled_fn = jit.compile(ast)
        assert compiled_fn({'x': 5}) == 10

    def test_optimization(self, jit):
        # Test constant folding optimization
        ast = BinOpNode(
            left=BinOpNode(
                left=NumberNode(2),
                op='+',
                right=NumberNode(3)
            ),
            op='*',
            right=NumberNode(4)
        )
        
        compiled_fn = jit.compile(ast, optimize=True)
        assert compiled_fn() == 20

    def test_function_call(self, jit):
        # Test function call compilation
        ast = CallNode(
            func='square',
            args=[NumberNode(4)]
        )
        
        env = {
            'square': lambda x: x * x
        }
        
        compiled_fn = jit.compile(ast)
        assert compiled_fn(env) == 16

    def test_error_handling(self, jit):
        # Test invalid AST handling
        with pytest.raises(ValueError):
            jit.compile("invalid ast")