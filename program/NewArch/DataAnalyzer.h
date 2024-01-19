#ifndef DATA_ANALYZER_H
#define DATA_ANALYZER_H

#include <iostream>
#include <vector>
#include <queue>

#include "../PythonThreadLocker.h"

using namespace std;

class DataAnalyzer{
public:
    DataAnalyzer():DA_result(-1){};
    ~DataAnalyzer(){};
public:
    void process();
private:
    void recognize();
private:
    int DA_result;
};

#endif