import os
import ctypes
import platform
from typing import Optional, Dict, Any
from ....errors import AmatakRuntimeError

class LinuxNative:
    """Linux-specific native implementations and system calls"""
    
    def __init__(self):
        self._libc = ctypes.CDLL("libc.so.6")
        self._system_info = self._get_system_info()
        
        # Setup ctypes for common Linux syscalls
        self._libc.malloc.argtypes = [ctypes.c_size_t]
        self._libc.malloc.restype = ctypes.c_void_p
        
        self._libc.free.argtypes = [ctypes.c_void_p]
        self._libc.free.restype = None
        
        self._libc.syscall.argtypes = [ctypes.c_long]
        self._libc.syscall.restype = ctypes.c_long
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get Linux system information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'libc_version': self._get_libc_version()
        }
    
    def _get_libc_version(self) -> str:
        """Get glibc version"""
        try:
            return os.confstr('CS_GNU_LIBC_VERSION')
        except:
            return "unknown"
    
    def memory_alloc(self, size: int) -> int:
        """Allocate memory using libc malloc"""
        ptr = self._libc.malloc(size)
        if not ptr:
            raise AmatakRuntimeError("Failed to allocate memory")
        return ptr
    
    def memory_free(self, ptr: int):
        """Free allocated memory"""
        self._libc.free(ptr)
    
    def syscall(self, number: int, *args) -> int:
        """Make Linux system call"""
        # Convert args to ctypes compatible types
        c_args = []
        for arg in args:
            if isinstance(arg, int):
                c_args.append(ctypes.c_long(arg))
            elif isinstance(arg, str):
                c_args.append(ctypes.c_char_p(arg.encode()))
            else:
                c_args.append(ctypes.c_void_p(arg))
        
        # Make the syscall (max 6 args supported)
        result = self._libc.syscall(
            ctypes.c_long(number),
            *c_args[:6]  # Linux syscalls typically take up to 6 args
        )
        
        if result < 0:
            errno = ctypes.get_errno()
            raise AmatakRuntimeError(f"Syscall failed with errno {errno}")
        return result
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        return self._system_info
    
    def file_descriptor_count(self) -> int:
        """Get number of open file descriptors"""
        try:
            return len(os.listdir(f"/proc/{os.getpid()}/fd"))
        except Exception as e:
            raise AmatakRuntimeError(f"Could not count file descriptors: {str(e)}")
    
    def process_memory(self) -> Dict[str, int]:
        """Get process memory usage in bytes"""
        try:
            with open(f"/proc/{os.getpid()}/status") as f:
                data = f.read()
            
            mem_info = {}
            for line in data.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    mem_info[key.strip()] = val.strip()
            
            return {
                'vm_size': int(mem_info.get('VmSize', '0 kB').split()[0]) * 1024,
                'vm_rss': int(mem_info.get('VmRSS', '0 kB').split()[0]) * 1024,
                'vm_peak': int(mem_info.get('VmPeak', '0 kB').split()[0]) * 1024
            }
        except Exception as e:
            raise AmatakRuntimeError(f"Could not read process memory: {str(e)}")

# Singleton instance
linux_native = LinuxNative()