% Parameters: 
%   * image: the image to determine the gradient magnitude and direction
%     matrices of, stored as a 2 or 3 dimensional matrix 
%   * gradientOpName: A string indicating which gradient operator to use. 
%       * The valid values are: 
%           * 'roberts'
%           * 'prewitt'
%           * 'sobel'
%           * 'sobel5x5'
%           * 'scharr'
% Return Values: 
%   * Magnitude: The gradient magnitude matrix 
%       * Type: uint8
%   * Direction: The gradient direction matirix 
%       * Type: double
%
% Note: For an image of size m1 x n1 and a gradient operator of size m2 x n2,
%       the resulting magnitude and direction matrices will be of size 
%       m1 + (m2 - 1) x n1 + (n2 - 1)
%
% Note: Magnitude matrix will be returned as having elements of type double.
%       Matlab expects image matrices in double format to be in the range of 
%       0 to 1, and so functions like imshow(Magnitude) will display the
%       magnitude incorrectly. To display it correctly, the matrix should be 
%       converted to uint8 type using the function uint8(Magnitude). This 
%       function leaves the magnitude in double format for further 
%       processing.  
% 
function [Magnitude, Direction] = imageGradient(image, gradientOpName)
    % Make the image grayscale if color image
    % Image is color if size of third dimension is greater than 1 
    if size(image, 3) > 1           
        image = rgb2gray(image);
    end 
    

    
    % Get the gradient operator matrices  
    [delta1, delta2] = gradientOperators(gradientOpName); 

    % Pad the image 
    padSize = size(delta1, 1) - 1;
    rows = size(image, 1);
    cols = size(image, 2); 
    for i = 1:padSize
        if mod(i,2) == 1
            image = [image, image(:,size(image,2))]; 
            image = [image; image(size(image, 1),:)]; 
        else
            image = [image(:,1), image];
            image = [image(1,:); image];
    end

    Gx = conv2(image, delta1, 'valid');
    Gy = conv2(image, delta2, 'valid'); 

    % Need to normalize magnitude for specific operator used
    %   I think its mag * 1 / (2 * (size(delta1, 1) - 1))
    %   So 2x2 => 1/2, 3x3 => 1/6, 5x5 => 1/8
    % Not right
    Magnitude = sqrt(Gx.^2 + Gy.^2); 
    Direction = atan2d(-Gy, Gx);  
end

    
