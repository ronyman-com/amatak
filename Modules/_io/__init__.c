#include <Python.h>
#include "amatak.h"

static PyMethodDef IoMethods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef iomodule = {
    PyModuleDef_HEAD_INIT,
    "_io",
    "Low-level IO module",
    -1,
    IoMethods
};

PyMODINIT_FUNC PyInit__io(void) {
    PyObject *m = PyModule_Create(&iomodule);
    if (m == NULL)
        return NULL;
    
    // Initialize IO types here
    return m;
}