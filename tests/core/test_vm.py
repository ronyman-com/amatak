import pytest
from amatak.core.vm import VM
from amatak.core.bytecode import (
    Bytecode, OpCode, Instruction
)

class TestVirtualMachine:
    @pytest.fixture
    def vm(self):
        return VM()

    def test_execute_simple_program(self, vm):
        # Test basic arithmetic operations
        bytecode = Bytecode([
            Instruction(OpCode.LOAD_CONST, 5),
            Instruction(OpCode.LOAD_CONST, 3),
            Instruction(OpCode.ADD),
            Instruction(OpCode.RETURN)
        ])
        
        result = vm.execute(bytecode)
        assert result == 8

    def test_variable_operations(self, vm):
        # Test variable loading and storage
        bytecode = Bytecode([
            Instruction(OpCode.LOAD_NAME, 'x'),
            Instruction(OpCode.LOAD_CONST, 2),
            Instruction(OpCode.MULTIPLY),
            Instruction(OpCode.RETURN)
        ])
        
        result = vm.execute(bytecode, {'x': 7})
        assert result == 14

    def test_control_flow(self, vm):
        # Test jumps and conditional execution
        bytecode = Bytecode([
            Instruction(OpCode.LOAD_NAME, 'x'),
            Instruction(OpCode.JUMP_IF_FALSE, 6),
            Instruction(OpCode.LOAD_CONST, 1),
            Instruction(OpCode.RETURN),
            Instruction(OpCode.LOAD_CONST, 0),
            Instruction(OpCode.RETURN)
        ])
        
        assert vm.execute(bytecode, {'x': True}) == 1
        assert vm.execute(bytecode, {'x': False}) == 0

    def test_function_calls(self, vm):
        # Test function calls and returns
        bytecode = Bytecode([
            Instruction(OpCode.LOAD_NAME, 'square'),
            Instruction(OpCode.LOAD_CONST, 4),
            Instruction(OpCode.CALL_FUNCTION, 1),
            Instruction(OpCode.RETURN)
        ])
        
        env = {
            'square': lambda x: x * x
        }
        
        assert vm.execute(bytecode, env) == 16

    def test_stack_underflow(self, vm):
        # Test error handling for stack underflow
        bytecode = Bytecode([
            Instruction(OpCode.ADD)
        ])
        
        with pytest.raises(RuntimeError):
            vm.execute(bytecode)