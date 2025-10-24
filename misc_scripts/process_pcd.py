import open3d as o3d
import numpy as np
import argparse



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

def filter_hsv(hsv_colors):
    return



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input_file', type=str)
    parser.add_argument('--output_file', type=str)
    parser.add_argument('--filter_colors', action='store_true')
    parser.add_argument('--h', type=int, nargs=2, default=[100,140])
    parser.add_argument('--s', type=float, nargs=2, default=[.05,.95])
    parser.add_argument('--v', type=float, nargs=2, default=[.05,.95])
    parser.add_argument('--crop_bbox', action='store_true')
    parser.add_argument('--bbox_bounds', type=float, nargs=6, default=[.2, .8, 0, .75, .2, .8])
    parser.add_argument('--remove_stat_outliers', action='store_true')
    parser.add_argument('--neighborhood', type=int, default=20)
    parser.add_argument('--std_ratio', type=float, default=2.0)
    parser.add_argument('--remove_radius_outliers', action='store_true')
    parser.add_argument('--min_neighbors', type=int, default=16)
    parser.add_argument('--radius', type=float, default=0.05)

    args = parser.parse_args()


    pcd = o3d.io.read_point_cloud(args.input_file)
    points = np.array(pcd.points)
    colors = np.array(pcd.colors)
    cur_pcd = pcd

    print(len(cur_pcd.points))
    if args.filter_colors:
        hsv_min = [args.h[0], args.s[0], args.v[0]]
        hsv_max = [args.h[1], args.s[1], args.v[1]]

        for ch in range(3):
            cur_colors = np.array(cur_pcd.colors)
            hsv_colors = rgb2hsv(cur_colors.reshape((cur_colors.shape[0], -1, 3)))
            hsv_colors = hsv_colors[:,0,:]
            print(hsv_colors[:,ch].min(), hsv_colors[:,ch].max())
            new_pcd = cur_pcd.select_by_index(np.where(np.logical_and(hsv_colors[:,ch]<=hsv_max[ch], hsv_colors[:,ch]>=hsv_min[ch]))[0])
            cur_pcd = new_pcd
            print(len(cur_pcd.points))

    
    if args.crop_bbox:
        np_points = np.array(cur_pcd.points)
        min_bound_x = np.quantile(np_points[:,0], args.bbox_bounds[0], axis=0)
        max_bound_x = np.quantile(np_points[:,0], args.bbox_bounds[1], axis=0)
        min_bound_y = np.quantile(np_points[:,1], args.bbox_bounds[2], axis=0)
        max_bound_y = np.quantile(np_points[:,1], args.bbox_bounds[3], axis=0)
        min_bound_z = np.quantile(np_points[:,2], args.bbox_bounds[4], axis=0)
        max_bound_z = np.quantile(np_points[:,2], args.bbox_bounds[5], axis=0)
        print(min_bound_x, min_bound_y, min_bound_z, max_bound_x, max_bound_y, max_bound_z)
        min_bound = np.array([min_bound_x, min_bound_y, min_bound_z])
        max_bound = np.array([max_bound_x, max_bound_y, max_bound_z])

        bbox = o3d.geometry.AxisAlignedBoundingBox(min_bound=min_bound, max_bound=max_bound)
        cur_pcd = cur_pcd.crop(bbox)
        print(len(cur_pcd.points))

    if args.remove_stat_outliers:
        cld, idx = cur_pcd.remove_statistical_outlier(nb_neighbors=args.neighborhood,
                                                    std_ratio=args.std_ratio)
        new_pcd = cur_pcd.select_by_index(idx)
        cur_pcd = new_pcd
        print(len(cur_pcd.points))

    if args.remove_radius_outliers:
        cld, idx = cur_pcd.remove_radius_outlier(nb_points=args.min_neighbors, radius=args.radius)
        new_pcd = cur_pcd.select_by_index(idx)
        cur_pcd = new_pcd
        print(len(cur_pcd.points))


    o3d.io.write_point_cloud(args.output_file, cur_pcd)
    o3d.visualization.draw_geometries([cur_pcd])

''''
hsv = rgb2hsv(colors.reshape((colors.shape[0], -1, 3)))
hsv = hsv[:,0,:]


print(np.where(hsv[:,0] > 21)[0].shape)

#new_pcd = pcd.select_by_index(np.where(hsv[:,0]>221)[0]) # purple
new_pcd = pcd.select_by_index(np.where(np.logical_or(hsv[:,0]<20, hsv[:,0]>320))[0]) # red
#o3d.io.write_point_cloud(f'colmap_exports/0421/0421_recons/{data}/phone_24mm/colmap_00-1/dense/fused_filtered.ply', new_pcd)
o3d.io.write_point_cloud(f'{pcd_name}_filtered.ply', new_pcd)
o3d.visualization.draw_geometries([new_pcd])
'''

'''

'''

#o3d.visualization.draw_geometries([crop_pcd])

#filter_pcd = crop_pcd.remove_radius_outlier(nb_points=64, radius=0.05)
#o3d.visualization.draw_geometries([filter_pcd])
