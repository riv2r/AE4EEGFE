#ifndef THREADPOOL_H
#define THREADPOOL_H

#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <stdexcept>
#include <memory>


template <typename T>
class threadpool{
public:
    threadpool(int thread_number=8,int max_requests=10000);
    ~threadpool();
    bool append(T* request);
private:
    static void *worker(void *arg);
    void run();
private:
    int b_thread_number;
    int b_max_requests;
    std::vector<std::thread> b_threads;
    std::queue<T*> b_workqueue;
    std::mutex b_queuelocker;
    std::condition_variable b_queuestate;
    bool b_stop;
};

template <typename T>
threadpool<T>::threadpool(int thread_number,int max_requests):b_thread_number(thread_number),b_max_requests(max_requests),b_stop(false){
    if(b_thread_number<=0 || b_max_requests<=0)
        throw std::exception();

    for(int i=0;i<b_thread_number;++i){
        b_threads.emplace_back(worker,this);
    }
}

template <typename T>
threadpool<T>::~threadpool(){
    std::unique_lock<std::mutex> lock(b_queuelocker);
    b_stop=true;

    b_queuestate.notify_all();
    for(auto& t:b_threads){
        t.join();
    }
}

template <typename T>
bool threadpool<T>::append(T* request){
    b_queuelocker.lock();
    if(b_workqueue.size()>b_max_requests){
        b_queuelocker.unlock();
        return false;
    }
    b_workqueue.push(request);
    b_queuelocker.unlock();
    b_queuestate.notify_one();
    return true;
}

template <typename T>
void *threadpool<T>::worker(void *arg){
    threadpool *pool=(threadpool*) arg;
    pool->run();
    return pool;
}

template <typename T>
void threadpool<T>::run(){
    while(!b_stop){
        std::unique_lock<std::mutex> lock(this->b_queuelocker);
        this->b_queuestate.wait(lock,[this]{return !this->b_workqueue.empty();});
        if(this->b_workqueue.empty())
            continue;
        else{
            T* request=b_workqueue.front();
            b_workqueue.pop();
            if(request)
                request->process();
        }
    }   
}

#endif