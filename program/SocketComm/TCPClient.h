#ifndef TCPCLIENT_H
#define TCPCLIENT_H

#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>

#pragma comment(lib,"Ws2_32.lib")

using namespace std;

class TCPClient{
public:
    TCPClient():clientHandle(INVALID_SOCKET){
        WSADATA wsaData;
        if(WSAStartup(MAKEWORD(2,2),&wsaData)!=0){
            cerr<<"Failed to initialize Winsock"<<endl;
        }
    }
    ~TCPClient();
    bool connect2Server(const char* serverIP,int serverPort);
    bool receiveData(char* buffer,int bufferSize);
private:
    SOCKET clientHandle;
};

#endif
