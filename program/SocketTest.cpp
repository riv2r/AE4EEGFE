#include <iostream>
#include <winsock2.h>
#include <vector>
#include <windows.h>
#include <ctime>
#include <fstream>
#include "SerialComm/SerialComm.h"

using namespace std;
/*
char port[]="COM5";
// trigger format HEX 0x01 0xE1 0x01 0x00 0xFF
// 0xFF is value determined by user
char mark[]={1,(char)225,1,0,(char)255};

void open(HANDLE& serialHandle)
{
    serialHandle=CreateFile(port,
                            GENERIC_WRITE,
                            0,
                            NULL,
                            OPEN_EXISTING,
                            0,
                            NULL);
    
    if(serialHandle==INVALID_HANDLE_VALUE)
    {
        cout<<"serial create error"<<endl;
        return;
    }
    
    SetupComm(serialHandle,1024,1024);

    COMMTIMEOUTS tout;
    tout.WriteTotalTimeoutMultiplier=500;
    tout.WriteTotalTimeoutConstant=5000;
    SetCommTimeouts(serialHandle,&tout);

    DCB dcb;
    GetCommState(serialHandle,&dcb);
    dcb.BaudRate=115200;
    dcb.ByteSize=8;
    dcb.Parity=NOPARITY;
    dcb.StopBits=ONESTOPBIT;
    SetCommState(serialHandle,&dcb);
    PurgeComm(serialHandle,PURGE_TXCLEAR|PURGE_RXCLEAR);
}

bool write(HANDLE& serialHandle)
{
    DWORD num;
    if(WriteFile(serialHandle,mark,sizeof(mark),&num,0)) return true;
    return false;
}

void close(HANDLE& serialHandle)
{
    CloseHandle(serialHandle);
}
*/

float ByteToFloat(unsigned char* p)
{
    return *((float*)p);
}

int main()
{
    HANDLE serialHandle;

	WORD sockVersion=MAKEWORD(2,2);
	WSADATA data;
	if(WSAStartup(sockVersion,&data)!=0) return 0;
	SOCKET dataCli=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
	if(dataCli==INVALID_SOCKET)
	{
		cout<<"invalid socket"<<endl;
		return 0;
	}
		
	sockaddr_in serAddr;
	serAddr.sin_family=AF_INET;
	serAddr.sin_port=htons(8712);
	serAddr.sin_addr.S_un.S_addr=inet_addr("127.0.0.1");

    vector<vector<float>> res(5000,vector<float>(9,0));

    int row=0,col=0;
    /*
	if(connect(dataCli,(sockaddr *)&serAddr,sizeof(serAddr))==SOCKET_ERROR)
    {
        cout<<"connect error"<<endl;
		closesocket(dataCli);
		return 0;
	}
    */
    SerialComm sh; 
    connect(dataCli,(sockaddr *)&serAddr,sizeof(serAddr));
    if(sh.write()) cout<<"success"<<endl;
    clock_t st=clock();
    while((double)(clock()-st)/CLOCKS_PER_SEC<=4){}
    if(sh.write()) cout<<"success"<<endl;
    
	while(row<5000)
    {
		char recData[4];
		int ret=recv(dataCli,recData,4,0);
        if(ret)
        {
            unsigned char* p=reinterpret_cast<unsigned char*>(recData);
            res[row][col]=ByteToFloat(p);
            ++col;
            if(col==9)
            {
                col=0;
                ++row;
            }
        }
	}
	WSACleanup();
    ofstream fWriter("file.txt");
    for(int i=0;i<5000;++i)
    {
        if(res[i][8]==255) cout<<"OK "<<i<<endl;
        for(int j=0;j<9;++j) fWriter<<res[i][j]<<" ";
        fWriter<<"\n";
    }
    fWriter.flush();
    fWriter.close();

	return 0;
}
