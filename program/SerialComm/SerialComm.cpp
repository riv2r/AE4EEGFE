#include "SerialComm.h"

SerialComm::SerialComm(){
    init();
}

SerialComm::~SerialComm(){
    close();
}

void SerialComm::init(){
    SetupComm(this->serialHandle,1024,1024);
    
    COMMTIMEOUTS tout;
    tout.WriteTotalTimeoutMultiplier=500;
    tout.WriteTotalTimeoutConstant=5000;
    SetCommTimeouts(this->serialHandle,&tout);

    DCB dcb;
    GetCommState(this->serialHandle,&dcb);
    dcb.BaudRate=115200;
    dcb.ByteSize=8;
    dcb.Parity=NOPARITY;
    dcb.StopBits=ONESTOPBIT;
    SetCommState(this->serialHandle,&dcb);
    PurgeComm(this->serialHandle,PURGE_TXCLEAR|PURGE_RXCLEAR);
}

void SerialComm::open(){
    this->serialHandle=CreateFileA(this->port,
                                   GENERIC_WRITE,
                                   0,
                                   NULL,
                                   OPEN_EXISTING,
                                   0,
                                   NULL);
    if(this->serialHandle==INVALID_HANDLE_VALUE){
        std::cout<<"serial open error"<<std::endl;
        return;
    }
}

bool SerialComm::write(){
    DWORD num;
    if(WriteFile(this->serialHandle,mark,sizeof(mark),&num,0))
        return true;
    return false;
}

void SerialComm::close(){
    CloseHandle(this->serialHandle);
}
