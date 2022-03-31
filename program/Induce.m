sca;
close all;
clear;

PsychDefaultSetup(2);

screens = Screen('Screens');
screenNumber = max(screens);% 0

white = WhiteIndex(screenNumber);% 1
black = BlackIndex(screenNumber);% 0

[window, rect] = PsychImaging('OpenWindow', screenNumber, black);
% 帧间时间间隔(=1/hertz)
nominalHertz = Screen('NominalFrameRate', window);
ifi = Screen('GetFlipInterval', window);

KbStrokeWait;

sca;