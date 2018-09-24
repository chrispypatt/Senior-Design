% thinEdges
% 
% Parameters: 
% 
% Return Values:
% 
%
function thinImage = thinEdges(mag, dir) 
    height = size(mag, 1);
    width = size(mag, 2); 
    thinImage = zeros(height, width); 

    for i = 1:height
        for j = 1:width
            % If pixel is non zero, check if greater than neighbors along
            % gradient direction. If so keep, otherwise set to zero. 
            if (mag(i,j) > 0)  
                % Find coordinates of neighbors along direction
                n1i = i + round(sind(dir(i,j))); 
                n1j = j - round(cosd(dir(i,j)));
                n2i = i + round(sind(dir(i,j) + 180)); 
                n2j = j - round(cosd(dir(i,j) + 180));

                % Assume pixel is maximum
                gtn1 = true;
                gtn2 = true; 
               
                % Check if n1 within bounds and mag less than n1  
                if n1i > 0 & n1i <= height & n1j > 0 & n1j < width
                    gtn1 = mag(i,j) >= mag(n1i, n1j);
                end  
                
                % Check if n2 within bounds and mag less than n2  
                if n2i > 0 & n2i <= height & n2j > 0 & n2j < width 
                    gtn1 = mag(i,j) >= mag(n2i, n2j);
                end 
                
                if gtn1 & gtn2 
                    thinImage(i,j) = mag(i,j);
                else 
                    thinImage(i,j) = 0; 
                end
            end
        end
    end
end
