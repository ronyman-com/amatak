#ifndef AMATAK_H
#define AMATAK_H

#include <Python.h>
#include "object.h"
#include "pyerrors.h"

/* API version */
#define AMATAK_API_VERSION 101

/* Core objects */
typedef struct {
    PyObject_HEAD
    void *interpreter_state;
} AmatakInterpreter;

/* Initialization and finalization */
PyAPI_FUNC(int) Amatak_Initialize(void);
PyAPI_FUNC(void) Amatak_Finalize(void);

/* Code execution */
PyAPI_FUNC(PyObject*) Amatak_CompileString(const char *code);
PyAPI_FUNC(PyObject*) Amatak_RunString(const char *code);

/* Module support */
PyAPI_FUNC(PyObject*) Amatak_ImportModule(const char *name);
PyAPI_FUNC(int) Amatak_AddToPath(const char *path);

/* Error handling */
PyAPI_FUNC(void) Amatak_Err_SetString(PyObject *exception, const char *msg);

/* Type definitions */
PyAPI_DATA(PyTypeObject) AmatakInterpreter_Type;

#ifdef __cplusplus
}
#endif

#endif /* AMATAK_H */


/* Core API functions */
PyObject* amatak_exec(PyObject* self, PyObject* args);
PyObject* amatak_compile(PyObject* self, PyObject* args);

/* Module definition */
extern PyMethodDef AmatakMethods[];

#endif