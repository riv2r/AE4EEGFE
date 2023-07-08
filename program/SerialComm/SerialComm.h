#ifndef SERIALCOMM_H
#define SERIALCOMM_H

#include <windows.h>
#include <iostream>

class SerialComm
{
public:
    SerialComm();
    ~SerialComm();
    SerialComm(const char* p):port(p)
    {
        open();
        init();
    }
    void open();
    void init();
    bool write();
    void close();
private:
    HANDLE serialHandle;
    const char* port="COM5";
    // trigger format HEX 0x01 0xE1 0x01 0x00 0xFF
    // 0xFF is value determined by user
    char mark[5]={1,(char)225,1,0,(char)255};
};

#endif