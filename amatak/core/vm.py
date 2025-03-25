import struct
from enum import Enum, auto
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..errors import AmatakRuntimeError
from ..runtime.memory.allocator import MemoryAllocator
from ..runtime.types.core import AmatakType, DynamicType
from .jit import JITCompiler

class OpCode(Enum):
    """Bytecode operation codes"""
    LOAD_CONST = auto()
    LOAD_VAR = auto()
    STORE_VAR = auto()
    LOAD_ARG = auto()
    CALL_FUNCTION = auto()
    RETURN = auto()
    BINARY_ADD = auto()
    BINARY_SUB = auto()
    BINARY_MUL = auto()
    BINARY_DIV = auto()
    COMPARE_EQ = auto()
    COMPARE_GT = auto()
    COMPARE_LT = auto()
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    MAKE_FUNCTION = auto()
    MAKE_ARRAY = auto()
    ARRAY_GET = auto()
    ARRAY_SET = auto()

@dataclass
class Function:
    name: str
    arg_count: int
    bytecode: bytes
    constants: List[Any]
    local_count: int
    returns: AmatakType = DynamicType()

class VM:
    def __init__(self, jit_enabled: bool = True):
        self.stack: List[Any] = []
        self.frames: List[Dict[str, Any]] = [{}]
        self.functions: Dict[str, Function] = {}
        self.constants: List[Any] = []
        self.memory = MemoryAllocator()
        self.jit = JITCompiler(self) if jit_enabled else None
        self.current_function: Optional[Function] = None
        self.pc = 0  # Program counter
        self.running = False

    def execute(self, bytecode: bytes) -> Any:
        """Execute bytecode in the VM"""
        self.running = True
        self.pc = 0
        
        try:
            while self.running and self.pc < len(bytecode):
                op = OpCode(bytecode[self.pc])
                self.pc += 1
                self._dispatch(op, bytecode)
                
                # Check for JIT opportunities
                if self.jit and self.current_function:
                    self.jit.record_call(self.current_function.name)
                    if self.jit.should_compile(self.current_function.name):
                        self.jit.compile_function(
                            self.current_function.name,
                            self.current_function.bytecode
                        )
        except Exception as e:
            raise AmatakRuntimeError(f"VM execution error: {str(e)}")
        
        return self.stack.pop() if self.stack else None

    def _dispatch(self, op: OpCode, bytecode: bytes):
        """Dispatch to operation handlers"""
        handlers = {
            OpCode.LOAD_CONST: self._load_const,
            OpCode.LOAD_VAR: self._load_var,
            OpCode.STORE_VAR: self._store_var,
            OpCode.LOAD_ARG: self._load_arg,
            OpCode.CALL_FUNCTION: self._call_function,
            OpCode.RETURN: self._return,
            OpCode.BINARY_ADD: self._binary_add,
            OpCode.BINARY_SUB: self._binary_sub,
            OpCode.BINARY_MUL: self._binary_mul,
            OpCode.BINARY_DIV: self._binary_div,
            OpCode.COMPARE_EQ: self._compare_eq,
            OpCode.COMPARE_GT: self._compare_gt,
            OpCode.COMPARE_LT: self._compare_lt,
            OpCode.JUMP: self._jump,
            OpCode.JUMP_IF_FALSE: self._jump_if_false,
            OpCode.MAKE_FUNCTION: self._make_function,
            OpCode.MAKE_ARRAY: self._make_array,
            OpCode.ARRAY_GET: self._array_get,
            OpCode.ARRAY_SET: self._array_set,
        }
        handlers[op](bytecode)

    def _load_const(self, bytecode: bytes):
        """Load constant onto stack"""
        const_idx = self._read_uint16(bytecode)
        self.stack.append(self.constants[const_idx])

    def _load_var(self, bytecode: bytes):
        """Load variable onto stack"""
        var_name = self._read_string(bytecode)
        for frame in reversed(self.frames):
            if var_name in frame:
                self.stack.append(frame[var_name])
                return
        raise AmatakRuntimeError(f"Undefined variable: {var_name}")

    def _store_var(self, bytecode: bytes):
        """Store top of stack in variable"""
        var_name = self._read_string(bytecode)
        self.frames[-1][var_name] = self.stack[-1]

    def _load_arg(self, bytecode: bytes):
        """Load function argument"""
        arg_idx = self._read_uint8(bytecode)
        self.stack.append(self.frames[-1][f"arg{arg_idx}"])

    def _call_function(self, bytecode: bytes):
        """Call a function"""
        func_name = self._read_string(bytecode)
        arg_count = self._read_uint8(bytecode)
        
        # Try JIT first if available
        if self.jit and func_name in self.jit.compiled_functions:
            args = self.stack[-arg_count:]
            result = self.jit.execute_native(func_name, *args)
            self.stack = self.stack[:-arg_count] + [result]
            return
        
        # Fall back to interpreted mode
        if func_name not in self.functions:
            raise AmatakRuntimeError(f"Undefined function: {func_name}")
        
        func = self.functions[func_name]
        if arg_count != func.arg_count:
            raise AmatakRuntimeError(
                f"Function {func_name} expects {func.arg_count} args, got {arg_count}"
            )
        
        # Setup new frame
        new_frame = {}
        for i in range(arg_count):
            new_frame[f"arg{i}"] = self.stack[-arg_count + i]
        
        self.frames.append(new_frame)
        self.current_function = func
        
        # Save state
        saved_pc = self.pc
        saved_stack = self.stack[:-arg_count]
        
        # Execute function
        self.stack = []
        self.pc = 0
        self.execute(func.bytecode)
        result = self.stack.pop() if self.stack else None
        
        # Restore state
        self.stack = saved_stack + [result]
        self.frames.pop()
        self.pc = saved_pc
        self.current_function = None

    def _return(self, bytecode: bytes):
        """Return from function"""
        self.running = False

    def _binary_add(self, bytecode: bytes):
        """Binary addition"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left + right)

    def _binary_sub(self, bytecode: bytes):
        """Binary subtraction"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left - right)

    def _binary_mul(self, bytecode: bytes):
        """Binary multiplication"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left * right)

    def _binary_div(self, bytecode: bytes):
        """Binary division"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left / right)

    def _compare_eq(self, bytecode: bytes):
        """Equality comparison"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left == right)

    def _compare_gt(self, bytecode: bytes):
        """Greater than comparison"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left > right)

    def _compare_lt(self, bytecode: bytes):
        """Less than comparison"""
        right = self.stack.pop()
        left = self.stack.pop()
        self.stack.append(left < right)

    def _jump(self, bytecode: bytes):
        """Unconditional jump"""
        offset = self._read_int16(bytecode)
        self.pc += offset

    def _jump_if_false(self, bytecode: bytes):
        """Conditional jump"""
        offset = self._read_int16(bytecode)
        if not self.stack.pop():
            self.pc += offset

    def _make_function(self, bytecode: bytes):
        """Create function object"""
        name = self._read_string(bytecode)
        arg_count = self._read_uint8(bytecode)
        bytecode_len = self._read_uint16(bytecode)
        func_bytecode = bytecode[self.pc:self.pc + bytecode_len]
        self.pc += bytecode_len
        
        self.functions[name] = Function(
            name=name,
            arg_count=arg_count,
            bytecode=func_bytecode,
            constants=self.constants.copy(),
            local_count=self._read_uint8(bytecode)
        )

    def _make_array(self, bytecode: bytes):
        """Create array"""
        size = self._read_uint16(bytecode)
        elements = self.stack[-size:]
        self.stack = self.stack[:-size] + [elements]

    def _array_get(self, bytecode: bytes):
        """Array index access"""
        index = self.stack.pop()
        array = self.stack.pop()
        self.stack.append(array[index])

    def _array_set(self, bytecode: bytes):
        """Array index assignment"""
        value = self.stack.pop()
        index = self.stack.pop()
        array = self.stack.pop()
        array[index] = value
        self.stack.append(value)

    def _read_uint8(self, bytecode: bytes) -> int:
        """Read unsigned 8-bit integer"""
        val = bytecode[self.pc]
        self.pc += 1
        return val

    def _read_uint16(self, bytecode: bytes) -> int:
        """Read unsigned 16-bit integer"""
        val = struct.unpack_from('>H', bytecode, self.pc)[0]
        self.pc += 2
        return val

    def _read_int16(self, bytecode: bytes) -> int:
        """Read signed 16-bit integer"""
        val = struct.unpack_from('>h', bytecode, self.pc)[0]
        self.pc += 2
        return val

    def _read_string(self, bytecode: bytes) -> str:
        """Read length-prefixed string"""
        length = self._read_uint16(bytecode)
        val = bytecode[self.pc:self.pc + length].decode('utf-8')
        self.pc += length
        return val

    def get_function_bytecode(self, func_name: str) -> Optional[bytes]:
        """Get bytecode for a function (for JIT compilation)"""
        if func_name in self.functions:
            return self.functions[func_name].bytecode
        return None