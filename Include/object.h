#ifndef AMATAK_OBJECT_H
#define AMATAK_OBJECT_H

#include <Python.h>

/* Base object type */
typedef struct _amatak_object {
    PyObject_HEAD
    PyObject *dict;
    PyObject *type;
} AmatakObject;

/* Type flags */
#define AMATAK_TYPE_FLAGS_VALID_VERSION_TAG (1UL << 0)

/* Object API */
PyAPI_FUNC(AmatakObject*) AmatakObject_New(PyTypeObject *);
PyAPI_FUNC(int) AmatakObject_Check(PyObject *);

/* Number protocol */
typedef struct {
    PyNumberMethods as_number;
} AmatakNumberMethods;

/* Sequence protocol */
typedef struct {
    PySequenceMethods as_sequence;
} AmatakSequenceMethods;

/* Mapping protocol */
typedef struct {
    PyMappingMethods as_mapping;
} AmatakMappingMethods;

/* Type object */
typedef struct {
    PyTypeObject type;
    AmatakNumberMethods *tp_as_number;
    AmatakSequenceMethods *tp_as_sequence;
    AmatakMappingMethods *tp_as_mapping;
} AmatakTypeObject;

/* Core type definitions */
PyAPI_DATA(PyTypeObject) AmatakObject_Type;
PyAPI_DATA(PyTypeObject) AmatakType_Type;

#endif /* AMATAK_OBJECT_H */