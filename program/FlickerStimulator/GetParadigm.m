function [Paradigm]=GetParadigm(winWidth,winHeight,targetWidth,targetHeight)
    
    %% Generate Matrix for 5 Targets (Top, Right, Down, Left, Stop)
    for i=1:6
        targetMatrix{i}=zeros(winHeight,winWidth,'uint8');
    end
    % conver maxtrix from zero to target
    %   00100 Top
    %   10101 Left/Stop/Right
    %   00100 Down
    for i=1:winHeight % first row to last
        for j=1:winWidth % first column to last
            % Target1:Top
            if j>winWidth/2-targetWidth/2 && j<=winWidth/2+targetWidth/2 && i<=targetHeight
                targetMatrix{1}(i,j)=1; % match target coordinate
                % disp('got it');
            % Target2:Left
            elseif i>winHeight/2-targetHeight/2 && i<=winHeight/2+targetHeight/2 && j<=targetWidth
                targetMatrix{2}(i,j)=1;
                % disp('got it');
            % Target3:Stop
            elseif j>winWidth/2-targetWidth/2 && j<=winWidth/2+targetWidth/2 && i>winHeight/2-targetHeight/2 && i<=winHeight/2+targetHeight/2
                targetMatrix{3}(i,j)=1;
                % disp('got it');
            % Target4:Right
            elseif i>winHeight/2-targetHeight/2 && i<=winHeight/2+targetHeight/2 && j>winWidth-targetWidth
                targetMatrix{4}(i,j)=1;
                % disp('got it');
            % Target5:Down
            elseif j>winWidth/2-targetWidth/2 && j<=winWidth/2+targetWidth/2 && i>winHeight-targetHeight
                targetMatrix{5}(i,j)=1;
                % disp('got it');
            end
        end
    end
    %% Draw Image to Screen: Draw 32 states
    for targetState1=1:2
        for targetState2=1:2
            for targetState3=1:2
                for targetState4=1:2
                    for targetState5=1:2
                        textureNumber=(targetState5-1)*16+(targetState4-1)*8+(targetState3-1)*4+(targetState2-1)*2+(targetState1-1)*1+1;
                        screenMatrix{textureNumber}=targetMatrix{6} |...
                                                    targetMatrix{1}*uint8(targetState1-1) |...
                                                    targetMatrix{2}*uint8(targetState2-1) |...
                                                    targetMatrix{3}*uint8(targetState3-1) |...
                                                    targetMatrix{4}*uint8(targetState4-1) |...
                                                    targetMatrix{5}*uint8(targetState5-1);
                    end
                end
            end
        end
    end
    Paradigm=screenMatrix;
end