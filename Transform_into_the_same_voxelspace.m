function TransformIntoSameVoxelSpace(target_file_name,object_file_name)
%
%   INPUT
%       target_file_name = filename of the image which the object_file_name needs to be
%       transformed into
%       object_file_name = filename of the image that needs to transformed into
%       the space of the target_file_name.
%

%%%%% put_into_same_voxel_space.m
%%%%%
%%%%% In SPM99, put a target image into the same
%%%%% space as an object image.
%%%%% The image-display parts of this program need Matlab 6,
%%%%% because they use the alpha transparency property.
%%%%% 
%%%%% The object image is the one that gets the manipulations done to it:
%%%%% The object image gets resampled so that it lies in the same voxel
%%%%% space as the target image.
%%%%% Written by Rajeev Raizada, May 20, 2003.
%%%%% raj@nmr.mgh.harvard.edu

%target_file_name = spm_get(1,'.img','Select target image');
V_target = spm_vol(target_file_name);
target = spm_read_vols(V_target);

disp(['Size of target image: ' num2str(size(target)) ]);

%object_file_name = spm_get(1,'.img','Select object image');
V_object = spm_vol(object_file_name);
object = spm_read_vols(V_object);

disp(['Size of object image: ' num2str(size(object)) ]);

%%% Find the part of the object image that corresponds to the target image,
%%% (which might involve extending the object image, if the target is bigger)
%%% and interp the object image to have the same resolution as the target

for dim = 1:3,
  
  %%%% In order to interpolate the object image into the target space,
  %%%% we have to figure out which parts of the object image
  %%%% correspond to the target image.
  %%%% If the target image is bigger, then these parts may extend 
  %%%% beyond the current range of the object image.
  %%%% To find these parts, we need to figure out what voxels
  %%%% in the object-image's space would get taken up by the target
  %%%% image, if we put the target into the object's space.
  %%%% First, we find the range in voxels with respect to
  %%%% the origin the the target image spans,
  %%%% then we convert this range into millimeters, so that we can directly
  %%%% compare its range to that of the object image.
  target_vox_size_in_this_dim = V_target.mat(dim,dim);
  
  %%%% Find out which voxel-number is where the origin is
  target_vox_origin = -V_target.mat(dim,4) / target_vox_size_in_this_dim;
  
  %%%% Find out how many voxels the target image has either side of origin
  target_vox_range_wrt_origin = [ 1 size(target,dim) ] - target_vox_origin;
  
  %%%% Turn this voxel-range into millimeters
  target_range_in_mm = ...
        target_vox_range_wrt_origin * target_vox_size_in_this_dim;
 
  %%%% We know the range in mm that the target image spans in this dim,
  %%%% and this will be the same as the range in mm that it spans in 
  %%%% the space of the object image.
  %%%% So, we need to work out the range in object-space voxels that
  %%%% the target image will span when it gets put into object space.
  object_vox_size_in_this_dim = V_object.mat(dim,dim);
  object_vox_origin = -V_object.mat(dim,4) / object_vox_size_in_this_dim;

  target_range_in_object_vox_wrt_origin = ...
      target_range_in_mm / object_vox_size_in_this_dim;

  target_range_in_object_voxspace = target_range_in_object_vox_wrt_origin ...
                                      + object_vox_origin;
  
  %%%% Now we know the range that the object image needs to span
  %%%% in order for it to fit the target space.
  %%%% All we need now, in order to be able to interpolate the object
  %%%% image into the target space, is the ratio of the voxel sizes
  target_object_size_ratio = ...
      target_vox_size_in_this_dim / object_vox_size_in_this_dim;
 
  %%%% For the interp3 command, we'll make three vectors called
  %%%% range_to_send_object_into1,2,3, one for each dimension.
  %%%% These span the range of the target image in the object space,
  %%%% and go up in steps of target_object_size_ratio
  eval(['range_to_send_object_into' num2str(dim) ...
        ' = [ target_range_in_object_voxspace(1): ' ...
        '     target_object_size_ratio : ' ...
        '     target_range_in_object_voxspace(2)];']);
  
end;

%%% Now we can do the interpolation.
%%% Note that interp3 will put NaN in places where the 
%%% interped object extends beyond the range of the original
%%% object image.
%%% Note that interp3 works in x and y coords, not rows and cols,
%%% hence the orders of the first two interp vecs are switched.

disp('Starting 3D interpolation of object image into target space...');

interped_object = ...
    interp3(object,range_to_send_object_into2, ...
                   range_to_send_object_into1', ...
                   range_to_send_object_into3); 


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%
%%% Let's display the interped object overlaid on top of the
%%% target image. This part uses transparancy, so needs Matlab 6

%%% Set how many colour values we want
num_color_vals = 64;

%%% Make the target image go from 0 to num_color_vals
target_0 = target - min(target(:));  %%% Minium value is now zero

target_01 = target_0 / max(target_0(:));  %%% Max value is now 1

target_cvals = num_color_vals * target_01;

%%% Make the interped object go from num_color_vals+1 to 2*num_color_vals 
interped_obj_0 = interped_object - min(interped_object(:));

interped_obj_01 = interped_obj_0 / max(interped_obj_0(:));

interped_obj_cvals = num_color_vals + 1 + num_color_vals * interped_obj_01;

%%% Make a compound colormap
compound_cmap = [ gray(num_color_vals); hot(num_color_vals) ];

%%% Pick some axial slices to show in subplots
num_subplot_rows = 3;
num_subplot_cols = 4;

num_subplots = num_subplot_rows * num_subplot_cols;

slices_to_show = round( linspace( 1, size(target,3), num_subplots ));

figure(1);
clf;

for subplot_idx = 1:num_subplots,
  subplot(num_subplot_rows,num_subplot_cols,subplot_idx),
  
  slice_num = slices_to_show(subplot_idx);
  
  target_slice_cvals = target_cvals(:,:,slice_num);
  %%% Set all the pixels that are 0 or NaN in the target_slice
  %%% to be black. This makes the transparent overlay look nicer.
  target_slice = target(:,:,slice_num);

  zero_entries = find( target_slice==0 );
  nan_entries = find( isnan(target_slice) );
  
  target_slice_cvals( zero_entries ) = 0;
  target_slice_cvals( nan_entries ) = 0;
  
  interped_obj_slice_cvals = interped_obj_cvals(:,:,slice_num);

  h_target = image(target_slice_cvals);
  hold on;
  h_interped_obj = image(interped_obj_slice_cvals);

  colormap( compound_cmap );

  %%% Make the interped object transparent (needs Matlab 6!)
  overlay_opacity = 0.4;    %%% Higher value means more opaque

  %%% Set all the pixels in the overlap to have alpha=overlay_opacity
  opacity_matrix = overlay_opacity * ones(size(interped_obj_slice_cvals));
  
  %%% Set all the pixels that are 0 or NaN in the interped_obj_slice
  %%% to be fully transparent, i.e. with opacity=0
  interped_obj_slice = interped_object(:,:,slice_num);

  zero_entries = find(interped_obj_slice==0);
  nan_entries = find( isnan(interped_obj_slice) );
  
  opacity_matrix( zero_entries ) = 0;
  opacity_matrix( nan_entries ) = 0;
  
  set(h_interped_obj,'alphadata',opacity_matrix);

  axis('image');
  axis('off');
  
end;

%%%%%% Ask whether to write Analyze image of interped object image

write_image_string = 'y';

if write_image_string == 'y',
  
  outfolder = fileparts(target_file_name);
  [~, outfile] = fileparts(object_file_name);
  new_name = fullfile(outfolder, 'gradients', [outfile, '.nii']);
  
  Vnew = V_target;
  Vnew.fname = new_name;
  
  spm_write_vol(Vnew,interped_object);
end;