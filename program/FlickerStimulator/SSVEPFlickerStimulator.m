%% Initiate Psychtoolbox
% when open MATLAB R2022a firstly
% execute the following code: InitPsychtoolbox
% InitPsychtoolbox;

%% Start
sca;
clc;
clear;
close all;

%% Initiate serial
%{
delete(instrfindall);
s=serial('COM8','BaudRate',115200);
fopen(s);
%}

%% Initiate TCP/IP
%{
% host IP and Port
ipAddress = 'localhost';
Port = 8888;
% number of channels: SSVEP-8 + 1 Trigger
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
%}

%% Initiate frequency
% Frames Period Freq. Simulated signal. 0 light. 1 dark
% [#]   [ms]    [Hz]    [-]
% 3.0   50.00   20.00   [0 1 1]
% 4.0   66.67   15.00   [0 0 1 1]
% 5.0   83.33   12.00   [0 0 1 1 1]
% 6.0   100.00  10.00   [0 0 0 1 1 1]
% 7.0   116.67  8.57    [0 0 0 1 1 1 1]
% 8.0   133.33  7.50    [0 0 0 0 1 1 1 1]
% 9.0   150.00  6.66    [0 0 0 0 1 1 1 1 1]

PsychDefaultSetup(2);
Screen('Preference', 'SkipSyncTests', 1);

% According to the paper 1 is black, 0 is white
twelve=         [0 0 1 1 1];
ten=            [0 0 0 1 1 1];
eight_fiveseven=[0 0 0 1 1 1 1];
seven_five=     [0 0 0 0 1 1 1 1];
% six_six=        [0 0 0 0 1 1 1 1 1];

% initiate freq table
% freq{1} = six_six;
freq{1} = seven_five;
freq{2} = eight_fiveseven;
freq{3} = ten;
freq{4} = twelve;
lenFreq=[length(freq{1}),length(freq{2}),length(freq{3}),length(freq{4})];

%% Generate display matrixes for movies
% Find LCM(least common multiple ) of freq matrix to create equal matrixes for all freqs
lcmFreq=1;
for i=1:length(lenFreq)
    lcmFreq=lcm(lcmFreq,lenFreq(i));
end
% Generate full movie matrix of frequency
for i=1:4
    freqCombine(i,:) = repmat(freq{i},1,lcmFreq/length(freq{i})); 
end
% revert value
freqCombine=1-freqCombine;

try
    screens=Screen('Screens');
    screenNumber = max(screens);
    % test size 1 [640 300 1280 780] 640x480
    % test size 2 [0 0 1920 1080] 1920x1080
    [win,winRect]=Screen('OpenWindow',screenNumber,[255 255 255],[0 0 640 480]);
    [width,height]=Screen('WindowSize',win);
    % initiate target size 
    targetWidth=100;
    targetHeight=100;
    % draw texture to screen
    screenMatrix=GetParadigm(width, height, targetWidth, targetHeight);
    for i=1:16
        texture(i)=Screen('MakeTexture',win,uint8(screenMatrix{i})*255);
    end
    textureWhite=Screen('MakeTexture',win,uint8(ones(size(screenMatrix{1})))*255);
    textureBlack=Screen('MakeTexture',win,uint8(zeros(size(screenMatrix{1})))*255);
    % Define refresh rate.
    ifi=Screen('GetFlipInterval',win);
    topPriorityLevel = MaxPriority(win);
    indexflip=1;

    %% Start looping movie
    Priority(topPriorityLevel);
    vb1=Screen('Flip',win);
    waitframes = 1;

    % while ~KbCheck % && etime(t2,t1)<125
        
        rst=[];
        % turn on client
        fopen(dataClient);
        %}
        % Before collect 1s
        % black
        %{
        Screen('DrawTexture',win,textureBlack);
        Screen('DrawingFinished',win);
        %}
        Screen('TextSize',win,50);
        Screen('TextFont',win,'Times');
        DrawFormattedText(win,'Ready to take control','center','center',[0 0 0]);
        vb1=Screen('Flip',win,vb1+(waitframes-0.5)*ifi);
        WaitSecs(1);

        %{
        % send trigger: 0x01 0xE1 0x01 0x00 0x01 '0x01' is trigger value determined by user
        fwrite(s,[1 225 1 0 255]);
        %}
        
        tic;
        while toc<=4
            % Drawing
            % Compute texture value based on display value from freq long matrixes
            textureValue=freqCombine(:,indexflip).*[1;2;4;8];
            textureValue=textureValue(4)+textureValue(3)+textureValue(2)+textureValue(1)+1;
            % Draw it on the back buffer
            Screen('DrawTexture',win,texture(textureValue));
            % Display current index
            % Screen('DrawText',win,num2str(indexflip),0,0,255);
            % Tell PTB no more drawing commands will be issued until the next flip
            Screen('DrawingFinished',win);
            % Fliping
            % Screen('Flip',win,vb1+halfifi);
            % Flip ASAP
            vb1=Screen('Flip',win,vb1+(waitframes-0.5)*ifi);
            indexflip=indexflip+1;
    
            % Reset index at the end of freq matrix
            if indexflip>lcmFreq
                indexflip=1;
                % disp('over');
            end
        end
        while true
            rawData = fread(dataClient, nChan*updatePoints, 'float');
            data = reshape(rawData,[nChan,updatePoints]);
            rst = [rst data];
            rstLength = size(rst,2);
            if rstLength >= bufferSize*sampleRate
                break
                % rst = rst(:,(end-bufferSize*sampleRate+1):end);
            end
        end
        %{
        % send trigger: 0x01 0xE1 0x01 0x00 0x01 '0x01' is trigger value determined by user
        fwrite(s,[1 225 1 0 1]);
        %}
        
        % After collect 1s
        % black
        %{
        Screen('DrawTexture',win,textureBlack);
        Screen('DrawingFinished',win);
        %}
        Screen('TextSize',win,50);
        Screen('TextFont',win,'Times');
        DrawFormattedText(win,'End','center','center',[0 0 0]);
        vb1=Screen('Flip',win,vb1+(waitframes-0.5)*ifi);
        WaitSecs(1);
        fclose(dataClient);

    % end
    % fclose(s);
    Priority(0); 
    frame_duration=Screen('GetFlipInterval',win);
    Screen('CloseAll');
    Screen('Close');
catch
    Screen('CloseAll');
    Screen('Close');
    psychrethrow(psychlasterror);
end