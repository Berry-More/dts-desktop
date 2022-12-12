import pandas as pd
import functions as func
import PySimpleGUI as sg
import matplotlib.pyplot as plt


def main():
    # Задание объектов интерфейса

    im = 'image.ico'

    sg.theme('SystemDefaultForReal')  # Default1
    sg.set_options(font='Cambria 12')
    figure_settings = [func.new_color_map, 'spline36']
    color_maps = ['new', 'coolwarm', 'bwr', 'plasma', 'jet', 'rainbow']
    interpolation = ['none', 'bilinear', 'bicubic', 'spline36']

    left_col = [[sg.Text('Loaded files')],
                [sg.Listbox(values=[], enable_events=True, size=(50, 25), key='-FILE_BOX-')],
                [sg.Text('Program log')],
                [sg.Multiline(size=(56, 5), key='-OUT-', font='Courier 10')]]

    right_col = [[sg.Text('Visualisation:'),
                  sg.Button('1D'),
                  sg.Button('2D'),
                  sg.Button('3D')],
                 [sg.Table(values=[[]], headings=['Depth, m', 'Temp, C'], auto_size_columns=False,
                           display_row_numbers=True, header_border_width=2,
                           border_width=2, selected_row_colors=('white', '#0079d8'),
                           size=(100, 30), justification='center', col_widths=[25, 20], key='-TAB-')]]

    menu_object = sg.Menu(func.make_menu(color_maps, interpolation, figure_settings))
    layout = [[menu_object],
              [sg.Column(left_col, element_justification='c'),
               sg.VSeparator(),
               sg.Column(right_col, element_justification='c')]]

    #
    # Создание рабочего окна и цикла

    window = sg.Window("DTSview", layout, icon=im)

    data = []
    dict_data = []
    tab = []
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            plt.close('all')
            break

        if event == 'Open':
            filenames = sg.popup_get_file('Load data', multiple_files=True,
                                          no_window=True, icon=im)
            if len(filenames) < 1:
                func.log_print(window, 'Data not exists!', 'red')
            else:
                func.log_print(window, 'Loading data...', 'black')
                data = func.load_las(filenames)
                dict_data = {data[i][0]: data[i] for i in range(len(data))}
                window['-FILE_BOX-'].update(list(dict_data.keys()))
                func.log_print(window, 'Files loaded!', 'green')

        if event in color_maps:
            if event == 'new':
                figure_settings[0] = func.new_color_map
            else:
                figure_settings[0] = str(event)
            menu_object.update(menu_definition=func.make_menu(color_maps, interpolation, figure_settings))
            func.log_print(window, 'Color map updated: ' + event, 'black')

        if event in interpolation:
            figure_settings[1] = str(event)
            menu_object.update(menu_definition=func.make_menu(color_maps, interpolation, figure_settings))
            func.log_print(window, 'Interpolation updated: ' + event, 'black')

        if event == '-FILE_BOX-':
            if len(values['-FILE_BOX-']) != 0:
                las_file = dict_data[values['-FILE_BOX-'][0]][1]
                diction = {}
                for i in las_file.curves:
                    diction[i.mnemonic] = i.data
                tab = pd.DataFrame(diction)
                values = tab.values.tolist()
                window['-TAB-'].update(values=values)

        if event == '1D':
            if len(tab) == 0:
                func.log_print(window, 'Data not exists!', 'red')
            else:
                window.Hide()
                f1d = func.FigureDepth()
                f1d.draw_line(tab, values['-FILE_BOX-'][0])
                plt.show(block=True)
                window.UnHide()

        if event == '2D':
            if len(data) == 0:
                func.log_print(window, 'Data not exists!', 'red')
            else:
                window.Hide()
                fig2d = func.make_figure_2d(data, figure_settings)
                if fig2d == 1:
                    func.log_print(window, 'Arrays lengths do not match!', 'red')
                window.UnHide()

        if event == '3D':
            if len(data) == 0:
                func.log_print(window, 'Data not exists!', 'red')
            else:
                window.Hide()
                fig3d = func.make_figure_3d(data, figure_settings)
                if fig3d == 1:
                    func.log_print(window, 'Arrays lengths do not match!', 'red')
                window.UnHide()


if __name__ == '__main__':
    main()
