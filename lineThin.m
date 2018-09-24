function [thinnedImg] = lineThin(image)

thinnedImg = bwmorph(image,'thin');
end

