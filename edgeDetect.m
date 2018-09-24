function [edgeImg] = edgeDetect(img)
edges = edge(rgb2gray(img),'canny');
% imshow(edges)
edgeImg = edges;
end

