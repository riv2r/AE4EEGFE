#include "TCPClient.h"

TCPClient::~TCPClient(){
    if(this->clientHandle!=INVALID_SOCKET){
        closesocket(clientHandle);
    }
    WSACleanup();
}

bool TCPClient::connect2Server(const char* serverIP,int serverPort){
    this->clientHandle=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
    if(this->clientHandle==INVALID_SOCKET){
        cerr<<"Failed to create socket"<<endl;
        return false;
    }

    sockaddr_in serverAddr;
    serverAddr.sin_family=AF_INET;
    serverAddr.sin_port=htons(serverPort);
    inet_pton(AF_INET,serverIP,&(serverAddr.sin_addr));

    if(connect(this->clientHandle,reinterpret_cast<sockaddr*>(&serverAddr),sizeof(serverAddr))==SOCKET_ERROR){
        cerr<<"Failed to connect to server"<<endl;
        closesocket(this->clientHandle);
        this->clientHandle=INVALID_SOCKET;
        return false;
    }
    return true;
}

bool TCPClient::receiveData(char* buffer,int bufferSize){
    if(this->clientHandle==INVALID_SOCKET){
        cerr<<"Invalid socket"<<endl;
        return false;
    }

    int bytesReceived=recv(this->clientHandle,buffer,bufferSize,0);
    if(bytesReceived==SOCKET_ERROR){
        cerr<<"Error receiving data"<<endl;
        return false;
    }

    if(bytesReceived==0){
        cout<<"Connection closed by the server"<<endl;
        return false;
    }

    return true;
}