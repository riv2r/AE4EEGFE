#include <iostream>
#include <vector>
#include <cmath>
#include <csignal>
#include <cassert>

#include "threadpool.h"
//#include <winsock2.h> before #include <windows.h>
#include "SocketComm/SocketComm.h"
#include "SerialComm/SerialComm.h"
#include "eeg_conn/eeg_conn.h"

using namespace std;

#define PI acos(-1)

const char* ip="127.0.0.1";
int port=8712;

int n=1000;
int chs=8;
vector<vector<float>> glbdata(n,vector<float>(chs));

static bool stop=false;
static void handle_term(int sig){
	stop=true;
}

float Byte2Float(unsigned char* p){
    float ans=0;
	unsigned long long temp=0;
	temp=(*p<<0)+(*(p+1)<<8)+(*(p+2)<<16)+(*(p+3)<<24);
	ans=*(float*)&temp;
	return ans;
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
	
	SocketComm ch(ip,port);
	bool chValid=ch.open();
	int row=0,col=0;
	int idx=0;
	while(chValid && !stop){
		char recData[4];
		int ret=recv(ch.getClientHandle(),recData,4,0);
		if(ret){
			unsigned char* p=reinterpret_cast<unsigned char*>(recData);
			glbdata[row][col]=Byte2Float(p);
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
	}
	delete[] items;

	Py_END_ALLOW_THREADS

	Py_FinalizeEx();

	return 0;
}
