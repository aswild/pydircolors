#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include <string.h>
#include <unistd.h>

// print a string to stderr, just to test that the extension module loads
// TODO: replace this with a useful function if I ever want to actually use it
static PyObject* compat_print(PyObject *self, PyObject *args)
{
    const char *msg;

    if (!PyArg_ParseTuple(args, "s", &msg))
        return NULL;

    if (fprintf(stderr, "%s\n", msg) < 1)
        return PyErr_SetFromErrno(PyExc_OSError);
    Py_RETURN_NONE;
}

static PyMethodDef compat_methods[] = {
    {"print", compat_print, METH_VARARGS, "Print to stderr"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef compat_module = {
    PyModuleDef_HEAD_INIT,
    "_compat",      // name
    "os.stat() and os.readlink() implementations with dir_fd and follow_symlinks "
    "keyword arguments for python bfore v3.3", // docstring
    -1,             // size of interpreter state, or -1  if it uses global vars
    compat_methods,
};

PyMODINIT_FUNC PyInit__compat(void)
{
    fprintf(stderr, "%s called\n", __func__);
    return PyModule_Create(&compat_module);
}
