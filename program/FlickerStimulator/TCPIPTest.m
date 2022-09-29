clc;
clf;
close all;
clear all;

tcpip_client = tcpip('127.0.0.1',8712,'NetworkRole','client');
tcpip_client.Timeout=1;
tcpip_client.InputBuffersize=36;
tcpip_client.TransferDelay='off';
tcpip_client.BytesAvailableFcnMode="byte";
packetSize=36;
tcpip_client.BytesAvailableFcnCount=packetSize;

dataCell=[];

fopen(tcpip_client);


i=0;
while 1
    i=i+1;
    dataTemp=[];
    dataReceive=fread(tcpip_client,36)
    for j=1:4:36
        temp=typecast(fliplr(uint8(dataReceive(j:j+3)')),'single')
        dataTemp=[dataTemp temp];
    end
    dataCell=[dataCell;dataTemp];
    if(i>4000)
        break;
    end
end

fclose(tcpip_client);	