#include <Python.h>
#include "amatak.h"
#include "object.h"
#include "pyerrors.h"

/* Module methods */
static PyObject *amatak_run_string(PyObject *self, PyObject *args) {
    const char *code;
    if (!PyArg_ParseTuple(args, "s", &code))
        return NULL;
    
    PyObject *result = Amatak_RunString(code);
    if (!result) {
        return NULL;
    }
    return result;
}

static PyMethodDef AmatakMethods[] = {
    {"run_string", amatak_run_string, METH_VARARGS, "Run Amatak code"},
    {NULL, NULL, 0, NULL}
};
static PyMethodDef AmatakMethods[] = {
    {"exec", amatak_exec, METH_VARARGS, "Execute Amatak code"},
    {"compile", amatak_compile, METH_VARARGS, "Compile Amatak code"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef amatakmodule = {
    PyModuleDef_HEAD_INIT,
    "_amatak",
    NULL,
    -1,
    AmatakMethods
};

PyMODINIT_FUNC PyInit__amatak(void) {
    return PyModule_Create(&amatakmodule);
}

/* Module definition */
static struct PyModuleDef amatakmodule = {
    PyModuleDef_HEAD_INIT,
    "_amatak",
    "Amatak core module",
    -1,
    AmatakMethods
};

/* Module initialization */
PyMODINIT_FUNC PyInit__amatak(void) {
    PyObject *m;
    
    if (PyType_Ready(&AmatakInterpreter_Type) < 0)
        return NULL;
    
    m = PyModule_Create(&amatakmodule);
    if (m == NULL)
        return NULL;
    
    /* Add types */
    Py_INCREF(&AmatakInterpreter_Type);
    PyModule_AddObject(m, "Interpreter", (PyObject *)&AmatakInterpreter_Type);
    
    /* Initialize exceptions */
    AmatakExc_SyntaxError = PyErr_NewException("_amatak.SyntaxError", PyExc_SyntaxError, NULL);
    Py_INCREF(AmatakExc_SyntaxError);
    PyModule_AddObject(m, "SyntaxError", AmatakExc_SyntaxError);
    
    return m;
}




