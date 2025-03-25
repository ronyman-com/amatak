import pytest
from amatak.bridges.wasm import WASMRuntime
import os

# Simple WASM module that exports an add function
SIMPLE_WASM = bytes([
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x01, 0x07, 0x01, 0x60, 0x02, 0x7f, 0x7f, 0x7f,
    0x03, 0x02, 0x01, 0x00, 0x07, 0x07, 0x01, 0x03,
    0x61, 0x64, 0x64, 0x00, 0x00, 0x0a, 0x09, 0x01,
    0x07, 0x00, 0x20, 0x00, 0x20, 0x01, 0x6a, 0x0b
])

class TestWASMBridge:
    @pytest.fixture
    def runtime(self):
        return WASMRuntime()

    def test_module_loading(self, runtime):
        # Test basic module loading
        module_id = runtime.load_module(SIMPLE_WASM)
        assert module_id.startswith("module_")
        assert module_id in runtime._loaded_modules

    def test_function_calling(self, runtime):
        # Test calling WASM functions
        runtime.load_module(SIMPLE_WASM)
        result = runtime.call_function("module_0", "add", 5, 3)
        assert result == 8

    def test_memory_operations(self, runtime):
        # Test memory read/write operations
        runtime.load_module(SIMPLE_WASM)
        
        # Test string handling
        test_str = "hello"
        ptr = runtime._write_string(test_str)
        assert ptr != 0
        
        read_str = runtime._read_string(ptr)
        assert read_str == test_str

    def test_error_handling(self, runtime):
        # Test error handling for invalid modules
        with pytest.raises(RuntimeError):
            runtime.load_module(b'invalid wasm')
        
        # Test error handling for invalid functions
        runtime.load_module(SIMPLE_WASM)
        with pytest.raises(RuntimeError):
            runtime.call_function("module_0", "nonexistent", 1, 2)

    def test_compile_and_run(self, runtime):
        # Test end-to-end compilation and execution
        # Note: This requires the compiler to be properly implemented
        try:
            result = runtime.compile_and_run("func main() { return 42 }")
            assert result == 42
        except NotImplementedError:
            pytest.skip("WASM compilation not fully implemented")