#include "TCPServer.h"

TCPServer::~TCPServer(){
    if(this->clientHandle!=INVALID_SOCKET){
        closesocket(this->clientHandle);
    }
    if(this->serverHandle!=INVALID_SOCKET){
        closesocket(this->serverHandle);
    }
    WSACleanup();
}

bool TCPServer::setupServer(const char* serverIP,int serverPort){
    this->serverHandle=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
    if(this->serverHandle==INVALID_SOCKET){
        cerr<<"Failed to create sokcet"<<endl;
        return false;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family=AF_INET;
    serverAddr.sin_addr.s_addr=inet_addr(serverIP);
    serverAddr.sin_port=htons(serverPort);

    if(bind(this->serverHandle,reinterpret_cast<sockaddr*>(&serverAddr),sizeof(serverAddr))==SOCKET_ERROR){
        cerr<<"Bind failed"<<endl;
        closesocket(this->serverHandle);
        return false;
    }

    if(listen(this->serverHandle,SOMAXCONN)==SOCKET_ERROR){
        cerr<<"Listen failed"<<endl;
        closesocket(this->serverHandle);
        return false;
    }

    cout<<"Waiting for client connection..."<<endl;
    this->clientHandle=accept(this->serverHandle,nullptr,nullptr);
    if(this->clientHandle==INVALID_SOCKET){
        cerr<<"Accept failed"<<endl;
        closesocket(this->serverHandle);
        return false;
    }

    cout<<"Client connected"<<endl;

    return true;
}

bool TCPServer::sendData(const char* data,int dataSize){
    if(this->clientHandle==INVALID_SOCKET){
        cerr<<"Invalid socket"<<endl;
        return false;
    }

    int bytesSent=send(this->clientHandle,data,dataSize,0);
    if(bytesSent==SOCKET_ERROR){
        cerr<<"Error sending data"<<endl;
        return false;
    }

    return true;
}