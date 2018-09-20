function [edgeImg] = edgeDetect(img)
edges = edge(rgb2gray(img),'canny');
% imshow(edges)
Segout = img;
Segout(edges) = 255;
edgeImg = Segout;
end

