import time
from typing import Dict, Set, List, Optional
from weakref import WeakValueDictionary
from ..errors import AmatakRuntimeError
from .allocator import MemoryAllocator
from ..types.core import AmatakObject, AmatakType

class GarbageCollector:
    """A generational garbage collector for Amatak runtime"""
    
    def __init__(self, allocator: MemoryAllocator):
        self.allocator = allocator
        
        # Generation 0: Young objects
        self.gen0: Dict[int, AmatakObject] = {}
        # Generation 1: Middle-aged objects
        self.gen1: Dict[int, AmatakObject] = WeakValueDictionary()
        # Generation 2: Old objects
        self.gen2: Dict[int, AmatakObject] = WeakValueDictionary()
        
        # Reference tracking
        self.references: Dict[int, Set[int]] = {}
        self.reverse_refs: Dict[int, Set[int]] = {}
        
        # Collection thresholds
        self.gen0_threshold = 1000
        self.gen1_threshold = 100
        self.collection_count = 0
        self.last_collection_time = time.time()
        
        # Flags
        self.enabled = True
        self.debug = False

    def register_object(self, obj: AmatakObject) -> None:
        """Register a new object with the GC"""
        if not isinstance(obj, AmatakObject):
            raise AmatakRuntimeError("Only AmatakObject instances can be registered")
            
        obj_id = id(obj)
        if obj_id not in self.gen0 and obj_id not in self.gen1 and obj_id not in self.gen2:
            self.gen0[obj_id] = obj
            self.references[obj_id] = set()
            self.reverse_refs[obj_id] = set()
            
            # Check if we need to collect
            if len(self.gen0) >= self.gen0_threshold:
                self.collect()

    def add_reference(self, from_obj: AmatakObject, to_obj: AmatakObject) -> None:
        """Track a reference between two objects"""
        from_id = id(from_obj)
        to_id = id(to_obj)
        
        if from_id in self.references and to_id in self.reverse_refs:
            self.references[from_id].add(to_id)
            self.reverse_refs[to_id].add(from_id)

    def remove_reference(self, from_obj: AmatakObject, to_obj: AmatakObject) -> None:
        """Remove a tracked reference between objects"""
        from_id = id(from_obj)
        to_id = id(to_obj)
        
        if from_id in self.references and to_id in self.reverse_refs:
            self.references[from_id].discard(to_id)
            self.reverse_refs[to_id].discard(from_id)

    def collect(self, generation: Optional[int] = None) -> None:
        """
        Run garbage collection
        
        Args:
            generation: Specific generation to collect (0, 1, or 2)
                       If None, runs generational collection
        """
        if not self.enabled:
            return
            
        start_time = time.time()
        collected = 0
        
        if generation == 0 or generation is None:
            # Mark and sweep for generation 0
            roots = self._find_roots()
            marked = self._mark(roots)
            collected += self._sweep_generation(marked, self.gen0)
            
            # Promote survivors to generation 1
            self._promote_generation(self.gen0, self.gen1)
            
        if generation == 1 or (generation is None and len(self.gen1) >= self.gen1_threshold):
            # Mark and sweep for generation 1
            roots = self._find_roots() | set(self.gen0.keys())
            marked = self._mark(roots)
            collected += self._sweep_generation(marked, self.gen1)
            
            # Promote survivors to generation 2
            self._promote_generation(self.gen1, self.gen2)
            
        if generation == 2 or generation is None:
            # Only collect gen2 if we're explicitly asked
            if generation == 2:
                roots = self._find_roots() | set(self.gen0.keys()) | set(self.gen1.keys())
                marked = self._mark(roots)
                collected += self._sweep_generation(marked, self.gen2)
        
        self.collection_count += 1
        duration = time.time() - start_time
        
        if self.debug:
            print(f"GC: Collected {collected} objects in {duration:.3f}s")

    def _find_roots(self) -> Set[int]:
        """Find root objects (stack, globals, etc.)"""
        # TODO: Implement actual root finding from interpreter
        # For now, return empty set - real implementation would track:
        # - Stack references
        # - Global variables
        # - Active registers
        return set()

    def _mark(self, roots: Set[int]) -> Set[int]:
        """Mark phase - find all reachable objects"""
        marked = set()
        to_process = list(roots)
        
        while to_process:
            obj_id = to_process.pop()
            if obj_id in marked:
                continue
                
            marked.add(obj_id)
            
            # Add all referenced objects
            for ref_id in self.references.get(obj_id, set()):
                if ref_id not in marked:
                    to_process.append(ref_id)
                    
        return marked

    def _sweep_generation(self, marked: Set[int], generation: Dict[int, AmatakObject]) -> int:
        """Sweep phase - collect unreachable objects"""
        collected = 0
        dead_objects = []
        
        for obj_id in list(generation.keys()):
            if obj_id not in marked:
                # Clean up object
                obj = generation.get(obj_id)
                if obj:
                    obj.__cleanup__()
                    del self.references[obj_id]
                    del self.reverse_refs[obj_id]
                    dead_objects.append(obj_id)
                    collected += 1
        
        # Remove from generation
        for obj_id in dead_objects:
            if obj_id in generation:
                del generation[obj_id]
                
        return collected

    def _promote_generation(self, source: Dict[int, AmatakObject], target: Dict[int, AmatakObject]) -> None:
        """Promote surviving objects to next generation"""
        for obj_id, obj in list(source.items()):
            target[obj_id] = obj
            del source[obj_id]

    def disable(self) -> None:
        """Temporarily disable garbage collection"""
        self.enabled = False

    def enable(self) -> None:
        """Re-enable garbage collection"""
        self.enabled = True
        # Run immediate collection if thresholds are exceeded
        if len(self.gen0) >= self.gen0_threshold:
            self.collect()

    def get_stats(self) -> dict:
        """Get garbage collection statistics"""
        return {
            'gen0_objects': len(self.gen0),
            'gen1_objects': len(self.gen1),
            'gen2_objects': len(self.gen2),
            'total_references': sum(len(refs) for refs in self.references.values()),
            'collections': self.collection_count,
            'enabled': self.enabled
        }

    def set_threshold(self, gen0: int = None, gen1: int = None) -> None:
        """Adjust collection thresholds"""
        if gen0 is not None:
            self.gen0_threshold = max(100, gen0)
        if gen1 is not None:
            self.gen1_threshold = max(10, gen1)

    def full_collect(self) -> None:
        """Perform full garbage collection on all generations"""
        self.collect(0)
        self.collect(1)
        self.collect(2)

    def __del__(self):
        # Clean up all objects on GC destruction
        self.full_collect()