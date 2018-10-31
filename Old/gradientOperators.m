% gradientOperators 
%
% Parameters: 
%   * opName: A string indicating which gradient operator to use. 
%       * The valid values are: 
%           * 'roberts'
%           * 'prewitt'
%           * 'sobel'
%           * 'sobel5x5'
%           * 'scharr'
%       * Throws error is any other string is passed 
%       * Note: operator name is case insensitive 
%
% Return values: 
%   * delta1: The horizontal gradient operator matrix 
%   * delta2: The vertical gradient operator matrix 
%
function [delta1, delta2] = gradientOperators(opName) 
    if strcmpi(opName, 'roberts')
        delta1 = [1  0; 
                  0 -1];

        delta2 = [ 0 1; 
                  -1 0]; 

    elseif strcmpi(opName, 'prewitt') 
        delta1 = [1 0 -1; 
                  1 0 -1; 
                  1 0 -1];

        delta2 = [ 1  1  1; 
                   0  0  0; 
                  -1 -1 -1]; 

    elseif strcmpi(opName, 'sobel') 
        delta1 = [1 0 -1; 
                  2 0 -2; 
                  1 0 -1];

        delta2 = [ 1  2  1; 
                   0  0  0;
                  -1 -2 -1]; 

    elseif strcmpi(opName, 'scharr') 
        delta1 = [ 3 0 -3; 
                  10 0 -10; 
                  3  0 -3];

        delta2 = [ 3  10  3; 
                   0   0  0; 
                  -3 -10 -3]; 

    elseif strcmpi(opName, 'sobel5x5') 
        delta1 = [1 2 0 -2 -1; 
                  2 3 0 -3 -2; 
                  3 5 0 -5 -3; 
                  2 3 0 -3 -2; 
                  1 2 0 -2 -1];

        delta2 = [ 1  2  3  2  1; 
                   2  3  5  3  2; 
                   0  0  0  0  0; 
                  -2 -3 -5 -3 -2; 
                  -1 -2 -3 -2 -1]; 

    else 
        error('Gradient operator is unknown'); 
    end
end 
