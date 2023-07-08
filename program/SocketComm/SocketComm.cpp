#include "SocketComm.h"

SocketComm::SocketComm()
{
    init();
}

SocketComm::~SocketComm()
{
    finalClose();
}

void SocketComm::init()
{
    WORD socketVersion=MAKEWORD(2,2);
    WSADATA data;
    if(WSAStartup(socketVersion,&data)!=0)
    {
        std::cout<<"WSA init error"<<std::endl;
        return;
    }

    this->clientHandle=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);

    if(this->clientHandle==INVALID_SOCKET)
    {
        std::cout<<"socket invalid"<<std::endl;
        return;
    }

    serverAddr.sin_family=AF_INET;
    serverAddr.sin_addr.S_un.S_addr=inet_addr(this->ip);
    serverAddr.sin_port=htons(this->port);
}

bool SocketComm::open()
{
    if(connect(this->clientHandle,(sockaddr*)&(this->serverAddr),sizeof(this->serverAddr))==SOCKET_ERROR)
    {
        std::cout<<"connect error"<<std::endl;
        close();
        return false;
    }
    return true;
}

void SocketComm::close()
{
    closesocket(this->clientHandle);
}

void SocketComm::finalClose()
{
    closesocket(this->clientHandle);
    WSACleanup();
}