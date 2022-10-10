clc;
clear;
close all;

% host IP and Port
% local host IP 'localhost'
% remote host IP XXX.X.X.X
% local Port 8888
% EEG Device Port 8712
ipAddress = 'localhost';
Port = 8888;
% number of channels
% SSVEP-8 + 1 Trigger
nChan = 9;
% sampling rate
sampleRate = 2400;
% buffer size (in seconds)
bufferSize = 4;
% update interval (in ms)
updateInterval = 0.04;% 40 ms

% calculate update points
if round(sampleRate * updateInterval) > 1
    updatePoints = round(sampleRate * updateInterval);
else
    updatePoints = sampleRate;
end

dataClient = tcpclient(ipAddress,Port);

% dataClient properties initialize
dataClient.InputBufferSize = 4*nChan*updatePoints*10;

rst=[];
% turn on client
fopen(dataClient);

while ~KbCheck
    rawData = fread(dataClient, nChan*updatePoints, 'float');
    data = reshape(rawData,[nChan,updatePoints]);
    rst = [rst data];
    rstLength = size(rst,2);
    if rstLength >= bufferSize*sampleRate
        rst = rst(:,(end-bufferSize*sampleRate+1):end);
    end
    
    for i = 1:nChan
        subplot(nChan,1,i);
        plot(rst(i,:)');
    end
    
    linkdata on;
    pause(0.01);
end

fclose(dataClient);	