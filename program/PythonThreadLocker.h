#include <Python.h>

class PythonThreadLocker{
private:
    PyGILState_STATE state;
public:
    PythonThreadLocker():state(PyGILState_Ensure()){}
    ~PythonThreadLocker(){
        PyGILState_Release(state);
    }
};