#include<iostream>
#include<exception>
#include<pthread.h>
#include"Python.h"

void* ssvepStimuliPy(void* args)
{
    Py_Initialize();
	PyGILState_STATE ret=PyGILState_Ensure();

    if(!Py_IsInitialized())
    {
		std::cout<<".py initialize failed"<<std::endl;
        pthread_exit(NULL);
	}
	
    PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('/home/user/Desktop/ControlByBCI/program')");

	PyObject* pModule=PyImport_ImportModule("SSVEPStimuli");

	if(pModule==NULL)
    {
		std::cout<<"module not found"<<std::endl;
		pthread_exit(NULL);
	}

	PyObject* pFunc=PyObject_GetAttrString(pModule,"startup");

	if(!pFunc || !PyCallable_Check(pFunc))
    {
		std::cout<<"startup() not found"<<std::endl;
		pthread_exit(NULL);
	}

	PyObject_CallObject(pFunc,NULL);

	PyGILState_Release(ret);
    Py_Finalize();

    pthread_exit(NULL);
}

void* livePy(void* args)
{
    Py_Initialize();
	PyGILState_STATE ret=PyGILState_Ensure();

    if(!Py_IsInitialized())
    {
		std::cout<<".py initialize failed"<<std::endl;
        pthread_exit(NULL);
	}
	
    PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('/home/user/Desktop/ControlByBCI/program')");

	PyObject* pModule=PyImport_ImportModule("Live");

	if(pModule==NULL)
    {
		std::cout<<"module not found"<<std::endl;
		pthread_exit(NULL);
	}

	PyObject* pFunc=PyObject_GetAttrString(pModule,"startup");

	if(!pFunc || !PyCallable_Check(pFunc))
    {
		std::cout<<"startup() not found"<<std::endl;
		pthread_exit(NULL);
	}

	PyObject_CallObject(pFunc,NULL);

	PyGILState_Release(ret);
    Py_Finalize();

    pthread_exit(NULL);
}


int main()
{
	Py_Initialize();
	PyEval_InitThreads();

	Py_BEGIN_ALLOW_THREADS

    pthread_t thread1;
	pthread_t thread2;

    if(pthread_create(&thread1,NULL,ssvepStimuliPy,NULL)!=0) throw std::exception();
    if(pthread_detach(thread1)) throw std::exception();

	sleep(2);

    if(pthread_create(&thread2,NULL,livePy,NULL)!=0) throw std::exception();
    if(pthread_detach(thread2)) throw std::exception();

	pthread_exit(NULL);

	Py_END_ALLOW_THREADS
}