#include<iostream>
#include<exception>
#include<thread>
#include<Python.h>
#include<windows.h>

void ssvepStimuliPy()
{
	PyGILState_STATE ret=PyGILState_Ensure();
	
    Py_Initialize();

    if(!Py_IsInitialized())
    {
		std::cout<<".py initialize failed"<<std::endl;
		return;
	}
	
    PyRun_SimpleString("import sys");
	//PyRun_SimpleString("sys.path.append('/home/user/Desktop/ControlByBCI/program')");
	PyRun_SimpleString("sys.path.append('C:/Users/user/Desktop/毕业设计/program/ControlByBCI/program')");

	PyObject* pModule=PyImport_ImportModule("SSVEPStimuli");

	if(pModule==NULL)
    {
		std::cout<<"module not found"<<std::endl;
		return;
	}

	PyObject* pFunc=PyObject_GetAttrString(pModule,"startup");

	if(!pFunc || !PyCallable_Check(pFunc))
    {
		std::cout<<"startup() not found"<<std::endl;
		return;
	}

	PyObject* pRet=PyObject_CallObject(pFunc,NULL);
	Py_DECREF(pRet);
	Py_DECREF(pFunc);
	Py_DECREF(pModule);

    Py_Finalize();
	PyGILState_Release(ret);

	return;
}

void livePy()
{
	PyGILState_STATE ret=PyGILState_Ensure();
	
    Py_Initialize();

    if(!Py_IsInitialized())
    {
		std::cout<<".py initialize failed"<<std::endl;
		return;
	}
	
    PyRun_SimpleString("import sys");
	//PyRun_SimpleString("sys.path.append('/home/user/Desktop/ControlByBCI/program')");
	PyRun_SimpleString("sys.path.append('C:/Users/user/Desktop/毕业设计/program/ControlByBCI/program')");

	PyObject* pModule=PyImport_ImportModule("Live");

	if(pModule==NULL)
    {
		std::cout<<"module not found"<<std::endl;
		return;
	}

	PyObject* pFunc=PyObject_GetAttrString(pModule,"startup");

	if(!pFunc || !PyCallable_Check(pFunc))
    {
		std::cout<<"startup() not found"<<std::endl;
		return;
	}

	PyObject* pRet=PyObject_CallObject(pFunc,NULL);
	Py_DECREF(pRet);
	Py_DECREF(pFunc);
	Py_DECREF(pModule);

    Py_Finalize();
	PyGILState_Release(ret);

	return;
}


int main()
{
	Py_Initialize();
	//python 3.9 and later does nothing
	//PyEval_InitThreads();

	Py_BEGIN_ALLOW_THREADS

    	std::thread th1(ssvepStimuliPy);
		//sleep(3);
		std::thread th2(livePy);
		th1.detach();
		th2.detach();
		while(true)
		{
			//sleep(1);
			Sleep(1000);
		}
	
	Py_END_ALLOW_THREADS

	Py_FinalizeEx();

	return 0;
}