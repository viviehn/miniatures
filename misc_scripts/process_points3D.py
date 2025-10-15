import numpy as np

original_file = 'cylinders_canon_50mm_points'

with open(f'colmap_exports/{original_file}.txt') as f:
    lines = f.readlines()

points = np.array([
    [float(l.split(' ')[1]), float(l.split(' ')[2]), float(l.split(' ')[3])] for l in lines[3:]
   ])

rgb = np.array([
    [float(l.split(' ')[4]), float(l.split(' ')[5]), float(l.split(' ')[6])] for l in lines[3:]
   ])

x_scale = points[:,0].max() - points[:,0].min()
y_scale = points[:,1].max() - points[:,1].min()
z_scale = points[:,2].max() - points[:,2].min()
print(x_scale, y_scale, z_scale)

scale = np.max([x_scale, y_scale, z_scale])
print(scale)

points_scaled = points/scale
points = points_scaled

points_center = np.mean(points, axis=0)
print(points_center)
points = points - points_center
print(points.min(), points.max())

with open(f'colmap_exports/{original_file}_meshlab.txt', 'w+') as f:
    for p, c in zip(points, rgb):
        f.write(f'{p[0]} {p[1]} {p[2]} {c[0]} {c[1]} {c[2]}\n')


