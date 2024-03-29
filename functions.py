import lasio
import PySimpleGUI
import numpy as np
import pyvista as pv
import matplotlib.pyplot as plt

from os.path import join
from datetime import datetime
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
        PySimpleGUI.one_line_progress_meter('Loading files', i + 1, len(file_names),
                                            no_titlebar=True, no_button=True, bar_color=('limegreen',
                                                                                         'grey80'))
    data = np.array(data)
    return data[data[:, 0].argsort()]


def log_print(window: PySimpleGUI.Window, text: str, color: str):
    text = str(datetime.now())[:-7] + ' : ' + text
    window['-OUT-'].print(text, text_color=color)


# поиск ближайшей по значению точки в массиве
def find_point(x, point):
    return np.argmin(np.abs(np.array(x) - point))


def find_2_points(x, y, xs, ys):
    x_ind = []
    for i in xs:
        x_ind.append(find_point(x, i))

    y_ind = []
    for i in ys:
        y_ind.append(find_point(y, i))

    return [x_ind, y_ind]


# коррекция оси
def get_extend(x, y):
    x_comp = (max(x) - min(x)) * 0.1 * (1/len(x))
    y_comp = (max(y) - min(y)) * 0.1 * (1 / len(y))
    return [min(x) - x_comp, max(x) + x_comp, min(y) - y_comp, max(y) + y_comp]


# класс отрисовки профиля (горизонтального и вертикального)
# сделано очень херово, по другому придумать не сумел(
class Profile:
    def __init__(self, line, x_axis, y_axis, matrix, f1d=None, f1t=None):
        self.line = line  # plt.plot - рисунок который будем выводить (пустой)
        self.background = 0  # Изображение матрицы, которое мы храним, когда профиль движется
        self.x_axis = x_axis  # ось времен
        self.y_axis = y_axis  # ось расстояния
        self.matrix = matrix  # матрица температур
        self.xs = list(line.get_xdata())  # значения времени в пикируемых точках
        self.ys = list(line.get_ydata())  # значения расстояния в пикируемых точкха
        self.traces = []

        self.f1d = f1d or 0
        self.f1t = f1t or 0

        self.fig = 0
        self.ax = 0

        # Контроль событий
        self.cid_picking = 0  # переменная отвечающая за отклик по нажатию мыши
        self.cid_motion = 0  # переменная отвечающая за движение мыши

    def disconnect(self):
        self.line.figure.canvas.mpl_disconnect(self.cid_picking)
        self.line.figure.canvas.mpl_disconnect(self.cid_motion)

    def update(self):
        canvas = self.line.figure.canvas
        self.line.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.line.axes.bbox)

    def clear(self):
        for i in self.traces:
            i = i.pop(0)
            i.remove()
        self.traces = []
        self.update()

    def motion_y(self, event):
        if len(self.xs) == 1:
            return
        self.line.set_data([event.xdata, event.xdata], [min(self.y_axis), max(self.y_axis)])

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

            # отрисовка профиля
            if len(self.xs) == 1:  # Когда
                self.disconnect()

                index = find_point(self.x_axis, self.xs[0])

                self.traces.append(self.line.axes.plot([self.xs[0], self.xs[0]],
                                                       [min(self.y_axis), max(self.y_axis)],
                                                       c='black', linewidth=0.75, linestyle='--'))
                # рисовка профиля
                if self.f1d == 0 or not plt.fignum_exists(self.f1d.fig.number):
                    self.f1d = FigureDepth()
                    self.f1d.draw_line({'DEPTH': self.y_axis, 'TEMP': self.matrix[index]},
                                       num2date(self.xs[0]).strftime('%H:%M:%S %m-%d-%Y'))
                else:
                    self.f1d.draw_line({'DEPTH': self.y_axis, 'TEMP': self.matrix[index]},
                                       num2date(self.xs[0]).strftime('%H:%M:%S %m-%d-%Y'))

                self.xs = []
                self.ys = []

                self.update()

    def motion_x(self, event):
        if len(self.xs) == 1:
            return
        self.line.set_data([min(self.x_axis), max(self.x_axis)], [event.ydata, event.ydata])

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

            axes = self.line.axes
            self.traces.append(axes.plot([min(self.x_axis), max(self.x_axis)], [self.ys[0], self.ys[0]],
                                         c='black', linewidth=0.75, linestyle='--'))

            # отрисовка профиля
            if len(self.xs) == 1:  # Когда
                self.disconnect()
                index = find_point(self.y_axis, self.ys[0])

                # рисовка профиля
                if self.f1t == 0 or not plt.fignum_exists(self.f1t.fig.number):
                    self.f1t = FigureTime()
                    self.f1t.draw_line({'TIME': self.x_axis, 'TEMP': np.array(self.matrix).T[index]},
                                       str(self.y_axis[index]) + ' м')
                    plt.show(block=True)
                else:
                    self.f1t.draw_line({'TIME': self.x_axis, 'TEMP': np.array(self.matrix).T[index]},
                                       str(self.y_axis[index]) + ' м')

                self.xs = []
                self.ys = []

                self.update()


# класс для профиля через осредненную область
class AverageRectangle:
    def __init__(self, rect, x_axis, y_axis, matrix):
        self.rect = rect
        self.background = 0  # Изображение матрицы, которое мы храним, когда профиль движется
        self.x_axis = x_axis  # ось времен
        self.y_axis = y_axis  # ось расстояния
        self.matrix = matrix  # матрица температур
        self.xs = []  # значения времени в пикируемых точках
        self.ys = []  # значения расстояния в пикируемых точках
        self.press = False

        self.fig = 0
        self.ax = 0

        # Контроль событий
        self.cid_picking = 0  # переменная отвечающая за отклик по нажатию мыши
        self.cid_motion = 0  # переменная отвечающая за движение мыши
        self.cid_release = 0

    def disconnect(self):
        self.rect.figure.canvas.mpl_disconnect(self.cid_picking)
        self.rect.figure.canvas.mpl_disconnect(self.cid_motion)
        self.rect.figure.canvas.mpl_disconnect(self.cid_release)

    def update(self):
        canvas = self.rect.figure.canvas
        self.rect.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

    def picking(self, event):
        if event.button == 1:  # условие при нажатии на левую кнопку мыши
            if event.inaxes != self.rect.axes:
                return
            self.press = True
            self.xs.append(event.xdata)  # добавляем в массив с х
            self.ys.append(event.ydata)  # добавляем в массив с у
            self.rect.set_x(self.xs[0])  # обновляем данные рисунка
            self.rect.set_y(self.ys[0])

    def release_x(self, event):
        if len(self.xs) == 1:
            self.press = False
            if event.xdata is not None:
                self.xs.append(event.xdata)
                self.ys.append(event.ydata)
            else:
                self.xs = []
                self.ys = []
                self.disconnect()
                return
            self.disconnect()
            points = find_2_points(self.x_axis, self.y_axis, self.xs, self.ys)
            matrix_for_average = []
            for i in range(min(points[0]), max(points[0]) + 1):
                matrix_for_average.append(self.matrix[i][min(points[1]):max(points[1])])

            # рисовка профиля
            self.fig, self.ax = plt.subplots(figsize=(5, 8))
            self.fig.canvas.set_window_title('Average temperature log')
            plt.plot(np.sum(np.array(matrix_for_average) / (max(points[0]) + 1 - min(points[0])), axis=0),
                     self.y_axis[min(points[1]):max(points[1])],
                     alpha=0.7, linewidth=1)
            plt.ylabel('Measured depth, m')
            plt.xlabel('Temperature, °C')
            plt.subplots_adjust(left=0.15, right=0.95, bottom=0.07, top=0.965)
            self.ax.invert_yaxis()
            self.fig.show()

            self.xs = []
            self.ys = []

    def release_y(self, event):
        if len(self.xs) == 1:
            self.press = False
            if event.xdata is not None:
                self.xs.append(event.xdata)
                self.ys.append(event.ydata)
            else:
                self.xs = []
                self.ys = []
                self.disconnect()
                return
            self.disconnect()
            points = find_2_points(self.x_axis, self.y_axis, self.xs, self.ys)
            matrix_for_average = []

            for i in range(min(points[0]), max(points[0]) + 1):
                matrix_for_average.append(self.matrix[i][min(points[1]):max(points[1])])

            # рисовка профиля
            self.fig, self.ax = plt.subplots(figsize=(8, 5))
            self.fig.canvas.set_window_title('Average temperature log')
            plt.plot(self.x_axis[min(points[0]):max(points[0]) + 1],
                     np.sum(np.array(matrix_for_average) / (max(points[1]) - min(points[1])), axis=1),
                     alpha=0.7, linewidth=1)
            plt.xlabel('Date, time')
            plt.ylabel('Temperature, °C')
            self.ax.xaxis_date()
            self.ax.xaxis.set_major_locator(AutoDateLocator(minticks=3, maxticks=6))
            self.fig.autofmt_xdate(rotation=0, ha='center')
            plt.subplots_adjust(left=0.10, right=0.95, bottom=0.1, top=0.94)
            self.fig.show()

            self.xs = []
            self.ys = []

    def motion(self, event):
        if event.inaxes is not None and self.press is True:
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


# класс отвечающий за экспорт по области
class ExportRectangle:
    def __init__(self, rect, x_axis, y_axis, matrix):
        self.rect = rect
        self.background = 0  # Изображение матрицы, которое мы храним, когда профиль движется
        self.x_axis = x_axis  # ось времен
        self.y_axis = y_axis  # ось расстояния
        self.matrix = matrix  # матрица температур
        self.xs = []  # значения времени в пикируемых точках
        self.ys = []  # значения расстояния в пикируемых точках

        # Контроль событий
        self.cid_picking = 0  # переменная отвечающая за отклик по нажатию мыши
        self.cid_motion = 0  # переменная отвечающая за движение мыши

    def disconnect(self):
        self.rect.figure.canvas.mpl_disconnect(self.cid_picking)
        self.rect.figure.canvas.mpl_disconnect(self.cid_motion)

    def update(self):
        canvas = self.rect.figure.canvas
        self.rect.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.rect.axes.bbox)

    def motion(self, event):
        if event.inaxes is not None:
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

        if len(self.xs) == 2:
            self.disconnect()
            points = find_2_points(self.x_axis, self.y_axis, self.xs, self.ys)
            d1 = min(points[1])
            d2 = max(points[1])
            folder_path = PySimpleGUI.popup_get_folder('Folder for export', no_window=True)

            if folder_path != '':
                for i in range(min(points[0]), max(points[0])):
                    las_file = lasio.LASFile()
                    las_file.well['DATE'] = num2date(self.x_axis[i]).strftime('%d.%m.20%y %H-%M-%S')

                    las_file.add_curve('DEPTH', self.y_axis[d1:d2], unit='M', descr='DEPTH')
                    las_file.add_curve('TEMP', self.matrix[i][d1:d2], unit='DEGR', descr='TEMPERATURE')

                    las_file.write(join(folder_path, las_file.well['DATE'].value + '.las'), version=2)

            self.xs = []
            self.ys = []


# класс отрисовки 1D фигуры
class FigureDepth:
    def __init__(self, figure=None, axes=None):

        # figure settings
        plt.style.use('bmh')
        if figure is None and axes is None:
            self.fig, self.ax = plt.subplots(figsize=(5, 8))
            self.fig.canvas.set_window_title('Temperature log')
        else:
            self.fig, self.ax = figure, axes

        # axes settings
        self.ax.invert_yaxis()
        self.ax.set_xlabel('Temperature, °C')
        self.ax.set_ylabel('Measured depth, m')
        self.fig.subplots_adjust(bottom=0.07, top=0.965)

        # list of active plots
        self.current_plots = []
        self.borders = []
        self.signs = []

        # events
        self.fig.canvas.mpl_connect('key_press_event', self.button_clear)
        self.fig.canvas.mpl_connect('key_press_event', self.button_add)
        self.fig.canvas.mpl_connect('key_press_event', self.button_borders)

        self.cid_picking = 0

    def update(self):
        if len(self.current_plots) > 0:
            x_data = []
            for i in self.current_plots:
                x_data.append(i[0].get_xdata())
            x_data = np.matrix(x_data)
            self.ax.set_xlim(x_data.min() - x_data.max() * 0.05, x_data.max() + x_data.max() * 0.05)
            y_data = self.current_plots[0][0].get_ydata()
            self.ax.set_ylim(max(y_data), min(y_data))
        self.ax.legend()
        self.fig.canvas.draw()

    def draw_line(self, tab, name):
        if plt.fignum_exists(self.fig.number):
            self.current_plots.append(self.ax.plot(tab['TEMP'], tab['DEPTH'], alpha=0.7, linewidth=1, label=name))
            self.update()

    def clear(self):
        for i in self.current_plots:
            i = i.pop(0)
            i.remove()
        for i in range(len(self.borders)):
            b = self.borders[i].pop(0)
            b.remove()
            self.signs[i].remove()
        self.current_plots = []
        self.borders = []
        self.signs = []
        self.update()

    def picking(self, event):
        if event.button == 1:  # условие при нажатии на левую кнопку мыши
            if event.inaxes != self.ax:
                return
            self.borders.append(self.ax.plot([-1000, 1000],
                                             [event.ydata, event.ydata],
                                             alpha=1, linewidth=1, color='red'))

            text = PySimpleGUI.popup_get_text('Enter signature:')
            x_pos = self.ax.get_xlim()[0] + abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.01
            y_pos = event.ydata - abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.005
            self.signs.append(self.ax.text(x_pos, y_pos, text, alpha=1, color='red'))
            self.update()

    def button_clear(self, event):
        if event.key == 'c' or event.key == 'с':
            self.clear()

    def button_add(self, event):
        if event.key == 'a' or event.key == 'ф':
            base_line_path = PySimpleGUI.popup_get_file('Choose base line .las', no_window=True)

            if len(base_line_path) != 0:
                graph_label = PySimpleGUI.popup_get_text('Enter line name:')
                data = load_las([base_line_path])[0][1]
                self.current_plots.append(self.ax.plot(data['TEMP'], data['DEPTH'],
                                                       alpha=0.7, linewidth=1, label=graph_label))
                self.update()

    def button_borders(self, event):
        if event.key == 'b' or event.key == 'и':
            if self.cid_picking == 0:
                self.cid_picking = self.fig.canvas.mpl_connect('button_press_event', self.picking)
            else:
                self.fig.canvas.mpl_disconnect(self.cid_picking)
                self.cid_picking = 0


# ПЕРЕДЕЛАТЬ ДЛЯ ОСРЕДНЕНИЙ ТОЖЕ
class FigureTime:
    def __init__(self):

        # figure settings
        plt.style.use('bmh')
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.fig.canvas.set_window_title('Temperature log')

        # axes settings
        self.ax.set_xlabel('Date, time')
        self.ax.set_ylabel('Temperature, °C')
        self.ax.xaxis_date()
        self.ax.xaxis.set_major_locator(AutoDateLocator(minticks=3, maxticks=6))
        self.fig.autofmt_xdate(rotation=0, ha='center')
        plt.subplots_adjust(left=0.08, right=0.95, bottom=0.1, top=0.94)

        # list of active plots
        self.current_plots = []
        self.borders = []
        self.signs = []

        # events
        self.fig.canvas.mpl_connect('key_press_event', self.button_clear)
        self.fig.canvas.mpl_connect('key_press_event', self.button_borders)

        self.cid_picking = 0

    def update(self):
        if len(self.current_plots) > 0:
            y_data = []
            for i in self.current_plots:
                y_data.append(i[0].get_ydata())
            y_data = np.matrix(y_data)
            self.ax.set_ylim(y_data.min() - y_data.max() * 0.05, y_data.max() + y_data.max() * 0.05)
            x_data = self.current_plots[0][0].get_xdata()
            self.ax.set_xlim(max(x_data), min(x_data))
        self.ax.legend()
        self.ax.invert_xaxis()
        self.fig.canvas.draw()

    def draw_line(self, tab, name):
        if plt.fignum_exists(self.fig.number):
            self.current_plots.append(self.ax.plot(tab['TIME'][::-1], tab['TEMP'][::-1], alpha=0.7, linewidth=1, label=name))
            self.update()

    def clear(self):
        for i in self.current_plots:
            i = i.pop(0)
            i.remove()
        for i in range(len(self.borders)):
            b = self.borders[i].pop(0)
            b.remove()
            self.signs[i].remove()
        self.current_plots = []
        self.borders = []
        self.signs = []
        self.update()

    def picking(self, event):
        if event.button == 1:  # условие при нажатии на левую кнопку мыши
            if event.inaxes != self.ax:
                return
            self.borders.append(self.ax.plot([event.xdata, event.xdata],
                                             [-1000, 1000],
                                             alpha=1, linewidth=1, color='red'))

            text = PySimpleGUI.popup_get_text('Enter signature:')
            y_pos = self.ax.get_ylim()[0] + abs(self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.01
            x_pos = event.xdata - abs(self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.005
            self.signs.append(self.ax.text(x_pos, y_pos, text, alpha=1, color='red'))
            self.update()

    def button_clear(self, event):
        if event.key == 'c' or event.key == 'с':
            self.clear()

    def button_borders(self, event):
        if event.key == 'b' or event.key == 'и':
            if self.cid_picking == 0:
                self.cid_picking = self.fig.canvas.mpl_connect('button_press_event', self.picking)
            else:
                self.fig.canvas.mpl_disconnect(self.cid_picking)
                self.cid_picking = 0


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
            return 1

    # отрисовка
    with plt.style.context('bmh'):
        fig, ax = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]}, figsize=(14, 8))
        fig.canvas.set_window_title('Thermogram 2D')
        graph = ax[0].imshow(np.array(z).T, cmap=settings[0],
                             interpolation=settings[1],
                             origin='lower', aspect='auto', resample=False,
                             interpolation_stage='rgba',
                             extent=get_extend(x, y))
        ax[0].xaxis_date()
        fig.autofmt_xdate(rotation=0, ha='center')
        ax[0].xaxis.set_major_locator(AutoDateLocator(minticks=2, maxticks=7))
        ax[0].set_ylabel('Measured depth, m')
        ax[0].set_xlabel('Date, time')
        fig.colorbar(graph, ax=ax[0], location='left')
        plt.subplots_adjust(left=0.001, right=0.95, bottom=0.07, top=0.965)
        ax[0].invert_yaxis()

        # ------------------------------- Инициализация графики -------------------------------------
        # Инициализация линии для профилей
        f1d = FigureDepth(fig, ax[1])
        line, = ax[0].plot([], [], '-', c='black', linewidth=0.75)  # пустая линия
        p = Profile(line, x, y, z, f1d)  # элемент класса профиль

        # Инициализация прямоугольника для осреднения
        rect = Rectangle((min(x), min(y)), 0, 0, fill=False, color='black', linewidth=1)
        ax[0].add_patch(rect)
        a = AverageRectangle(rect, x, y, z)

        # Инициализация прямоугольника для экспорта
        rect_export = Rectangle((min(x), min(y)), 0, 0, fill=False,
                                color='white', linewidth=1, linestyle='dashed')
        ax[0].add_patch(rect_export)
        e = ExportRectangle(rect_export, x, y, z)

        # ------------------------------- Инициализация графики -------------------------------------

        # Профиль по Time
        def log_x_button_func(event):
            if event.key == 'x' or event.key == 'ч':
                p.disconnect()
                a.disconnect()
                e.disconnect()

                p.update()
                p.cid_picking = p.line.figure.canvas.mpl_connect('button_press_event', p.picking_x)
                p.cid_motion = p.line.figure.canvas.mpl_connect('motion_notify_event', p.motion_x)

        plt.connect('key_press_event', log_x_button_func)

        # Профиль по Depth
        def log_y_button_func(event):
            if event.key == 'z' or event.key == 'я':
                p.disconnect()
                a.disconnect()
                e.disconnect()

                p.update()
                p.cid_picking = p.line.figure.canvas.mpl_connect('button_press_event', p.picking_y)
                p.cid_motion = p.line.figure.canvas.mpl_connect('motion_notify_event', p.motion_y)

        plt.connect('key_press_event', log_y_button_func)

        # профиль по Time
        def average_y_button_func(event):
            if event.key == '[' or event.key == 'х':
                p.disconnect()
                a.disconnect()
                e.disconnect()

                a.rect.set_height(0)
                a.rect.set_width(0)
                a.update()
                a.cid_picking = a.rect.figure.canvas.mpl_connect('button_press_event', a.picking)
                a.cid_motion = a.rect.figure.canvas.mpl_connect('motion_notify_event', a.motion)
                a.cid_release = a.rect.figure.canvas.mpl_connect('button_release_event', a.release_y)

        plt.connect('key_press_event', average_y_button_func)

        # профиль по Depth
        def average_x_button_func(event):
            if event.key == ']' or event.key == 'ъ':
                p.disconnect()
                a.disconnect()
                e.disconnect()

                a.rect.set_height(0)
                a.rect.set_width(0)
                a.update()
                a.cid_picking = a.rect.figure.canvas.mpl_connect('button_press_event', a.picking)
                a.cid_motion = a.rect.figure.canvas.mpl_connect('motion_notify_event', a.motion)
                a.cid_release = a.rect.figure.canvas.mpl_connect('button_release_event', a.release_x)

        plt.connect('key_press_event', average_x_button_func)

        # Функция экспорта
        def export_button_func(event):
            if event.key == 'e' or event.key == 'у':
                p.disconnect()
                a.disconnect()
                e.disconnect()

                e.rect.set_height(0)
                e.rect.set_width(0)
                e.update()
                e.cid_picking = e.rect.figure.canvas.mpl_connect('button_press_event', e.picking)
                e.cid_motion = e.rect.figure.canvas.mpl_connect('motion_notify_event', e.motion)

        plt.connect('key_press_event', export_button_func)

        # Функция очистки
        def clear_button_func(event):
            if event.key == 'c' or event.key == 'с':
                p.clear()

        plt.connect('key_press_event', clear_button_func)

        plt.show(block=True)


# класс отрисовки профиля в 3D
# самый лучший кусок этого кода
class Profile3D:
    def __init__(self, plotter, basic_mesh):
        self.plotter = plotter
        self.basic_mesh = basic_mesh
        self.points_set = []
        self.line = 0
        self.depth_mode = True

        # key events
        self.plotter.add_key_event('z', self.clicking)
        self.plotter.add_key_event('c', self.clear)

    def clicking(self):
        self.plotter.track_click_position(callback=self.plotting, side='right', double=True)
        self.plotter.track_click_position(callback=self.mode_change, side='left', double=True)
        self.plotter.track_click_position(callback=self.choosing, side='right')

    def clear(self):
        if len(self.points_set) != 0 or self.line != 0:
            self.plotter.remove_actor(self.line)
            self.points_set = []
            self.line = 0

    def choosing(self, position):
        self.clear()

        if len(self.points_set) != 0:
            self.plotter.remove_actor(self.line)

        self.points_set = []

        if self.depth_mode:
            minimum = np.abs(self.basic_mesh.points.T[0] - position[0]).min()
            for i in self.basic_mesh.points:
                if abs(i[0] - position[0]) == minimum:
                    self.points_set.append(i)

        else:
            minimum = np.abs(self.basic_mesh.points.T[1] - position[1]).min()
            for i in self.basic_mesh.points:
                if abs(i[1] - position[1]) == minimum:
                    self.points_set.append(i)

        self.line = self.plotter.add_mesh(pv.MultipleLines(self.points_set), color='black', line_width=5)

    def plotting(self, position):
        self.plotter.untrack_click_position(side='right')
        self.plotter.untrack_click_position(side='left')
        self.points_set = np.array(self.points_set)

        if self.depth_mode:
            data = {'DEPTH': self.points_set.T[1], 'TEMP': self.points_set.T[2]}
            self.show(data, 'Depth, m', self.plotter)

        else:
            data = {'DEPTH': self.points_set.T[0], 'TEMP': self.points_set.T[2]}
            self.show(data, 'Time, min', self.plotter)

        self.points_set = []

    def mode_change(self, position):
        if self.depth_mode:
            self.depth_mode = False
            self.choosing(self.points_set[int(len(self.points_set) // 2)])
        else:
            self.depth_mode = True
            self.choosing(self.points_set[int(len(self.points_set) // 2)])

    @staticmethod
    def show(tab: dict, x_axes: str, plotter):
        chart = pv.Chart2D(x_label=x_axes, y_label='Temperature, °C')
        chart.line(x=tab['DEPTH'], y=tab['TEMP'], width=2)

        chart.x_axis.label_size = 20
        chart.y_axis.label_size = 20
        chart.x_axis.tick_label_size = 16
        chart.y_axis.tick_label_size = 16

        pv.global_theme.title = 'Line'
        chart.show()
        plotter.add_camera_orientation_widget()


# функция отрисовки матрицы в 3D
def make_figure_3d(data, settings):
    # задание осей и матрицы
    x = []
    y = data[0][1]['DEPTH']
    z = []

    for i in data:
        x.append(i[0].timestamp())
        z.append(list(i[1]['TEMP']))
    x = (np.array(x) - min(x)) / 60

    for i in z:
        if len(z[0]) != len(i):
            return 1

    points = []
    for i in range(len(z)):
        for j in range(len(z[i])):
            points.append([x[i], y[j], z[i][j]])

    cloud = pv.PolyData(points)
    surf = cloud.delaunay_2d()
    surf['Temperature'] = np.reshape(z, len(z) * len(z[0]))

    pv.global_theme.cmap = settings[0]
    pv.global_theme.font.color = 'black'

    surf.scale([1 / max(x), 1 / max(y), 0.5 / np.matrix(z).max()], inplace=True)
    p = pv.Plotter(notebook=False)

    p.set_background('white')
    p.add_mesh(surf, show_scalar_bar=False)

    Profile3D(p, surf)

    p.add_scalar_bar('Temperature, C°', vertical=True, font_family='courier',
                     title_font_size=14, label_font_size=14)

    p.add_camera_orientation_widget()
    p.show(title='Thermogram 3D')
