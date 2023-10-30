#ifndef SOCKETCOMM_H
#define SOCKETCOMM_H

#include <winsock2.h>
#include <iostream>

class SocketComm{
public:
    SocketComm();
    ~SocketComm();
    SocketComm(const char* ipTmp,int portTmp):ip(ipTmp),port(portTmp){
        init();
    }
    void init();
    bool open();
    void close();
    void finalClose();
    SOCKET getClientHandle(){
        return this->clientHandle;
    }
private:
    SOCKET clientHandle;
    sockaddr_in serverAddr;
    const char* ip="127.0.0.1";
    int port=8712;
};

#endif
