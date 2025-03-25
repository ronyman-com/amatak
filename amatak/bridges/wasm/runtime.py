from wasmer import Instance, Memory, ImportObject, Function
from typing import Dict, Any, Optional, Callable
import os
from ....errors import AmatakRuntimeError
from ....runtime.types.core import (
    IntegerType, FloatType, ArrayType, ObjectType
)
from .compiler import WASMCompiler

class WASMRuntime:
    """Manages execution of WASM modules in Amatak"""
    
    def __init__(self):
        self.compiler = WASMCompiler()
        self._loaded_modules: Dict[str, Instance] = {}
        self._memory = None
        
    def load_module(self, wasm_bytes: bytes, imports: Optional[Dict] = None) -> str:
        """
        Load a WASM module into the runtime.
        
        Args:
            wasm_bytes: WASM binary code
            imports: Import object for WASM imports
            
        Returns:
            Module ID for reference
        """
        try:
            module_id = f"module_{len(self._loaded_modules)}"
            instance = Instance(wasm_bytes, imports or self._get_default_imports())
            self._loaded_modules[module_id] = instance
            self._memory = instance.exports.memory if hasattr(instance.exports, 'memory') else None
            return module_id
        except Exception as e:
            raise AmatakRuntimeError(f"Failed to load WASM module: {str(e)}")
    
    def call_function(self, module_id: str, func_name: str, *args) -> Any:
        """
        Call a function in a loaded WASM module.
        
        Args:
            module_id: ID of loaded module
            func_name: Name of exported function
            args: Arguments to pass
            
        Returns:
            Function return value
        """
        if module_id not in self._loaded_modules:
            raise AmatakRuntimeError(f"Module {module_id} not loaded")
            
        instance = self._loaded_modules[module_id]
        
        if not hasattr(instance.exports, func_name):
            raise AmatakRuntimeError(f"Function {func_name} not found in module")
            
        try:
            func = getattr(instance.exports, func_name)
            return func(*args)
        except Exception as e:
            raise AmatakRuntimeError(f"WASM function call failed: {str(e)}")
    
    def get_memory(self) -> Optional[Memory]:
        """Get the WASM memory instance if available"""
        return self._memory
    
    def _get_default_imports(self) -> ImportObject:
        """Create default import object for WASM modules"""
        imports = ImportObject()
        
        # Basic I/O
        imports.register("env", {
            "print": Function(lambda ptr: print(self._read_string(ptr))),
            "log": Function(lambda val: print(f"[WASM] {val}"))
        })
        
        # Math functions
        imports.register("math", {
            "sin": Function(lambda x: float(x)),
            "cos": Function(lambda x: float(x))
        })
        
        return imports
    
    def _read_string(self, ptr: int) -> str:
        """Read a string from WASM memory"""
        if not self._memory:
            return ""
            
        memory = self._memory.uint8_view()
        length = 0
        while memory[ptr + length] != 0:
            length += 1
            
        bytes_data = bytes(memory[ptr:ptr+length])
        return bytes_data.decode('utf-8')
    
    def _write_string(self, string: str) -> int:
        """Write a string to WASM memory and return pointer"""
        if not self._memory:
            return 0
            
        bytes_data = string.encode('utf-8') + b'\x00'
        ptr = self._alloc(len(bytes_data))
        
        memory = self._memory.uint8_view()
        for i, byte in enumerate(bytes_data):
            memory[ptr + i] = byte
            
        return ptr
    
    def _alloc(self, size: int) -> int:
        """Allocate memory in WASM module"""
        if "alloc" in self._loaded_modules.get("env", {}):
            return self.call_function("env", "alloc", size)
        return 0
    
    def compile_and_run(self, source: str) -> Any:
        """Compile and immediately execute Amatak code"""
        wasm_bytes = self.compiler.compile_amatak_to_wasm(source)
        module_id = self.load_module(wasm_bytes)
        return self.call_function(module_id, "main")