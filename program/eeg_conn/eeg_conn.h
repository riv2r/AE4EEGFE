#ifndef EEG_CONN_H
#define EEG_CONN_H

#include <iostream>
#include <vector>
#include <winsock2.h>

#include "../PythonThreadLocker.h"

using namespace std;

class eeg_conn{
public:
    eeg_conn(){};
    ~eeg_conn(){};
public:
    void init(SOCKET,int,int);
    void process();
    bool read();
    void recognize();
    bool write();
    int getrst(){
        return this->result;
    }
public:
    static vector<int> results;
private:
    SOCKET sockfd;
    int n;
    int chs;
    int result=-1;
    vector<vector<double>> data;
};

#endif