from amatak.runtime.memory import MemoryAllocator
from amatak.runtime.memory.gc import GarbageCollector
from amatak.runtime.types.core import AmatakObject

# Create allocator and GC
allocator = MemoryAllocator()
gc = GarbageCollector(allocator)

# Sample object class
class MyObject(AmatakObject):
    def __init__(self, value):
        self.value = value
        self.ref = None
    
    def __cleanup__(self):
        print(f"Cleaning up {self.value}")

# Create and register objects
obj1 = MyObject(1)
obj2 = MyObject(2)
obj3 = MyObject(3)

gc.register_object(obj1)
gc.register_object(obj2)
gc.register_object(obj3)

# Create references
gc.add_reference(obj1, obj2)
gc.add_reference(obj2, obj3)

# Run collection
print("Before GC:", gc.get_stats())
gc.collect()
print("After GC:", gc.get_stats())

# Remove reference and collect again
gc.remove_reference(obj1, obj2)
gc.full_collect()
print("After full collection:", gc.get_stats())