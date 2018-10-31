function newImage = imageThreshold(image, threshold) 
    % Make the image grayscale if color image
    % Image is color if size of third dimension is greater than 1 
    if size(image, 3) > 1           
        image = rgb2gray(image);
    end 

    i_max = size(image, 1);
    j_max = size(image, 2); 

    newImage = uint8(zeros(i_max, j_max)); 

    for i = 1:i_max
        for j = 1:j_max
            if image(i, j) > threshold
               newImage(i, j) = image(i, j);
            else
               newImage(i, j) = 0;  
        end
    end

end
