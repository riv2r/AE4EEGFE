#include "DataAnalyzer.h"

extern vector<vector<float>> globalData;
extern queue<int> globalResult;

void DataAnalyzer::recognize(){
	PythonThreadLocker locker;
	
    Py_Initialize();

    if(!Py_IsInitialized()){
		std::cout<<".py initialize failed"<<std::endl;
		return;
	}
	
    PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('C:/Users/user/Desktop/ControlByBCI/program')");

	PyObject* pModule=PyImport_ImportModule("IntentRec");

	if(pModule==NULL){
		std::cout<<"module not found"<<std::endl;
		return;
	}

	PyObject* pFunc=PyObject_GetAttrString(pModule,"methodCCA");

	if(!pFunc || !PyCallable_Check(pFunc)){
		std::cout<<"methodCCA() not found"<<std::endl;
		return;
	}

	PyObject *PyList=PyList_New(0);
    PyObject *ArgList=PyTuple_New(1);
    for(int i=0;i<globalData.size();i++){
		PyObject *PyListTemp=PyList_New((Py_ssize_t)globalData[i].size());
		for(int j=0;j<globalData[i].size();j++){
			PyList_SetItem(PyListTemp,j,PyFloat_FromDouble((double)globalData[i][j]));
		}
		PyList_Append(PyList,PyListTemp);
	}
	PyTuple_SetItem(ArgList,0,PyList);

	PyObject* pRet=PyObject_CallObject(pFunc,ArgList);

	PyArg_Parse(pRet,"i",&this->DA_result);
	globalResult.emplace(this->DA_result);

	Py_DECREF(pRet);
	Py_DECREF(pFunc);
	Py_DECREF(pModule);

    //Py_Finalize();

	return;
}

void DataAnalyzer::process(){
	recognize();
}