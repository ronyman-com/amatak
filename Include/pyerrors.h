#ifndef AMATAK_PYERRORS_H
#define AMATAK_PYERRORS_H

#include <Python.h>

/* Standard exception types */
PyAPI_DATA(PyObject*) AmatakExc_BaseException;
PyAPI_DATA(PyObject*) AmatakExc_SyntaxError;
PyAPI_DATA(PyObject*) AmatakExc_RuntimeError;
PyAPI_DATA(PyObject*) AmatakExc_TypeError;
PyAPI_DATA(PyObject*) AmatakExc_ValueError;
PyAPI_DATA(PyObject*) AmatakExc_ImportError;

/* Error macros */
#define AmatakErr_SetString(exc, msg) PyErr_SetString((exc), (msg))
#define AmatakErr_Occurred() PyErr_Occurred()
#define AmatakErr_Clear() PyErr_Clear()

/* Exception initialization */
PyAPI_FUNC(int) AmatakErrors_Init(void);

/* Syntax error helper */
PyAPI_FUNC(void) AmatakErr_SyntaxLocation(const char *filename, int lineno, int colno);

/* Warning support */
PyAPI_FUNC(int) AmatakErr_WarnEx(PyObject *category, const char *message, int stack_level);

#endif /* AMATAK_PYERRORS_H */