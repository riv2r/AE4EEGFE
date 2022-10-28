clc;
clear;
close all;

ipAddress = 'localhost';
Port = 8888;
nChan = 9;
sampleRate = 1000;
updateInterval = 0.04;

% calculate update points
if round(sampleRate * updateInterval) > 1
    updatePoints = round(sampleRate * updateInterval);
else
    updatePoints = sampleRate;
end

dataServer = tcpip(ipAddress,Port,'NetworkRole','server');
dataServer.OutputBufferSize = 4*nChan*updatePoints*10;

x=0;
rst = [];

fopen(dataServer);

tic;
while true
    if length(rst)>=nChan*updatePoints
        rst
        fwrite(dataServer,rst,'float');
        rst = [];
    end
    for i=0:7
        rst=[rst sin(10*2*pi*x+i*pi/2)];
    end
    if toc>=1
        rst = [rst 1];
        tic;
    else
        rst = [rst 0];
    end
    x=x+1;
end

fclose(dataServer);	