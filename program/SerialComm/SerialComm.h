#ifndef SERIALCOMM_H
#define SERIALCOMM_H

#include <windows.h>
#include <iostream>

class SerialComm
{
public:
    SerialComm();
    ~SerialComm();
    void open();
    void init();
    bool write();
    void close();
private:
    HANDLE serialHandle;
    const char* port="COM5";
    char mark[5]={1,(char)225,1,0,(char)255};
};

#endif