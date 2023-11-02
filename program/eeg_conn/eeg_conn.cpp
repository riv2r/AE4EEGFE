#include "eeg_conn.h"

extern vector<vector<float>> glbdata;

vector<int> eeg_conn::results=vector<int>();

void eeg_conn::init(int n,int chs){
    e_n=n;
    e_chs=chs;
}

bool eeg_conn::read(){
	data=glbdata;
	if(data.size()==e_n && data[0].size()==e_chs)
		return true;
	return false;
}

void eeg_conn::recognize(){
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
    for(int i=0;i<data.size();i++){
		PyObject *PyListTemp=PyList_New((Py_ssize_t)data[i].size());
		for(int j=0;j<data[i].size();j++){
			PyList_SetItem(PyListTemp,j,PyFloat_FromDouble((double)data[i][j]));
		}
		PyList_Append(PyList,PyListTemp);
	}
	PyTuple_SetItem(ArgList,0,PyList);

	PyObject* pRet=PyObject_CallObject(pFunc,ArgList);

	PyArg_Parse(pRet,"i",&result);
	cout<<result<<endl;

	Py_DECREF(pRet);
	Py_DECREF(pFunc);
	Py_DECREF(pModule);

    //Py_Finalize();

	return;
}

bool eeg_conn::write(){
    results.emplace_back(this->result);
    return true;
}

void eeg_conn::process(){
	bool rflag=read();
	if(rflag){
		recognize();
	}
	else{
		cout<<"read fault"<<endl;
	}
    if(result!=-1){
        write();
    }
}