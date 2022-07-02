%% Initiate Psychtoolbox
% when open MATLAB R2022a firstly
% execute the following code: InitPsychtoolbox
InitPsychtoolbox;

%% Start
sca;
clc;
clear;
close all;
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
six_six=        [0 0 0 0 1 1 1 1 1];

% initiate freq table
freq{1} = six_six;
freq{2} = seven_five;
freq{3} = eight_fiveseven;
freq{4} = ten;
freq{5} = twelve;
lenFreq=[length(freq{1}),length(freq{2}),length(freq{3}),length(freq{4}),length(freq{5})];

%% Generate display matrixes for movies
% Find LCM(least common multiple ) of freq matrix to create equal matrixes for all freqs
lcmFreq=1;
for i=1:length(lenFreq)
    lcmFreq=lcm(lcmFreq,lenFreq(i));
end
% Generate full movie matrix of frequency
for i=1:5
    freqCombine(i,:) = repmat(freq{i},1,lcmFreq/length(freq{i})); 
end
% revert value
freqCombine=1-freqCombine;
try
    screens=Screen('Screens');
    screenNumber = max(screens);
    % test size 1 [640 300 1280 780] 640x480
    % test size 2 [0 0 1920 1080] 1920x1080
    [win,winRect]=Screen('OpenWindow',screenNumber,[],[0 0 1920 1080]);
    [width,height]=Screen('WindowSize',win);
    % initiate target size 
    targetWidth=100;
    targetHeight=100;
    % draw texture to screen
    screenMatrix=GetImage(width, height, targetWidth, targetHeight);
    for i=1:32
        texture(i)=Screen('MakeTexture',win,uint8(screenMatrix{i})*255);
    end
    % Define refresh rate.
    ifi=Screen('GetFlipInterval',win);
    topPriorityLevel = MaxPriority(win);
    indexflip=1;

    %% Start looping movie
    Priority(topPriorityLevel);
    while ~KbCheck
        % Drawing
        % Compute texture value based on display value from freq long matrixes
        textureValue=freqCombine(:,indexflip).*[1;2;4;8;16];
        textureValue=textureValue(5)+textureValue(4)+textureValue(3)+textureValue(2)+textureValue(1)+1;
        % Draw it on the back buffer
        Screen('DrawTexture',win,texture(textureValue));
        % Display current index
        % Screen('DrawText',win,num2str(indexflip),0,0,255);
        % Tell PTB no more drawing commands will be issued until the next flip
        Screen('DrawingFinished',win);
        % Fliping
        % Screen('Flip',win,vb1+halfifi);
        % Flip ASAP
        Screen('Flip',win);
        indexflip=indexflip+1;

        % Reset index at the end of freq matrix
        if indexflip>lcmFreq
            indexflip=1;
            % disp('over');
        end
    end
    Priority(0); 
    frame_duration=Screen('GetFlipInterval',win);
    Screen('CloseAll');
    Screen('Close');
catch
    Screen('CloseAll');
    Screen('Close');
    psychrethrow(psychlasterror);
end