import PySimpleGUI as sg
from functions import load_las
import matplotlib.pyplot as plt

# Нужно понять как правильно добавлять и удалять границы
# понять как расставлять лимиты (их можно обновлять в апдейте)


class Figure1D:
    def __init__(self):

        # figure settings
        plt.style.use('bmh')
        self.fig, self.ax = plt.subplots(figsize=(5, 8))
        self.fig.canvas.set_window_title('Temperature log')

        # axes settings
        self.ax.invert_yaxis()
        self.ax.legend()
        self.ax.set_xlabel('Temperature, C°')
        self.ax.set_ylabel('Depth, m')
        self.fig.subplots_adjust(left=0.14, right=0.95, bottom=0.07, top=0.965)

        # list of active plots
        self.current_plots = []

        # events
        self.fig.canvas.mpl_connect('key_press_event', self.button_clear)
        self.fig.canvas.mpl_connect('key_press_event', self.button_add)
        self.fig.canvas.mpl_connect('key_press_event', self.button_borders)

        self.cid_picking = 0

    def update(self):
        self.ax.get_legend().remove()
        self.ax.legend()
        self.fig.canvas.draw()

    def draw_line(self, tab, name):
        self.current_plots.append(self.ax.plot(tab['TEMP'], tab['DEPTH'],
                                               alpha=0.7, linewidth=1, label=name))
        self.update()

    def clear(self):
        for i in self.current_plots:
            i = i.pop(0)
            i.remove()
        self.current_plots = []
        self.update()

    def picking(self, event):
        return

    def button_clear(self, event):
        if event.key == 'c' or event.key == 'с':
            self.clear()

    def button_add(self, event):
        if event.key == 'a' or event.key == 'ф':
            base_line_path = sg.popup_get_file('Choose base line .las', no_window=True)

            if len(base_line_path) != 0:
                graph_label = sg.popup_get_text('Enter line name:')
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


fig = Figure1D()
plt.show()
