#ifndef TCPSERVER_H
#define TCPSERVER_H

#include <iostream>
#include <winsock2.h>

#pragma comment(lib,"Ws2_32.lib")

using namespace std;

class TCPServer{
public:
    TCPServer():serverHandle(INVALID_SOCKET),clientHandle(INVALID_SOCKET){
        WSADATA wsaData;
        if(WSAStartup(MAKEWORD(2,2),&wsaData)!=0){
            cerr<<"Failed to initialize Winsock"<<endl;
        }
    }
    ~TCPServer();
    bool setupServer(const char* serverIP,int serverPort);
    bool sendData(const char* data,int dataSize);
private:
    SOCKET serverHandle;
    SOCKET clientHandle;
};

#endif
