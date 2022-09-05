# import numpy as np
# import matplotlib.pyplot as plt
#
#
# class DraggableRectangle:
#     def __init__(self, rect):
#         self.rect = rect
#         self.press = None
#
#     def connect(self):
#         """Connect to all the events we need."""
#         self.cidpress = self.rect.figure.canvas.mpl_connect(
#             'button_press_event', self.on_press)
#         self.cidrelease = self.rect.figure.canvas.mpl_connect(
#             'button_release_event', self.on_release)
#         self.cidmotion = self.rect.figure.canvas.mpl_connect(
#             'motion_notify_event', self.on_motion)
#
#     def on_press(self, event):
#         """Check whether mouse is over us; if so, store some data."""
#         if event.inaxes != self.rect.axes:
#             return
#         contains, attrd = self.rect.contains(event)
#         if not contains:
#             return
#         print('event contains', self.rect.xy)
#         self.press = self.rect.xy, (event.xdata, event.ydata)
#
#     def on_motion(self, event):
#         """Move the rectangle if the mouse is over us."""
#         if self.press is None or event.inaxes != self.rect.axes:
#             return
#         (x0, y0), (xpress, ypress) = self.press
#         dx = event.xdata - xpress
#         dy = event.ydata - ypress
#         # print(f'x0={x0}, xpress={xpress}, event.xdata={event.xdata}, '
#         #       f'dx={dx}, x0+dx={x0+dx}')
#         self.rect.set_x(x0+dx)
#         self.rect.set_y(y0+dy)
#
#         self.rect.figure.canvas.draw()
#
#     def on_release(self, event):
#         """Clear button press information."""
#         self.press = None
#         self.rect.figure.canvas.draw()
#
#     def disconnect(self):
#         """Disconnect all callbacks."""
#         self.rect.figure.canvas.mpl_disconnect(self.cidpress)
#         self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
#         self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
#
# fig, ax = plt.subplots()
# rects = ax.bar(range(10), 20*np.random.rand(10))
# drs = []
# for rect in rects:
#     dr = DraggableRectangle(rect)
#     dr.connect()
#     drs.append(dr)
#
# plt.show()


# """
# Illustrate the figure and axes enter and leave events by changing the
# frame colors on enter and leave
# """
# import matplotlib.pyplot as plt
#
# def enter_axes(event):
#     print('enter_axes', event.inaxes)
#     event.inaxes.patch.set_facecolor('yellow')
#     event.canvas.draw()
#
# def leave_axes(event):
#     print('leave_axes', event.inaxes)
#     event.inaxes.patch.set_facecolor('white')
#     event.canvas.draw()
#
# def enter_figure(event):
#     print('enter_figure', event.canvas.figure)
#     event.canvas.figure.patch.set_facecolor('red')
#     event.canvas.draw()
#
# def leave_figure(event):
#     print('leave_figure', event.canvas.figure)
#     event.canvas.figure.patch.set_facecolor('grey')
#     event.canvas.draw()
#
# fig1, axs = plt.subplots(2)
# fig1.suptitle('mouse hover over figure or axes to trigger events')
#
# fig1.canvas.mpl_connect('figure_enter_event', enter_figure)
# fig1.canvas.mpl_connect('figure_leave_event', leave_figure)
# fig1.canvas.mpl_connect('axes_enter_event', enter_axes)
# fig1.canvas.mpl_connect('axes_leave_event', leave_axes)
#
# fig2, axs = plt.subplots(2)
# fig2.suptitle('mouse hover over figure or axes to trigger events')
#
# fig2.canvas.mpl_connect('figure_enter_event', enter_figure)
# fig2.canvas.mpl_connect('figure_leave_event', leave_figure)
# fig2.canvas.mpl_connect('axes_enter_event', enter_axes)
# fig2.canvas.mpl_connect('axes_leave_event', leave_axes)
#
# plt.show()

# """
# Compute the mean and stddev of 100 data sets and plot mean vs. stddev.
# When you click on one of the (mean, stddev) points, plot the raw dataset
# that generated that point.
# """
#
# import numpy as np
# import matplotlib.pyplot as plt
#
# X = np.random.rand(100, 1000)
# xs = np.mean(X, axis=1)
# ys = np.std(X, axis=1)
#
# fig, ax = plt.subplots()
# ax.set_title('click on point to plot time series')
# line, = ax.plot(xs, ys, 'o', picker=True, pickradius=5)  # 5 points tolerance
#
#
# def onpick(event):
#     if event.artist != line:
#         return
#     n = len(event.ind)
#     if not n:
#         return
#     fig, axs = plt.subplots(n, squeeze=False)
#     for dataind, ax in zip(event.ind, axs.flat):
#         ax.plot(X[dataind])
#         ax.text(0.05, 0.9,
#                 f"$\\mu$={xs[dataind]:1.3f}\n$\\sigma$={ys[dataind]:1.3f}",
#                 transform=ax.transAxes, verticalalignment='top')
#         ax.set_ylim(-0.5, 1.5)
#     fig.show()
#     return True
#
#
# fig.canvas.mpl_connect('pick_event', onpick)
# plt.show()

# import numpy as np
# import matplotlib.pyplot as plt
#
# fig, ax = plt.subplots()
# ax.set_title('click on points')
#
# line, = ax.plot(np.random.rand(100), 'o',
#                 picker=True, pickradius=5)  # 5 points tolerance
#
# def onpick(event):
#     thisline = event.artist
#     print(thisline)
#     xdata = thisline.get_xdata()
#     ydata = thisline.get_ydata()
#     ind = event.ind
#     points = tuple(zip(xdata[ind], ydata[ind]))
#     print('onpick points:', points)
#
# fig.canvas.mpl_connect('pick_event', onpick)
#
# plt.show()


# from datetime import datetime
#
# print(datetime.fromtimestamp(19122.216743328278))

# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle
#
#
# class Square():
#     def __init__(self, rect):
#         self.rect = rect
#         canvas = self.rect.figure.canvas
#         self.rect.set_animated(True)
#         canvas.draw()
#         self.background = canvas.copy_from_bbox(self.rect.axes.bbox)
#
#         self.cid = self.rect.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
#
#     def on_motion(self, event):
#         if event.inaxes != None:
#             self.rect.set_x(event.xdata)
#             self.rect.set_y(event.ydata)
#             canvas = self.rect.figure.canvas
#             axes = self.rect.axes
#
#             canvas.restore_region(self.background)
#
#             axes.draw_artist(self.rect)
#
#             canvas.blit(axes.bbox)
#
#
# fig, ax = plt.subplots(figsize=(10, 8))
# a = Rectangle((0.5, 0.5), -0.2, 0.2)
# ax.add_patch(a)
# sq = Square(a)
#
# plt.show()


# import numpy as np
# import matplotlib.pyplot as plt
#
# class DraggableRectangle:
#     lock = None  # only one can be animated at a time
#
#     def __init__(self, rect):
#         self.rect = rect
#         self.press = None
#         self.background = None
#
#     def connect(self):
#         """Connect to all the events we need."""
#         self.cidpress = self.rect.figure.canvas.mpl_connect(
#             'button_press_event', self.on_press)
#         self.cidrelease = self.rect.figure.canvas.mpl_connect(
#             'button_release_event', self.on_release)
#         self.cidmotion = self.rect.figure.canvas.mpl_connect(
#             'motion_notify_event', self.on_motion)
#
#     def on_press(self, event):
#         """Check whether mouse is over us; if so, store some data."""
#         if (event.inaxes != self.rect.axes
#                 or DraggableRectangle.lock is not None):
#             return
#         contains, attrd = self.rect.contains(event)
#         if not contains:
#             return
#         print('event contains', self.rect.xy)
#         self.press = self.rect.xy, (event.xdata, event.ydata)
#         DraggableRectangle.lock = self
#
#         # draw everything but the selected rectangle and store the pixel buffer
#         canvas = self.rect.figure.canvas
#         axes = self.rect.axes
#         self.rect.set_animated(True)
#         canvas.draw()
#         self.background = canvas.copy_from_bbox(self.rect.axes.bbox)
#
#         # now redraw just the rectangle
#         axes.draw_artist(self.rect)
#
#         # and blit just the redrawn area
#         canvas.blit(axes.bbox)
#
#     def on_motion(self, event):
#         """Move the rectangle if the mouse is over us."""
#         if (event.inaxes != self.rect.axes
#                 or DraggableRectangle.lock is not self):
#             return
#         (x0, y0), (xpress, ypress) = self.press
#         dx = event.xdata - xpress
#         dy = event.ydata - ypress
#         self.rect.set_x(x0+dx)
#         self.rect.set_y(y0+dy)
#
#         canvas = self.rect.figure.canvas
#         axes = self.rect.axes
#         # restore the background region
#         canvas.restore_region(self.background)
#
#         # redraw just the current rectangle
#         axes.draw_artist(self.rect)
#
#         # blit just the redrawn area
#         canvas.blit(axes.bbox)
#
#     def on_release(self, event):
#         """Clear button press information."""
#         if DraggableRectangle.lock is not self:
#             return
#
#         self.press = None
#         DraggableRectangle.lock = None
#
#         # turn off the rect animation property and reset the background
#         self.rect.set_animated(False)
#         self.background = None
#
#         # redraw the full figure
#         self.rect.figure.canvas.draw()
#
#     def disconnect(self):
#         """Disconnect all callbacks."""
#         self.rect.figure.canvas.mpl_disconnect(self.cidpress)
#         self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
#         self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
#
# fig, ax = plt.subplots()
# rects = ax.bar(range(10), 20*np.random.rand(10))
# drs = []
# for rect in rects:
#     dr = DraggableRectangle(rect)
#     dr.connect()
#     drs.append(dr)
#
# plt.show()

# class SelectFromCollection:
#     """
#     Select indices from a matplotlib collection using `PolygonSelector`.
#
#     Selected indices are saved in the `ind` attribute. This tool fades out the
#     points that are not part of the selection (i.e., reduces their alpha
#     values). If your collection has alpha < 1, this tool will permanently
#     alter the alpha values.
#
#     Note that this tool selects collection objects based on their *origins*
#     (i.e., `offsets`).
#
#     Parameters
#     ----------
#     ax : `~matplotlib.axes.Axes`
#         Axes to interact with.
#     collection : `matplotlib.collections.Collection` subclass
#         Collection you want to select from.
#     alpha_other : 0 <= float <= 1
#         To highlight a selection, this tool sets all selected points to an
#         alpha value of 1 and non-selected points to *alpha_other*.
#     """
#
#     def __init__(self, ax, collection, alpha_other=0.3):
#         self.canvas = ax.figure.canvas
#         self.collection = collection
#         self.alpha_other = alpha_other
#
#         self.xys = collection.get_offsets()
#         self.Npts = len(self.xys)
#
#         # Ensure that we have separate colors for each object
#         self.fc = collection.get_facecolors()
#         if len(self.fc) == 0:
#             raise ValueError('Collection must have a facecolor')
#         elif len(self.fc) == 1:
#             self.fc = np.tile(self.fc, (self.Npts, 1))
#
#         self.poly = PolygonSelector(ax, self.onselect)
#         self.ind = []
#
#     def onselect(self, verts):
#         path = Path(verts)
#         self.ind = np.nonzero(path.contains_points(self.xys))[0]
#         self.fc[:, -1] = self.alpha_other
#         self.fc[self.ind, -1] = 1
#         self.collection.set_facecolors(self.fc)
#         self.canvas.draw_idle()
#
#     def disconnect(self):
#         self.poly.disconnect_events()
#         self.fc[:, -1] = 1
#         self.collection.set_facecolors(self.fc)
#         self.canvas.draw_idle()
#
#
# if __name__ == '__main__':
#     import matplotlib.pyplot as plt
#
#     fig, ax = plt.subplots()
#     grid_size = 5
#     grid_x = np.tile(np.arange(grid_size), grid_size)
#     grid_y = np.repeat(np.arange(grid_size), grid_size)
#     pts = ax.scatter(grid_x, grid_y)
#
#     selector = SelectFromCollection(ax, pts)
#
#     print("Select points in the figure by enclosing them within a polygon.")
#     print("Press the 'esc' key to start a new polygon.")
#     print("Try holding the 'shift' key to move all of the vertices.")
#     print("Try holding the 'ctrl' key to move a single vertex.")
#
#     plt.show()
#
#     selector.disconnect()
#
#     # After figure is closed print the coordinates of the selected points
#     print('\nSelected points:')
#     print(selector.xys[selector.ind])


# import pyvista as pv
#
# mesh = pv.Sphere()
# p = pv.Plotter(notebook=False)
# p.add_mesh(mesh)
# p.show()

# import tkinter
# import pyvista
#
# from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor
#
#
# # Setup for root window
# root = tkinter.Tk()
# root.title("pyvista tk Demo")
#
# frame = tkinter.Frame(root)
# frame.pack(fill=tkinter.BOTH, expand=1, side=tkinter.TOP)
#
# # create an instance of a pyvista.Plotter to be used for tk
# mesh = pyvista.Sphere()
# pl = pyvista.Plotter()
# pl.add_mesh(mesh)
#
# # Setup for rendering window interactor
# renwininteract = vtkTkRenderWindowInteractor(root, rw=pl.ren_win,
#                                              width=400, height=400)
# renwininteract.Initialize()
# renwininteract.pack(side='top', fill='both', expand=1)
# renwininteract.Start()
#
# # Begin execution by updating the renderer and starting the tkinter
# # loop
# pl.render()
# root.mainloop()

# import lasio
# import numpy as np
# import PySimpleGUI as sg
# from datetime import datetime
#
#
# # чтение las файлов
# def load_las(file_names):
#     data = []
#     for i in file_names:
#         file = lasio.read(i)
#         date = datetime.strptime(file.well['DATE'].value, '%d.%m.20%y %H-%M-%S')
#         data.append((date, file))
#     data = np.array(data)
#     return data[data[:, 0].argsort()]
#
#
# filenames = sg.popup_get_file('Load data', multiple_files=True, no_window=True)
# data = load_las(filenames)
#
# print(data)

# def change_file(path, out):
#     file = open(path)
#
#     line = [0]
#     lines = []
#     while len(line) != 0:
#         line = file.readline()
#         lines.append(line)
#     file.close()
#
#     new_lines = []
#     bad_lines = 0
#
#     for i in lines[:-1]:
#         if i[0] != ',':
#             i = i.replace(',', '\t')
#             i = i.replace(':', '\t')
#             new_lines.append(i)
#         else:
#             bad_lines = bad_lines + 1
#
#     edit_file = open(out, 'w')
#     for i in new_lines:
#         edit_file.write(i)
#     edit_file.close()
#
#     return bad_lines
#
#
# f = r'D:\Temp\Work\ПУ-21\raw.txt'
# a = change_file(f, r'D:\Temp\Work\ПУ-21\file.txt')
# print(a)


# def make_header(lines):
#
#     names = ['X', 'Y', 'Z']
#
#     elements = []
#     element = ''
#     for j in lines:
#         for i in j:
#             if i != '_':
#                 element = element + i
#             else:
#                 elements.append(element)
#                 element = ''
#                 break
#
#     header = []
#     for i in elements:
#         for j in names:
#             header.append(i + '_' + j)
#
#     header.append('PR_DateTime')
#
#     return header
#
#
# def read_three(path, out):
#
#     file = open(path)
#
#     a1 = file.readline()
#     a2 = file.readline()
#     a3 = file.readline()
#
#     header = make_header([a1, a2, a3])
#
#     all_parts = []
#     file = open(path)
#     while len(a1) != 0:
#
#         part = []
#         a1 = file.readline()
#         a2 = file.readline()
#         a3 = file.readline()
#         three_lines = [a1, a2, a3]
#
#         element = ''
#         for line in three_lines:
#             for i in line:
#                 if i != ',' and i != '\n':
#                     element = element + i
#                 else:
#                     if len(element) != 0:
#                         for head_name in header:
#                             if head_name in element:
#                                 part.append(element)
#                     element = ''
#         if len(part) == len(header):
#             all_parts.append(part)
#
#     data = {}
#     for i in header:
#         data[i] = []
#
#     for part in all_parts:
#         for element in part:
#             for head in header:
#                 if head in element:
#                     data[head].append(element[len(head):])
#
#     return
#
#
# path = r'D:\Temp\Work\ПУ-21\GPS Data\loc\GPS.log'
#
# read_three(path, '11')
#
# import PySimpleGUI as sg
#
# print(sg.theme_list())

# import numpy as np
#
# time_data = np.load(r'PU21\parasound\time_data.npy')
# loc_data = np.load(r'PU21\parasound\loc_data.npy')
# loc_x = np.load(r'PU21\parasound\loc_X.npy')
#
# print((min(time_data), max(time_data)))
# print((min(loc_data), max(loc_data)))

# def get_coord(line):
#     h = ''
#     value = ''
#     for i in line:
#         if value != '' and i == ' ':
#             break
#         if '">' in h:
#             value = value + i
#         if '">' not in h:
#             h = h + i
#     return float(value)
#
#
# text = '			<lon noItems="3">3.497222e-001 3.497210e-001 3.497197e-001 </lon>'
#
# print(get_coord(text))

# import numpy as np
# import matplotlib.pyplot as plt
#
# loc = np.load('PU21/parasound/loc_data.npy')
# data = np.load('PU21/parasound/time_data.npy')
# x = np.load('PU21/parasound/loc_x.npy')
#
# interp = np.interp(data, loc, x)
#
# fig = plt.figure()
# plt.plot(loc, x, '.')
# plt.plot(data, interp, '.')
# plt.show()

# import shutil
#
# shutil.copy(r'D:\Temp\NSU\Средний бал.xlsx', r'D:\Temp')

# from datetime import datetime
#
# a = 'PS3SLF_2022-08-07T151128Z_00457568.asd'
# b = 'PS3SLF_2022-08-07T150128Z_00457568.asd'
#
# print(a[-4:])

import PySimpleGUI as pg

help(pg.popup_error)
