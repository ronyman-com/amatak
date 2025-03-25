import ctypes
import mmap
import platform
import struct
from dataclasses import dataclass
from typing import Dict, List, Optional
from .vm import OpCode, VM
from ..errors import AmatakRuntimeError
from ..runtime.memory.allocator import MemoryAllocator
from ..runtime.types.core import AmatakType

@dataclass
class NativeFunction:
    address: int
    arg_count: int
    return_type: AmatakType

class JITCompiler:
    def __init__(self, vm: VM):
        self.vm = vm
        self.memory = MemoryAllocator()
        self.compiled_functions: Dict[str, NativeFunction] = {}
        self.platform = platform.machine().lower()
        
        # Architecture-specific configurations
        self.arch_config = {
            'x86_64': {
                'register_args': ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9'],
                'return_reg': 'rax',
                'call_conv': self._compile_x86_64
            },
            'arm64': {
                'register_args': ['x0', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7'],
                'return_reg': 'x0',
                'call_conv': self._compile_arm64
            }
        }

    def compile_function(self, func_name: str, bytecode: bytes) -> NativeFunction:
        """Compile Amatak bytecode to native machine code"""
        if func_name in self.compiled_functions:
            return self.compiled_functions[func_name]
        
        # Get architecture-specific compiler
        compiler = self.arch_config.get(self.platform)
        if not compiler:
            raise AmatakRuntimeError(f"JIT not supported on {self.platform}")

        # Generate native code
        native_code = compiler['call_conv'](bytecode)
        
        # Allocate executable memory
        exec_mem = self.memory.allocate_executable(len(native_code))
        ctypes.memmove(exec_mem, native_code, len(native_code))
        
        # Create function wrapper
        func_type = ctypes.CFUNCTYPE(ctypes.c_void_p, *[ctypes.c_void_p]*6)
        native_func = func_type(exec_mem)
        
        # Store metadata
        compiled = NativeFunction(
            address=exec_mem,
            arg_count=self._count_args(bytecode),
            return_type=self._get_return_type(bytecode)
        )
        self.compiled_functions[func_name] = compiled
        
        return compiled

    def _compile_x86_64(self, bytecode: bytes) -> bytes:
        """Generate x86_64 machine code"""
        # Prologue
        code = b'\x55'                           # push rbp
        code += b'\x48\x89\xE5'                  # mov rbp, rsp
        
        # TODO: Implement actual bytecode translation
        # This is a placeholder that just returns 42
        code += b'\x48\xC7\xC0\x2A\x00\x00\x00' # mov rax, 42
        
        # Epilogue
        code += b'\x5D'                           # pop rbp
        code += b'\xC3'                           # ret
        
        return code

    def _compile_arm64(self, bytecode: bytes) -> bytes:
        """Generate ARM64 machine code"""
        # Prologue
        code = b'\xFD\x03\x00\x91'               # mov x29, sp
        
        # TODO: Implement actual bytecode translation
        # This is a placeholder that just returns 42
        code += b'\x28\x00\x80\xD2'              # mov x0, #42
        
        # Epilogue
        code += b'\xFD\x03\x00\x91'              # mov sp, x29
        code += b'\xC0\x03\x5F\xD6'              # ret
        
        return code

    def _count_args(self, bytecode: bytes) -> int:
        """Count arguments from bytecode"""
        # Simple implementation - count LOAD_ARG ops
        return bytecode.count(OpCode.LOAD_ARG.value)

    def _get_return_type(self, bytecode: bytes) -> AmatakType:
        """Determine return type from bytecode"""
        # Default to dynamic type for now
        from ..runtime.types.core import DynamicType
        return DynamicType()

    def execute_native(self, func_name: str, *args) -> object:
        """Execute a compiled native function"""
        if func_name not in self.compiled_functions:
            raise AmatakRuntimeError(f"Function {func_name} not compiled")
        
        func = self.compiled_functions[func_name]
        
        # Convert Python args to C types
        c_args = []
        for arg in args:
            if isinstance(arg, int):
                c_args.append(ctypes.c_long(arg))
            elif isinstance(arg, float):
                c_args.append(ctypes.c_double(arg))
            else:
                c_args.append(ctypes.py_object(arg))
        
        # Call the native function
        func_type = ctypes.CFUNCTYPE(ctypes.py_object, *[type(arg) for arg in c_args])
        native_func = func_type(func.address)
        return native_func(*args)

    def warmup(self, functions: Dict[str, bytes]):
        """Pre-compile frequently used functions"""
        for name, bytecode in functions.items():
            self.compile_function(name, bytecode)

class JITContext:
    """Runtime context for JIT compilation"""
    def __init__(self, vm: VM):
        self.jit = JITCompiler(vm)
        self.hot_functions: Dict[str, int] = {}  # function_name -> call_count
        
    def should_compile(self, func_name: str) -> bool:
        """Determine if a function should be JIT compiled"""
        return self.hot_functions.get(func_name, 0) > 10
        
    def record_call(self, func_name: str):
        """Track function call frequency"""
        self.hot_functions[func_name] = self.hot_functions.get(func_name, 0) + 1
        
    def compile_hot_functions(self):
        """Compile frequently called functions"""
        for func_name, count in self.hot_functions.items():
            if count > 10 and func_name not in self.jit.compiled_functions:
                # Get bytecode from VM
                bytecode = self.jit.vm.get_function_bytecode(func_name)
                if bytecode:
                    self.jit.compile_function(func_name, bytecode)