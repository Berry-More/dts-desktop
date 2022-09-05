import lasio
import numpy as np
import pyvista as pv
from os.path import join
import PySimpleGUI as sg
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.dates import date2num, num2date, AutoDateLocator


color_list = ['mediumblue', 'dodgerblue', 'lightskyblue',
              'springgreen', 'greenyellow', 'yellow',
              'darkorange', 'firebrick']
new_color_map = LinearSegmentedColormap.from_list('my_color_map', colors=color_list, N=256)


# функция для обновления меню
def make_menu(col, inter, sets):
    colors = col.copy()
    inters = inter.copy()

    if sets[0] != new_color_map:
        cid = col.index(sets[0])
        colors[cid] = colors[cid] + ' ✔'
    else:
        colors[0] = colors[0] + ' ✔'
    iid = inter.index(sets[1])
    inters[iid] = inters[iid] + ' ✔'

    menu = [['File', ['Open',
                      'Edit', ['Figure', ['Color bar', colors,
                                          'Interpolation', inters]],
                      'Exit']],
            ['Help']]

    return menu


# чтение las файлов
def load_las(file_names):
    data = []
    for i in range(len(file_names)):
        file = lasio.read(file_names[i])
        date = datetime.strptime(file.well['DATE'].value, '%d.%m.20%y %H-%M-%S')
        data.append((date, file))
        sg.one_line_progress_meter('Loading files', i + 1, len(file_names))
    data = np.array(data)
    return data[data[:, 0].argsort()]


def log_print(window: sg.Window, text: str, color: str):
    text = str(datetime.now())[:-7] + ' : ' + text
    window['-OUT-'].print(text, text_color=color)
    return


# поиск ближайшей по значению точки в массиве
def find_point(x, point):
    return list(np.abs(np.array(x)-point)).index(min(np.abs(np.array(x)-point)))


def find_2_points(x, y, xs, ys):
    x_ind = []
    for i in xs:
        x_ind.append(find_point(x, i))

    y_ind = []
    for i in ys:
        y_ind.append(find_point(y, i))

    return [x_ind, y_ind]


# класс отрисовки профиля (горизонтального и вертикального)
# сделано очень херово, по другому придумать не сумел(
class Profile:
    def __init__(self, line, xaxis, yaxis, matrix):
        self.line = line  # plt.plot - рисунок который будем выводить (пустой)
        self.xaxis = xaxis  # ось времен
        self.yaxis = yaxis  # ось расстояния
        self.matrix = matrix  # матрица температур
        self.xs = list(line.get_xdata())  # значения времени в пикируемых точках
        self.ys = list(line.get_ydata())  # значения расстояния в пикируемых точках

        # Контроль событий
        self.cidpicking = 0  # переменная отвечающая за отклик по нажатию мыши
        self.cidmotion = 0  # переменная отвечающая за движение мыши

        # Отрисовка профиля
        canvas = self.line.figure.canvas
        self.line.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.line.axes.bbox)

    def disconnect(self):
        self.line.figure.canvas.mpl_disconnect(self.cidpicking)
        self.line.figure.canvas.mpl_disconnect(self.cidmotion)

    def motion_y(self, event):
        if len(self.xs) == 1:
            return
        self.line.set_data([event.xdata, event.xdata], [min(self.yaxis), max(self.yaxis)])

        canvas = self.line.figure.canvas
        axes = self.line.axes
        canvas.restore_region(self.background)
        axes.draw_artist(self.line)
        canvas.blit(axes.bbox)

    def picking_y(self, event):
        # пикирование
        if event.button == 1:  # условие при нажатии на левую кнопку мыши
            if event.inaxes != self.line.axes:
                return
            self.xs.append(event.xdata)  # добавляем в массив с х
            self.ys.append(event.ydata)  # добавляем в массив с у
            self.line.set_data(self.xs, self.ys)  # обновляем данные рисунка
            self.line.figure.canvas.draw()  # перерисывываем

            # отрисовка профиля
            if len(self.xs) == 1:  # Когда
                self.disconnect()
                index = find_point(self.xaxis, self.xs[0])

                # рисовка профиля
                fig, ax = plt.subplots(figsize=(8, 5))
                fig.canvas.set_window_title('Profile')
                plt.plot(self.yaxis, self.matrix[index], alpha=0.7, linewidth=1)
                plt.xlabel('Depth, m')
                plt.ylabel('Temperature, C')
                fig.show()

                self.xs = []
                self.ys = []

    def motion_x(self, event):
        if len(self.xs) == 1:
            return
        self.line.set_data([min(self.xaxis), max(self.xaxis)], [event.ydata, event.ydata])

        canvas = self.line.figure.canvas
        axes = self.line.axes
        canvas.restore_region(self.background)
        axes.draw_artist(self.line)
        canvas.blit(axes.bbox)

    def picking_x(self, event):
        # пикирование
        if event.button == 1:  # условие при нажатии на левую кнопку мыши
            if event.inaxes != self.line.axes:
                return
            self.xs.append(event.xdata)  # добавляем в массив с х
            self.ys.append(event.ydata)  # добавляем в массив с у
            self.line.set_data(self.xs, self.ys)  # обновляем данные рисунка
            self.line.figure.canvas.draw()  # перерисывываем

            # отрисовка профиля
            if len(self.xs) == 1:  # Когда
                self.disconnect()
                index = find_point(self.yaxis, self.ys[0])

                # рисовка профиля
                fig, ax = plt.subplots(figsize=(8, 5))
                fig.canvas.set_window_title('Profile')
                plt.plot(self.xaxis, np.array(self.matrix).T[index], alpha=0.7, linewidth=1)
                plt.xlabel('Time, date')
                plt.ylabel('Temperature, C')
                ax.xaxis_date()
                ax.xaxis.set_major_locator(AutoDateLocator(minticks=3, maxticks=6))
                fig.autofmt_xdate(rotation=0, ha='center')
                fig.show()

                self.xs = []
                self.ys = []


class AverageRectangle:
    def __init__(self, rect, xaxis, yaxis, matrix):
        self.rect = rect
        self.xaxis = xaxis  # ось времен
        self.yaxis = yaxis  # ось расстояния
        self.matrix = matrix  # матрица температур
        self.xs = []  # значения времени в пикируемых точках
        self.ys = []  # значения расстояния в пикируемых точках
        self.press = False

        # Контроль событий
        self.cidpicking = 0  # переменная отвечающая за отклик по нажатию мыши
        self.cidmotion = 0  # переменная отвечающая за движение мыши
        self.cidrelease = 0

        # Отрисовка профиля
        canvas = self.rect.figure.canvas
        self.rect.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

    def disconnect(self):
        self.rect.figure.canvas.mpl_disconnect(self.cidpicking)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.draw()  # перерисывываем

    def picking(self, event):
        if event.button == 1:  # условие при нажатии на левую кнопку мыши
            if event.inaxes != self.rect.axes:
                return
            self.press = True
            self.xs.append(event.xdata)  # добавляем в массив с х
            self.ys.append(event.ydata)  # добавляем в массив с у
            self.rect.set_x(self.xs[0])  # обновляем данные рисунка
            self.rect.set_y(self.ys[0])
            self.rect.figure.canvas.draw()  # перерисывываем

    def release_x(self, event):
        if len(self.xs) == 1:
            self.press = False
            if event.xdata != None:
                self.xs.append(event.xdata)
                self.ys.append(event.ydata)
            else:
                self.xs = []
                self.ys = []
                self.disconnect()
                return
            self.disconnect()
            points = find_2_points(self.xaxis, self.yaxis, self.xs, self.ys)
            matrix_for_average = []

            for i in range(min(points[0]), max(points[0])+1):
                matrix_for_average.append(self.matrix[i][min(points[1]):max(points[1])])

            # рисовка профиля
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.canvas.set_window_title('Average profile')
            plt.plot(self.yaxis[min(points[1]):max(points[1])],
                     np.sum(np.array(matrix_for_average)/(max(points[0])+1 - min(points[0])), axis=0),
                     alpha=0.7, linewidth=1)
            plt.xlabel('Depth, m')
            plt.ylabel('Temperature, C')
            fig.show()

            self.xs = []
            self.ys = []

    def release_y(self, event):
        if len(self.xs) == 1:
            self.press = False
            if event.xdata != None:
                self.xs.append(event.xdata)
                self.ys.append(event.ydata)
            else:
                self.xs = []
                self.ys = []
                self.disconnect()
                return
            self.disconnect()
            points = find_2_points(self.xaxis, self.yaxis, self.xs, self.ys)
            matrix_for_average = []

            for i in range(min(points[0]), max(points[0])+1):
                matrix_for_average.append(self.matrix[i][min(points[1]):max(points[1])])

            # рисовка профиля
            fig, ax = plt.subplots(figsize=(8, 5))
            fig.canvas.set_window_title('Average profile')
            plt.plot(self.xaxis[min(points[0]):max(points[0])+1],
                     np.sum(np.array(matrix_for_average)/(max(points[1]) - min(points[1])), axis=1),
                     alpha=0.7, linewidth=1)
            plt.xlabel('Time, date')
            plt.ylabel('Temperature, C')
            ax.xaxis_date()
            ax.xaxis.set_major_locator(AutoDateLocator(minticks=3, maxticks=6))
            fig.autofmt_xdate(rotation=0, ha='center')
            fig.show()

            self.xs = []
            self.ys = []

    def motion(self, event):
        if event.inaxes != None and self.press == True:
            if len(self.xs) == 2:
                return

            if len(self.xs) == 1:
                self.rect.set_width(event.xdata - self.xs[0])  # по оси х
                self.rect.set_height(event.ydata - self.ys[0])  # по оси y

            canvas = self.rect.figure.canvas
            axes = self.rect.axes
            canvas.restore_region(self.background)
            axes.draw_artist(self.rect)
            canvas.blit(axes.bbox)


class ExportRectangle:
    def __init__(self, rect, xaxis, yaxis, matrix):
        self.rect = rect
        self.xaxis = xaxis  # ось времен
        self.yaxis = yaxis  # ось расстояния
        self.matrix = matrix  # матрица температур
        self.xs = []  # значения времени в пикируемых точках
        self.ys = []  # значения расстояния в пикируемых точках

        # Контроль событий
        self.cidpicking = 0  # переменная отвечающая за отклик по нажатию мыши
        self.cidmotion = 0  # переменная отвечающая за движение мыши

        # Отрисовка профиля
        canvas = self.rect.figure.canvas
        self.rect.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

    def disconnect(self):
        self.rect.figure.canvas.mpl_disconnect(self.cidpicking)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
        self.rect.figure.canvas.draw()  # перерисывываем

    def motion(self, event):
        if event.inaxes != None:
            if len(self.xs) == 2:
                return

            if len(self.xs) == 1:
                self.rect.set_width(event.xdata - self.xs[0])  # по оси х
                self.rect.set_height(event.ydata - self.ys[0])  # по оси y

            canvas = self.rect.figure.canvas
            axes = self.rect.axes
            canvas.restore_region(self.background)
            axes.draw_artist(self.rect)
            canvas.blit(axes.bbox)

    def picking(self, event):
        if event.button == 1:  # условие при нажатии на левую кнопку мыши
            if event.inaxes != self.rect.axes:
                return
            self.xs.append(event.xdata)  # добавляем в массив с х
            self.ys.append(event.ydata)  # добавляем в массив с у
            self.rect.set_x(self.xs[0])  # обновляем данные рисунка
            self.rect.set_y(self.ys[0])
            self.rect.figure.canvas.draw()  # перерисывываем

        if len(self.xs) == 2:
            self.disconnect()
            points = find_2_points(self.xaxis, self.yaxis, self.xs, self.ys)
            d1 = min(points[1])
            d2 = max(points[1])
            folder_path = sg.popup_get_folder('Folder for export', no_window=True)

            if folder_path != '':
                for i in range(min(points[0]), max(points[0])):
                    las_file = lasio.LASFile()
                    las_file.well['DATE'] = num2date(self.xaxis[i]).strftime('%d.%m.20%y %H-%M-%S')

                    las_file.add_curve('DEPTH', self.yaxis[d1:d2], unit='M', descr='DEPTH')
                    las_file.add_curve('TEMP', self.matrix[i][d1:d2], unit='DEGR', descr='TEMPERATURE')

                    las_file.write(join(folder_path, las_file.well['DATE'].value + '.las'), version=2)

            self.xs = []
            self.ys = []


# https://jakevdp.github.io/PythonDataScienceHandbook/04.11-settings-and-stylesheets.html

# функция отрисовки матрицы в 2D
def make_figure_2d(data, settings):
    # задание осей и матрицы
    x_t = []
    y = data[0][1]['DEPTH']
    z = []

    for i in data:
        x_t.append(i[0])
        z.append(i[1]['TEMP'])
    x = date2num(x_t)

    for i in z:
        if len(z[0]) != len(i):
            return 0

    # отрисовка
    with plt.style.context('bmh'):
        fig, ax = plt.subplots(figsize=(9, 8))
        fig.canvas.set_window_title('Visualisation 2D')
        graph = ax.imshow(np.array(z).T, cmap=settings[0],
                          interpolation=settings[1],
                          origin='lower', aspect='auto',
                          extent=[min(x), max(x), min(y), max(y)])
        ax.xaxis_date()
        fig.autofmt_xdate(rotation=0, ha='center')
        ax.xaxis.set_major_locator(AutoDateLocator(minticks=2, maxticks=7))
        plt.ylabel('Depth, m')
        plt.xlabel('Time, date')
        fig.colorbar(graph, ax=ax)
        plt.subplots_adjust(left=0.08, right=0.9, bottom=0.07, top=0.965)
        ax.invert_yaxis()

        # ------------------------------- Кнопки отрисовки профилей -------------------------------------
        plt.figtext(0.925, 0.9, 'Profile', size=13, ha='center')  # подпись для кнопок

        line, = ax.plot([], [], '-', c='black', linewidth=0.75)  # пустая линия
        p = Profile(line, x, y, z)  # элемент класса профиль

        # по Time
        ax_prof_x_button = plt.axes([0.875, 0.84, 0.05, 0.05])
        profile_x_button = Button(ax_prof_x_button, 'T', color='white', hovercolor='grey')

        def prof_x_button_func(event):
            p.disconnect()
            a.disconnect()
            e.disconnect()

            p.cidpicking = p.line.figure.canvas.mpl_connect('button_press_event', p.picking_x)
            p.cidmotion = p.line.figure.canvas.mpl_connect('motion_notify_event', p.motion_x)

        profile_x_button.on_clicked(prof_x_button_func)

        # по Depth
        ax_prof_y_button = plt.axes([0.925, 0.84, 0.05, 0.05])  # xposition, yposition, width, height
        profile_y_button = Button(ax_prof_y_button, 'D', color='white', hovercolor='grey')

        def prof_y_button_func(event):
            p.disconnect()
            a.disconnect()
            e.disconnect()

            p.cidpicking = p.line.figure.canvas.mpl_connect('button_press_event', p.picking_y)
            p.cidmotion = p.line.figure.canvas.mpl_connect('motion_notify_event', p.motion_y)
        profile_y_button.on_clicked(prof_y_button_func)

        # -----------------------------------------------------------------------------------------------

        # ------------------------- Кнопки осредненных по интервалу профилей ----------------------------
        plt.figtext(0.925, 0.775, 'Average', size=13, ha='center')

        rect = Rectangle((min(x), min(y)), 0, 0, fill=False, color='black', linewidth=1)
        ax.add_patch(rect)
        a = AverageRectangle(rect, x, y, z)

        rect_export = Rectangle((min(x), min(y)), 0, 0, fill=False,
                                color='white', linewidth=1, linestyle='dashed')
        ax.add_patch(rect_export)
        e = ExportRectangle(rect_export, x, y, z)

        # профиль по Time
        ax_av_y_button = plt.axes([0.875, 0.715, 0.05, 0.05])
        average_y_button = Button(ax_av_y_button, 'T', color='white', hovercolor='grey')

        def av_y_button_func(event):
            p.disconnect()
            a.disconnect()
            e.disconnect()

            a.rect.set_height(0)
            a.rect.set_width(0)
            a.cidpicking = a.rect.figure.canvas.mpl_connect('button_press_event', a.picking)
            a.cidmotion = a.rect.figure.canvas.mpl_connect('motion_notify_event', a.motion)
            a.cidrelease = a.rect.figure.canvas.mpl_connect('button_release_event', a.release_y)

        average_y_button.on_clicked(av_y_button_func)

        # профиль по Depth
        ax_av_x_button = plt.axes([0.925, 0.715, 0.05, 0.05])
        average_x_button = Button(ax_av_x_button, 'D', color='white', hovercolor='grey')

        def av_x_button_func(event):
            p.disconnect()
            a.disconnect()
            e.disconnect()

            a.rect.set_height(0)
            a.rect.set_width(0)
            a.cidpicking = a.rect.figure.canvas.mpl_connect('button_press_event', a.picking)
            a.cidmotion = a.rect.figure.canvas.mpl_connect('motion_notify_event', a.motion)
            a.cidrelease = a.rect.figure.canvas.mpl_connect('button_release_event', a.release_x)
        average_x_button.on_clicked(av_x_button_func)

        # -----------------------------------------------------------------------------------------------

        # --------------------------------- Кнопка экспорта ---------------------------------------------

        plt.figtext(0.925, 0.650, 'Export data', size=13, ha='center')

        ax_export_button = plt.axes([0.875, 0.59, 0.1, 0.05])
        export_button = Button(ax_export_button, 'Cut', color='white', hovercolor='grey')

        def ex_button_func(event):
            p.disconnect()
            a.disconnect()
            e.disconnect()

            e.rect.set_height(0)
            e.rect.set_width(0)
            e.cidpicking = e.rect.figure.canvas.mpl_connect('button_press_event', e.picking)
            e.cidmotion = e.rect.figure.canvas.mpl_connect('motion_notify_event', e.motion)

        export_button.on_clicked(ex_button_func)

        plt.show(block=True)

    return 1


# функция отрисовки матрицы в 3D
def make_figure_3d(data, settings):
    # задание осей и матрицы
    x = []
    y = data[0][1]['DEPTH']
    z = []

    for i in data:
        x.append(i[0].timestamp())
        z.append(list(i[1]['TEMP']))
    x = (np.array(x) - min(x))/60

    for i in z:
        if len(z[0]) != len(i):
            return 0

    points = []
    for i in range(len(z)):
        for j in range(len(z[i])):
            points.append([x[i], y[j], z[i][j]])

    cloud = pv.PolyData(points)
    surf = cloud.delaunay_2d()
    surf['Temperature'] = np.reshape(z, len(z) * len(z[0]))

    # surf.rotate_z(180, inplace=True)
    surf.scale([1/max(x), 1/max(y), 0.5/np.matrix(z).max()], inplace=True)

    pv.global_theme.cmap = settings[0]
    pv.global_theme.font.color = 'black'

    p = pv.Plotter(notebook=False)
    # p.set_scale(xscale=10/max(x), yscale=10/max(y), zscale=5/np.matrix(z).max())
    p.set_background('white')
    p.add_mesh(surf)
    p.show_grid(xlabel="Time [min]", ylabel="Depth [m]", zlabel="Temperature [C]")
    p.add_camera_orientation_widget()
    p.show(title='Visualisation 3D')

    return 1
