%% compare gradients inside a mask to outside the mask
function [ratio, inside, outside] = gradient_goodness(gradfile, component, mask)
%% comp         -       component to compare
%% comp2compare -       directory of components to compare against
%% mask         -       brainmask
%% plotting     -       logical to set if you want all scatterplots


% use read_avw (fsl?s matlab function) to read in *.nii.gz files
[bgmask, dims,scales,bpp,endian] = read_avw(mask);
bgmask = logical(bgmask);

[compmap] = logical(read_avw(component));
[gradmap] = read_avw(gradfile);

inside = mean2(gradmap(bgmask & compmap));
outside = mean2(gradmap(bgmask & ~compmap));

% Calculate the ratio between the two
ratio = inside / outside;

end