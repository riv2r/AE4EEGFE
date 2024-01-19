#include <iostream>
#include <vector>
#include <queue>
#include <cmath>
#include <csignal>
#include <cassert>
#include <ctime>

#include "threadpool.h"
#include "SocketComm/TCPClient.h"
#include "SocketComm/TCPServer.h"
#include "NewArch/DataAnalyzer.h"

// namespace
using namespace std;

// macro define
#define PI acos(-1)
#define DASIZE 5

// global variables
const char* serverIP1="127.0.0.1";
int serverPort1=8712;
const char* serverIP2="192.168.185.192";
int serverPort2=8080;
int n=3000;
int chs=8;
vector<vector<float>> globalData(n,vector<float>(chs));
queue<int> globalResult;

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
	
	TCPClient client;
	bool flag1=client.connect2Server(serverIP1,serverPort1);
	TCPServer server;
	bool flag2=server.setupServer(serverIP2,serverPort2);

	DataAnalyzer *DAItems=new DataAnalyzer[DASIZE];
	assert(DAItems);

	threadpool<DataAnalyzer> DAPool;

	int row=0,col=0;
	int idx=0;
	int cnt=0;
	while(flag1 && flag2 && !stop){
		char temp[4];
		bool flagRead=client.receiveData(temp,4);
		if(flagRead){
			globalData[row][col]=*reinterpret_cast<float*>(temp);
			++col;
			if(col==chs){
				col=0;
				++row;
				if(row==n){
					time_t now=time(nullptr);
					cout<<ctime(&now)<<endl;
					DAPool.append(DAItems+idx);
					++cnt;
					++idx;
					if(idx==DASIZE)
						idx=0;
					row=0;
					col=0;
				}
			}
		}
		if(!globalResult.empty()){
			const char* val=to_string(globalResult.front()).c_str();
			server.sendData(val,strlen(val));
			globalResult.pop();
			cout<<cnt<<endl;
		}
	}
	delete[] DAItems;

	Py_END_ALLOW_THREADS

	Py_FinalizeEx();

	return 0;
}
