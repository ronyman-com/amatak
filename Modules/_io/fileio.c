#include "amatak.h"

typedef struct {
    PyObject_HEAD
    FILE *fp;
    int fd;
    char *name;
} fileio;

static PyObject *fileio_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    fileio *self = (fileio *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->fp = NULL;
        self->fd = -1;
        self->name = NULL;
    }
    return (PyObject *)self;
}

static int fileio_init(fileio *self, PyObject *args, PyObject *kwds) {
    const char *name;
    const char *mode = "r";
    
    if (!PyArg_ParseTuple(args, "s|s", &name, &mode))
        return -1;
    
    self->fp = fopen(name, mode);
    if (self->fp == NULL) {
        PyErr_SetFromErrno(PyExc_IOError);
        return -1;
    }
    
    self->name = strdup(name);
    self->fd = fileno(self->fp);
    
    return 0;
}

// ... (other fileio methods)

static PyTypeObject FileIO_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_io.FileIO",                   /* tp_name */
    sizeof(fileio),                 /* tp_basicsize */
    0,                              /* tp_itemsize */
    0,                              /* tp_dealloc */
    0,                              /* tp_print */
    0,                              /* tp_getattr */
    0,                              /* tp_setattr */
    0,                              /* tp_reserved */
    0,                              /* tp_repr */
    0,                              /* tp_as_number */
    0,                              /* tp_as_sequence */
    0,                              /* tp_as_mapping */
    0,                              /* tp_hash */
    0,                              /* tp_call */
    0,                              /* tp_str */
    0,                              /* tp_getattro */
    0,                              /* tp_setattro */
    0,                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,             /* tp_flags */
    "FileIO objects",               /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                              /* tp_iternext */
    0,                              /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)fileio_init,          /* tp_init */
    0,                              /* tp_alloc */
    fileio_new,                     /* tp_new */
};