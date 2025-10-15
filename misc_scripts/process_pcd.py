import open3d as o3d
import numpy as np

#data = 'pyramidcube2'
pcd_name = 'macro_nerf'

#pcd = o3d.io.read_point_cloud(f'colmap_exports/0421/{data}_fused.ply')
#pcd = o3d.io.read_point_cloud(f'colmap_exports/0421/0421_recons/{data}/phone_24mm/colmap_00-1/dense/fused.ply')
pcd = o3d.io.read_point_cloud(f'{pcd_name}.ply')
points = np.array(pcd.points)
colors = np.array(pcd.colors)


def rgb2hsv(rgb):
    """ convert RGB to HSV color space

    :param rgb: np.ndarray
    :return: np.ndarray
    """

    rgb = rgb.astype('float')
    maxv = np.amax(rgb, axis=2)
    maxc = np.argmax(rgb, axis=2)
    minv = np.amin(rgb, axis=2)
    minc = np.argmin(rgb, axis=2)

    hsv = np.zeros(rgb.shape, dtype='float')
    hsv[maxc == minc, 0] = np.zeros(hsv[maxc == minc, 0].shape)
    hsv[maxc == 0, 0] = (((rgb[..., 1] - rgb[..., 2]) * 60.0 / (maxv - minv + np.spacing(1))) % 360.0)[maxc == 0]
    hsv[maxc == 1, 0] = (((rgb[..., 2] - rgb[..., 0]) * 60.0 / (maxv - minv + np.spacing(1))) + 120.0)[maxc == 1]
    hsv[maxc == 2, 0] = (((rgb[..., 0] - rgb[..., 1]) * 60.0 / (maxv - minv + np.spacing(1))) + 240.0)[maxc == 2]
    hsv[maxv == 0, 1] = np.zeros(hsv[maxv == 0, 1].shape)
    hsv[maxv != 0, 1] = (1 - minv / (maxv + np.spacing(1)))[maxv != 0]
    hsv[..., 2] = maxv

    return hsv

hsv = rgb2hsv(colors.reshape((colors.shape[0], -1, 3)))
hsv = hsv[:,0,:]


print(np.where(hsv[:,0] > 21)[0].shape)

#new_pcd = pcd.select_by_index(np.where(hsv[:,0]>221)[0]) # purple
new_pcd = pcd.select_by_index(np.where(np.logical_or(hsv[:,0]<20, hsv[:,0]>320))[0]) # red
#o3d.io.write_point_cloud(f'colmap_exports/0421/0421_recons/{data}/phone_24mm/colmap_00-1/dense/fused_filtered.ply', new_pcd)
o3d.io.write_point_cloud(f'{pcd_name}_filtered.ply', new_pcd)
o3d.visualization.draw_geometries([new_pcd])

'''

min_bound = np.quantile(np_points, .01, axis=0)
max_bound = np.quantile(np_points, .99, axis=0)

bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=min_bound, max_bound=max_bound)
crop_pcd = pcd.crop(bbox)

o3d.io.write_point_cloud('colmap_exports/alpha_50mm_dense_crop.ply', crop_pcd)
print(pcd.get_min_bound(), pcd.get_max_bound())
print(crop_pcd.get_min_bound(), crop_pcd.get_max_bound())

print(crop_pcd.colors)
'''

#o3d.visualization.draw_geometries([crop_pcd])

#filter_pcd = crop_pcd.remove_radius_outlier(nb_points=64, radius=0.05)
#o3d.visualization.draw_geometries([filter_pcd])
