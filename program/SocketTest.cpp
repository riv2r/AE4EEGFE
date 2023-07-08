#include <vector>
#include <ctime>
#include <fstream>

#include "SerialComm/SerialComm.h"
#include "SocketComm/SocketComm.h"

using namespace std;

float ByteToFloat(unsigned char* p)
{
    return *((float*)p);
}

int main()
{
    /*
	WORD sockVersion=MAKEWORD(2,2);
	WSADATA data;
	if(WSAStartup(sockVersion,&data)!=0) return 0;
	SOCKET dataCli=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
	if(dataCli==INVALID_SOCKET)
	{
		cout<<"invalid socket"<<endl;
		return 0;
	}
		
	sockaddr_in serAddr;
	serAddr.sin_family=AF_INET;
	serAddr.sin_port=htons(8712);
	serAddr.sin_addr.S_un.S_addr=inet_addr("127.0.0.1");
    */

    vector<vector<float>> res(5000,vector<float>(9,0));

    int row=0,col=0;
    /*
	if(connect(dataCli,(sockaddr *)&serAddr,sizeof(serAddr))==SOCKET_ERROR)
    {
        cout<<"connect error"<<endl;
		closesocket(dataCli);
		return 0;
	}
    */
    SocketComm ch("127.0.0.1",8712);
    SerialComm sh("COM5");
    //connect(dataCli,(sockaddr *)&serAddr,sizeof(serAddr));

    ch.open();

    if(sh.write()) cout<<"mark"<<endl;

    clock_t st=clock();
    clock_t ed=clock();
    while((double)(ed-st)/CLOCKS_PER_SEC<=4)
    {
        ed=clock();
    }

    if(sh.write()) cout<<"mark"<<endl;
    
	while(row<5000)
    {
		char recData[4];
		int ret=recv(ch.getClientHandle(),recData,4,0);
        if(ret)
        {
            unsigned char* p=reinterpret_cast<unsigned char*>(recData);
            res[row][col]=ByteToFloat(p);
            ++col;
            if(col==9)
            {
                col=0;
                ++row;
            }
        }
	}
	WSACleanup();
    ofstream fWriter("file.txt");
    for(int i=0;i<5000;++i)
    {
        if(res[i][8]==255) cout<<"OK "<<i<<endl;
        for(int j=0;j<9;++j) fWriter<<res[i][j]<<" ";
        fWriter<<"\n";
    }
    fWriter.flush();
    fWriter.close();

	return 0;
}
