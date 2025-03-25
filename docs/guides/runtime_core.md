Key Features:
Type Hierarchy:

Base AmatakType class for all types

Built-in types: Integer, Float, String, Boolean

Complex types: Array, Object, Function

Special types: Dynamic, Nullable

Validation & Coercion:

Each type implements validate() and coerce()

Type constraints (min/max values, patterns, etc.)

Safe conversion between types

Composite Types:

Arrays with typed elements

Objects with typed fields

Functions with parameter and return types

Dynamic Typing Support:

DynamicType for untyped values

type_of() function for runtime type detection

Gradual typing support

Error Handling:

Detailed type errors

Constraint violation messages

Safe coercion attempts

Usage Examples:


```
# Create custom types
PersonType = ObjectType({
    "name": StringType(max_length=100),
    "age": IntegerType(min_val=0, max_val=150),
    "email": StringType(pattern=r"^[^@]+@[^@]+\.[^@]+$")
})

# Validate values
person = {"name": "Alice", "age": 30, "email": "alice@example.com"}
if PersonType.validate(person):
    print("Valid person")

# Coerce values
try:
    safe_age = IntegerType(min_val=18).coerce("25")
except AmatakTypeError as e:
    print(f"Error: {e}")

# Runtime type checking
value = [1, 2, 3]
print(f"Type of value: {type_of(value)}")  # Array[Integer]

# Nullable types
nullable_int = NullableType(INTEGER)
print(nullable_int.validate(None))  # True
print(nullable_int.validate(42))    # True

```