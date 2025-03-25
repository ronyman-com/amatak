import os
import ctypes
import platform
from ctypes import wintypes
from typing import Optional, Dict, Any
from ....errors import AmatakRuntimeError

# Windows API types and constants
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)

# Windows API function prototypes
kernel32.GetProcessMemoryInfo.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.PROCESS_MEMORY_COUNTERS),
    wintypes.DWORD
]
kernel32.GetProcessMemoryInfo.restype = wintypes.BOOL

kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
kernel32.GlobalFree.restype = wintypes.HGLOBAL

class WindowsNative:
    """Windows-specific native implementations and system calls"""
    
    def __init__(self):
        self._system_info = self._get_system_info()
        self._process_handle = kernel32.GetCurrentProcess()
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get Windows system information"""
        class OSVERSIONINFOEX(ctypes.Structure):
            _fields_ = [
                ("dwOSVersionInfoSize", wintypes.DWORD),
                ("dwMajorVersion", wintypes.DWORD),
                ("dwMinorVersion", wintypes.DWORD),
                ("dwBuildNumber", wintypes.DWORD),
                ("dwPlatformId", wintypes.DWORD),
                ("szCSDVersion", wintypes.CHAR * 128),
                ("wServicePackMajor", wintypes.WORD),
                ("wServicePackMinor", wintypes.WORD),
                ("wSuiteMask", wintypes.WORD),
                ("wProductType", wintypes.BYTE),
                ("wReserved", wintypes.BYTE)
            ]
        
        os_info = OSVERSIONINFOEX()
        os_info.dwOSVersionInfoSize = ctypes.sizeof(OSVERSIONINFOEX)
        
        if not kernel32.GetVersionExW(ctypes.byref(os_info)):
            raise AmatakRuntimeError("Could not get Windows version info")
        
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'windows_version': f"{os_info.dwMajorVersion}.{os_info.dwMinorVersion}",
            'build_number': os_info.dwBuildNumber,
            'service_pack': f"{os_info.wServicePackMajor}.{os_info.wServicePackMinor}"
        }
    
    def memory_alloc(self, size: int) -> int:
        """Allocate memory using GlobalAlloc"""
        ptr = kernel32.GlobalAlloc(0x0040, size)  # GHND = GMEM_MOVEABLE | GMEM_ZEROINIT
        if not ptr:
            raise AmatakRuntimeError("Failed to allocate memory")
        return ptr
    
    def memory_free(self, ptr: int):
        """Free allocated memory"""
        if not kernel32.GlobalFree(ptr) == 0:
            raise AmatakRuntimeError("Failed to free memory")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        return self._system_info
    
    def process_memory(self) -> Dict[str, int]:
        """Get process memory usage in bytes"""
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t)
            ]
        
        mem_counters = PROCESS_MEMORY_COUNTERS()
        mem_counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        
        if not kernel32.GetProcessMemoryInfo(
            self._process_handle,
            ctypes.byref(mem_counters),
            mem_counters.cb
        ):
            raise AmatakRuntimeError("Could not get process memory info")
        
        return {
            'working_set': mem_counters.WorkingSetSize,
            'peak_working_set': mem_counters.PeakWorkingSetSize,
            'pagefile': mem_counters.PagefileUsage,
            'peak_pagefile': mem_counters.PeakPagefileUsage
        }
    
    def file_handle_count(self) -> int:
        """Get number of open file handles"""
        try:
            import psutil
            return len(psutil.Process().handles())
        except ImportError:
            raise AmatakRuntimeError("psutil required for handle count on Windows")
        except Exception as e:
            raise AmatakRuntimeError(f"Could not count file handles: {str(e)}")
    
    def registry_read(self, key_path: str, value_name: str) -> Any:
        """Read a value from Windows Registry"""
        try:
            import winreg
            hive, subkey = key_path.split('\\', 1)
            
            # Map hive names to constants
            hives = {
                'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                'HKEY_USERS': winreg.HKEY_USERS,
                'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
            }
            
            if hive not in hives:
                raise AmatakRuntimeError(f"Unknown registry hive: {hive}")
            
            with winreg.OpenKey(hives[hive], subkey) as key:
                value, regtype = winreg.QueryValueEx(key, value_name)
                return value
        except Exception as e:
            raise AmatakRuntimeError(f"Registry read failed: {str(e)}")

# Singleton instance
windows_native = WindowsNative()