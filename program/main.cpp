#include <iostream>
#include <vector>
#include <cmath>
#include <csignal>
#include <cassert>

#include "threadpool.h"
//#include <winsock2.h> before #include <windows.h>
#include "SocketComm/TCPClient.h"
#include "SocketComm/TCPServer.h"
#include "eeg_conn/eeg_conn.h"

// namespace
using namespace std;

// macro define
#define PI acos(-1)

// global variables
const char* serverIP1="127.0.0.1";
int serverPort1=8712;
const char* serverIP2="192.168.185.192";
int serverPort2=8080;
int n=4000;
int chs=8;
vector<vector<float>> glbdata(n,vector<float>(chs));

static bool stop=false;
static void handle_term(int sig){
	stop=true;
}

int main(){
	Py_Initialize();
	//python 3.9 and later does nothing
	//PyEval_InitThreads();

	Py_BEGIN_ALLOW_THREADS
	signal(SIGINT,handle_term);

	eeg_conn *items=new eeg_conn[128];
	assert(items);

	threadpool<eeg_conn> pool;
	
	TCPClient client;
	bool flag1=client.connect2Server(serverIP1,serverPort1);
	TCPServer server;
	bool flag2=server.setupServer(serverIP2,serverPort2);
	int row=0,col=0;
	int idx=0;
	while(flag1 && flag2 && !stop){
		char recData[4];
		bool flag_r=client.receiveData(recData,4);
		if(flag_r){
			glbdata[row][col]=*reinterpret_cast<float*>(recData);
			++col;
			if(col==chs){
				col=0;
				++row;
				if(row==n){
					items[idx].init(n,chs);
					pool.append(items+idx);
					++idx;
					row=0;
					col=0;
				}
			}
		}
		if(!eeg_conn::results.empty()){
			const char* result=to_string(eeg_conn::results.front()).c_str();
			server.sendData(result,strlen(result));
			eeg_conn::results.pop();
		}
	}
	delete[] items;

	Py_END_ALLOW_THREADS

	Py_FinalizeEx();

	return 0;
}
