#include <iostream>
#include <cmath>
#include <vector>
#include <thread>
#include <csignal>
#include <cassert>

// #include <winsock2.h> before #include <windows.h>
#include "SocketComm/SocketComm.h"
#include "SerialComm/SerialComm.h"
#include "threadpool.h"
#include "eeg_conn/eeg_conn.h"

using namespace std;

#define PI acos(-1)

const char* ip="127.0.0.1";
int port=8712;

int n=1000;
int chs=8;
vector<vector<double>> glbdata(n,vector<double>(chs));

static bool stop=false;
static void handle_term(int sig){
	stop=true;
}

double Byte2Double(unsigned char* p){
    return *((double*)p);
}

void IntentRecPy(vector<vector<double>>& nums);

int main(){
	Py_Initialize();
	//python 3.9 and later does nothing
	//PyEval_InitThreads();

	Py_BEGIN_ALLOW_THREADS
	signal(SIGINT,handle_term);

	eeg_conn *items=new eeg_conn[128];
	assert(items);

	threadpool<eeg_conn> pool;
	
	SocketComm ch(ip,port);
	bool chValid=ch.open();
	int row=0,col=0;
	int idx=0;
	while(chValid){
		char recData[4];
		int ret=recv(ch.getClientHandle(),recData,4,0);
		if(ret){
			unsigned char* p=reinterpret_cast<unsigned char*>(recData);
			glbdata[row][col]=Byte2Double(p);
			++col;
			if(col==chs){
				col=0;
				++row;
				if(row==n){
					items[idx].init(ch.getClientHandle(),n,chs);
					pool.append(items+idx);
					++idx;
					row=0;
					col=0;
				}
			}
		}
	}
	delete[] items;

	Py_END_ALLOW_THREADS

	Py_FinalizeEx();

	return 0;
}

/*
void IntentRecPy(){
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
	
	vector<vector<double>> nums(glbData);

	PyObject *PyList=PyList_New(0);
    PyObject *ArgList=PyTuple_New(1);
    for(int i=0;i<nums.size();i++){
		PyObject *PyListTemp=PyList_New((Py_ssize_t)nums[i].size());
		for(int j=0;j<nums[i].size();j++){
			PyList_SetItem(PyListTemp,j,PyFloat_FromDouble(nums[i][j]));
		}
		PyList_Append(PyList,PyListTemp);
	}
	PyTuple_SetItem(ArgList,0,PyList);

	PyObject* pRet=PyObject_CallObject(pFunc,ArgList);

	int result;
	PyArg_Parse(pRet,"i",&result);
	cout<<"result:"<<result<<endl;

	Py_DECREF(pRet);
	Py_DECREF(pFunc);
	Py_DECREF(pModule);

    Py_Finalize();

	return;
}
*/