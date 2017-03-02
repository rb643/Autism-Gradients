%% compare one t-maps against a list of t-maps
function [compcor compp] = betweenComponentCorrelations(comp1, comp2comparedir, mask, plotting)
%% comp         -       component to compare
%% comp2compare -       directory of components to compare against
%% mask         -       brainmask
%% plotting     -       logical to set if you want all scatterplots


% use read_avw (fsl?s matlab function) to read in *.nii.gz files
[bgmask, dims,scales,bpp,endian] = read_avw(mask);
bgmask = logical(bgmask);

[ICmain, dimsmain,scalesmain,bppmain,endianmain] = read_avw(comp1);

% get the list of component to compare against
c = dir(fullfile(comp2comparedir,'*.nii'));
disp(c)
subsize = ceil(sqrt(length(c)));
figure;
for icom = 1:length(c)
    [comp, dims,scales,bpp,endian] = read_avw(fullfile(comp2comparedir,c(icom).name));
    [r, p] = corr(ICmain(bgmask),comp(bgmask));
    compcor(icom) = r;
    compp = p
    
    if plotting == 1
        subplot(subsize,subsize,icom);
        scatter(ICmain(bgmask),comp(bgmask));lsline;
        title(['Correlation between ' comp1 ' and ' c(icom).name ' R = ' num2str(r,3) ',' 'P = ' num2str(p,3)]);
    end
    
end
compcor;
compp;

end