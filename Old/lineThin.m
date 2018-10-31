function [thinnedImg] = lineThin(image)

thinnedImg = bwmorph(image,'thin');
thinnedImg = bwareaopen(thinnedImg,500);
end

