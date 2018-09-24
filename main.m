clear;close all;

vidObj = VideoReader('assets/videos/typing.mp4');
frames = vidObj.NumberOfFrames;
vidObj = VideoReader('assets/videos/typing.mp4');
vidHeight = vidObj.Height;
vidWidth = vidObj.Width;
s = struct('cdata',zeros(vidHeight,vidWidth,3,'uint8'),'colormap',[]);

v = VideoWriter('assets/videos/typingEdges.mp4', 'MPEG-4');
open(v);
k = 1;
try
    f = waitbar(0,'Reading in video. Please wait...');
    while hasFrame(vidObj)
        waitbar(k/(2*frames),f,'Reading in video. Please wait...');
        s(k).cdata = readFrame(vidObj);
        k = k+1;
    end


    for i = 1:(k-1)
        waitbar((i+frames)/(2*frames),f,'Processing video. Please wait...');
        edges = edgeDetect(s(i).cdata);
        thinned = lineThin(edges);
%         Segout = img;
% Segout(edges) = 255;

        writeVideo(v,double(thinned));
    end

    close(v);
    close(f);
catch exception
    close(v);
    close(f);
end