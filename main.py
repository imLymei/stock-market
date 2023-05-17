import settings
import yfinance as yf  # uses pandas
import customtkinter as ctk
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

try:
    from ctypes import windll, byref, sizeof, c_int
except:
    pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=settings.BG_COLOR)
        self.geometry('900x800')
        self.title('')
        self.iconbitmap('./empty.ico')
        self.set_title_bar_color()

        self.input_string = ctk.StringVar(value='AAPL')
        self.time_string = ctk.StringVar(value=settings.TIME_OPTIONS[0])

        self.max_data = None
        self.year = None
        self.six_months = None
        self.one_month = None
        self.one_weak = None
        self.has_data = False

        InputPanel(self, self.input_string, self.time_string)
        self.graph_panel = None

        self.time_string.trace('w', self.create_graph)
        self.bind('<Return>', self.input_handler)

        self.mainloop()

    def input_handler(self, event=None):
        ticker = yf.Ticker(self.input_string.get())
        start = '1000-01-01'
        end = datetime.today()

        self.max_data = ticker.history(start=start, end=end, period='1d')
        self.year = self.max_data.iloc[-260:]  # 365 days in a year ~> 260 work days in a year
        self.six_months = self.max_data.iloc[-130:]
        self.one_month = self.max_data.iloc[-22:]
        self.one_weak = self.max_data.iloc[-5:]

        self.has_data = True

        self.create_graph()

    def create_graph(self, *args):
        if not self.has_data:
            try:
                self.input_handler()
            except:
                pass

        if self.graph_panel:
            self.graph_panel.pack_forget()

        data = None

        match self.time_string.get():
            case 'Max':
                data = self.max_data
            case '1 Year':
                data = self.year
            case '6 Months':
                data = self.six_months
            case 'Month':
                data = self.one_month
            case 'Week':
                data = self.one_weak

        self.graph_panel = GraphPanel(self, data)

    def set_title_bar_color(self):
        try:
            HWND = windll.user32.GetParent(self.winfo_id())
            windll.dwmapi.DwmSetWindowAttribute(HWND, 35, byref(c_int(settings.TITLE_HEX_COLOR)), sizeof(c_int))
        except:
            pass


class InputPanel(ctk.CTkFrame):
    def __init__(self, master, input_string, time_string):
        super().__init__(master=master, fg_color=settings.INPUT_BG_COLOR, corner_radius=0)

        ctk.CTkEntry(self, fg_color=settings.BG_COLOR, border_color=settings.TEXT_COLOR, border_width=1,
                     textvariable=input_string).pack(side='left', padx=10, pady=10)

        self.buttons = [TextButton(self, text, time_string) for text in settings.TIME_OPTIONS]

        time_string.trace('w', self.update_buttons)

        self.pack(fill='both', side='bottom')

    def update_buttons(self, *args):
        for button in self.buttons:
            button.check_time_string()


class TextButton(ctk.CTkLabel):
    def __init__(self, master, text, time_string):
        super().__init__(master=master, text=text, text_color=settings.TEXT_COLOR)

        self.time_string = time_string
        self.text = text

        self.check_time_string()

        self.bind('<Button>', self.update_time_string)

        self.pack(side='right', ipadx=10, ipady=10)

    def check_time_string(self):
        color = settings.TEXT_COLOR if self.text != self.time_string.get() else settings.HIGHLIGHT_COLOR
        self.configure(text_color=color)

    def update_time_string(self, _):
        self.time_string.set(self.text)


class GraphPanel(ctk.CTkFrame):
    def __init__(self, master, data):
        super().__init__(master=master, fg_color=settings.BG_COLOR)

        figure = plt.Figure()
        figure.subplots_adjust(left=0, top=1, right=0.96, bottom=0)
        figure.patch.set_facecolor(settings.BG_COLOR)

        ax = figure.add_subplot(111)
        ax.set_facecolor(settings.BG_COLOR)

        for side in ['top', 'left', 'bottom', 'right']:
            ax.spines[side].set_color(settings.BG_COLOR)

        line = ax.plot(data['Close'])[0]
        line.set_color(settings.HIGHLIGHT_COLOR)

        ax.tick_params(axis='x', direction='in', pad=-14, colors=settings.TICK_COLOR)
        ax.tick_params(axis='y', direction='in', pad=0, colors=settings.HIGHLIGHT_COLOR)
        ax.yaxis.tick_right()

        figure_widget = FigureCanvasTkAgg(master=self, figure=figure)
        figure_widget.get_tk_widget().pack(fill='both', expand=True)

        self.pack(expand=True, fill='both')


if __name__ == '__main__':
    App()
