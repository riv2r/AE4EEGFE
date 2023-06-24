#include<iostream>
#include<exception>
#include<pthread.h>
#include"Python.h"

void* SSVEPStimuliPy(void* args)
{
    Py_Initialize();
    if(!Py_IsInitialized())
    {
		std::cout<<".py initialize failed"<<std::endl;
        pthread_exit(NULL);
	}
	
    PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('.')");

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
    Py_Finalize();
    pthread_exit(NULL);
}

int main()
{
    pthread_t thread;
    if(pthread_create(&thread,NULL,SSVEPStimuliPy,NULL)!=0) throw std::exception();
    if(pthread_detach(thread)) throw std::exception();
    pthread_exit(NULL);
    return 0;
}