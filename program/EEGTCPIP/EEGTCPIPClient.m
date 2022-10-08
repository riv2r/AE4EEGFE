clc;
clear;
close all;

% remote host IP and Port
ipAddress = 'localhost';
serverPort = 8712;
% number of channel 
nChan = 9;
% sampling rate
sampleRate = 250;
% buffer size in seconds
bufferSize = 4;
% update interval in ms
updateInterval = 0.04;% 40 ms

% calculate update points
if round(sampleRate * updateInterval) > 1
    updatePoints = round(sampleRate * updateInterval);
else
    updatePoints = sampleRate;
end

dataClient = tcpip(ipAddress,serverPort,'NetworkRole','client');

% dataClient properties initialize
dataClient.BytesAvailableFcnCount = 4*nChan*updatePoints;
dataClient.BytesAvailableFcnMode = 'byte';
dataClient.InputBufferSize = dataClient.BytesAvailableFcnCount*10;

dataCell=[];
fopen(dataClient);

i=0;
while ~KbCheck
    rawData = fread(dataClient, dataClient.BytesAvailableFcnCount/4, 'float');
    data = reshape(rawData,[nChan,length(rawData)/nChan]);
    dataCell = [dataCell data];
    dataCellLength = size(dataCell,2);
    if dataCellLength >= bufferSize*sampleRate
        dataCell = dataCell(:,(end-bufferSize*sampleRate+1):end);
    end
    
    for i = 1:nChan
        subplot(nChan,1,i);
        plot(dataCell(i,:)');
    end
    
    % plot(dataCell(9,:)');
    linkdata on;
    pause(updateInterval);
    i=i+1;
end

fclose(dataClient);	