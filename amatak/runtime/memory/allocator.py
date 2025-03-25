import mmap
import os
import ctypes
import platform
from dataclasses import dataclass
from typing import Dict, List, Optional
from ..errors import AmatakMemoryError

@dataclass
class MemoryBlock:
    """Represents a single allocated memory block"""
    address: int
    size: int
    is_executable: bool
    refcount: int = 1

class MemoryAllocator:
    """A custom memory allocator for Amatak runtime"""
    
    def __init__(self):
        self.allocations: Dict[int, MemoryBlock] = {}
        self.free_blocks: Dict[int, List[MemoryBlock]] = {}
        self.page_size = os.sysconf('SC_PAGESIZE')
        self.total_allocated = 0
        self._initialize_memory_pools()
        
        # Platform-specific configurations
        self._configure_for_platform()
        
    def _configure_for_platform(self):
        """Set platform-specific memory parameters"""
        system = platform.system().lower()
        if system == 'linux' or system == 'darwin':
            self.prot_exec = mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC
            self.prot_default = mmap.PROT_READ | mmap.PROT_WRITE
        elif system == 'windows':
            self.prot_exec = 0x40  # PAGE_EXECUTE_READWRITE
            self.prot_default = 0x04  # PAGE_READWRITE
        else:
            raise AmatakMemoryError(f"Unsupported platform: {system}")

    def _initialize_memory_pools(self):
        """Initialize memory pools for different size classes"""
        # Power-of-two size classes from 64 bytes to 1MB
        self.size_classes = [64 * (2**i) for i in range(0, 15)]
        for size in self.size_classes:
            self.free_blocks[size] = []

    def allocate(self, size: int, executable: bool = False) -> int:
        """
        Allocate memory block
        
        Args:
            size: Size in bytes to allocate
            executable: Whether memory should be executable
            
        Returns:
            Memory address of allocated block
        """
        if size <= 0:
            raise AmatakMemoryError("Allocation size must be positive")
            
        # Round up to nearest size class
        size_class = next(sc for sc in self.size_classes if sc >= size)
        
        # Try to reuse free block first
        if self.free_blocks[size_class]:
            block = self.free_blocks[size_class].pop()
            block.is_executable = executable
            block.refcount = 1
            self._set_memory_protection(block.address, block.size, executable)
            return block.address
            
        # Allocate new memory
        try:
            # Align size to page boundary
            aligned_size = ((size + self.page_size - 1) // self.page_size) * self.page_size
            
            # Allocate memory with mmap
            prot = self.prot_exec if executable else self.prot_default
            mem = mmap.mmap(-1, aligned_size, prot=prot)
            
            # Get address and create block
            address = ctypes.addressof(ctypes.c_char.from_buffer(mem))
            block = MemoryBlock(address, aligned_size, executable)
            
            self.allocations[address] = block
            self.total_allocated += aligned_size
            return address
            
        except Exception as e:
            raise AmatakMemoryError(f"Memory allocation failed: {str(e)}")

    def allocate_executable(self, size: int) -> int:
        """Allocate executable memory block"""
        return self.allocate(size, executable=True)

    def reallocate(self, address: int, new_size: int) -> int:
        """
        Reallocate memory block to new size
        
        Args:
            address: Original memory address
            new_size: New size in bytes
            
        Returns:
            New memory address (may be same as original)
        """
        if address not in self.allocations:
            raise AmatakMemoryError("Invalid memory address for reallocation")
            
        old_block = self.allocations[address]
        
        if new_size <= old_block.size:
            # Can reuse the same block if shrinking
            return address
            
        # Allocate new block
        new_address = self.allocate(new_size, old_block.is_executable)
        
        # Copy data from old block
        try:
            ctypes.memmove(
                new_address,
                old_block.address,
                min(old_block.size, new_size)
            )
        except Exception as e:
            self.free(new_address)
            raise AmatakMemoryError(f"Memory reallocation failed: {str(e)}")
            
        # Free old block
        self.free(address)
        
        return new_address

    def free(self, address: int) -> None:
        """
        Free allocated memory
        
        Args:
            address: Memory address to free
        """
        if address not in self.allocations:
            raise AmatakMemoryError("Attempt to free invalid memory address")
            
        block = self.allocations[address]
        block.refcount -= 1
        
        if block.refcount <= 0:
            # Find appropriate size class
            size_class = next(sc for sc in self.size_classes if sc >= block.size)
            
            # Add to free list for reuse
            self.free_blocks[size_class].append(block)
            del self.allocations[address]
            self.total_allocated -= block.size

    def reference(self, address: int) -> None:
        """
        Increment reference count for memory block
        
        Args:
            address: Memory address to reference
        """
        if address not in self.allocations:
            raise AmatakMemoryError("Attempt to reference invalid memory address")
        self.allocations[address].refcount += 1

    def _set_memory_protection(self, address: int, size: int, executable: bool) -> None:
        """
        Set memory protection flags
        
        Args:
            address: Memory address
            size: Size of memory region
            executable: Whether memory should be executable
        """
        try:
            if platform.system().lower() in ['linux', 'darwin']:
                # Use mprotect on Unix-like systems
                libc = ctypes.CDLL(None)
                prot = self.prot_exec if executable else self.prot_default
                aligned_addr = address & ~(self.page_size - 1)
                aligned_size = ((address + size + self.page_size - 1) & ~(self.page_size - 1)) - aligned_addr
                result = libc.mprotect(aligned_addr, aligned_size, prot)
                if result != 0:
                    raise AmatakMemoryError("Failed to set memory protection")
            else:
                # On Windows, protection is set at allocation time
                pass
        except Exception as e:
            raise AmatakMemoryError(f"Memory protection change failed: {str(e)}")

    def get_usage_stats(self) -> dict:
        """
        Get memory usage statistics
        
        Returns:
            Dictionary with allocation statistics
        """
        return {
            'total_allocated': self.total_allocated,
            'active_blocks': len(self.allocations),
            'free_blocks': sum(len(blocks) for blocks in self.free_blocks.values()),
            'size_class_usage': {
                size: len(blocks) for size, blocks in self.free_blocks.items()
            }
        }

    def cleanup(self) -> None:
        """Clean up all allocated memory"""
        for address in list(self.allocations.keys()):
            self.free(address)
        self.free_blocks = {size: [] for size in self.size_classes}
        self.total_allocated = 0

    def __del__(self):
        self.cleanup()