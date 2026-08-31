import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set the apperance mode of the application
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class live_counter_gui(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Set the title and size of the window
        self.title("COUNTER LIVE GRAPH")
        self.geometry("900x600")

        # Define the layout of the window. 
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create a frame for the configuration options on the left side of the window
        self.config_frame = ctk.CTkFrame(self, width=180)
        self.config_frame.grid(row=0, column=0, rowspan=2, padx=(10, 0), pady=10, sticky="nsew")
        self.config_frame.pack_propagate(False)

        # Create a frame for the buttons on the right side
        self.button_frame = ctk.CTkFrame(self, width=420, height=55)
        self.button_frame.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="nsew")

        # Create a frame for the graph on the right side
        self.graph_frame = ctk.CTkFrame(self, width=420, height=545)
        self.graph_frame.grid(row=1, column=1, padx=10, pady=(10,10), sticky="nsew")

        self.create_config_widgets()
        self.create_button_widgets()
        self.create_graph()

    def create_config_widgets(self):

        config_label_moku = ctk.CTkLabel(self.config_frame, text="MOKU IP", font=ctk.CTkFont(size=16, weight="bold"))
        config_label_moku.pack(pady=(20, 10), padx=20)

        self.ip_entry = ctk.CTkEntry(self.config_frame, textvariable=ctk.StringVar(), placeholder_text="Enter Moku IP")
        self.ip_entry.pack(pady=(0, 20), padx=20)

        record_label = ctk.CTkLabel(self.config_frame, text="Record Time (s)", font=ctk.CTkFont(size=16, weight="bold"))
        record_label.pack(pady=(0, 10), padx=20)

        self.record_entry = ctk.CTkEntry(self.config_frame, textvariable=ctk.StringVar(), placeholder_text="Enter Record Time")
        self.record_entry.pack(pady=(0, 20), padx=20)

        input_label = ctk.CTkLabel(self.config_frame, text="Input Channel", font=ctk.CTkFont(size=16, weight="bold"))
        input_label.pack(pady=(0, 10), padx=20)

        self.input_select = ctk.IntVar(value=0)

        # Frame specifically for the radio buttons
        radio_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        radio_frame.pack(padx=(10, 0), pady=(0, 20))

        self.input1_radio = ctk.CTkRadioButton(radio_frame, text="IN 1", variable=self.input_select, value=1)
        self.input2_radio = ctk.CTkRadioButton(radio_frame, text="IN 2", variable=self.input_select, value=2)
        self.input3_radio = ctk.CTkRadioButton(radio_frame, text="IN 3", variable=self.input_select, value=3)
        self.input4_radio = ctk.CTkRadioButton(radio_frame, text="IN 4", variable=self.input_select, value=4)

        # Two columns
        self.input1_radio.grid(row=0, column=0, pady=5)
        self.input2_radio.grid(row=0, column=1, padx=(1,0), pady=5)
        self.input3_radio.grid(row=1, column=0, pady=5)
        self.input4_radio.grid(row=1, column=1, padx=(1,0), pady=5)

        self.checkbox_time_trend = ctk.CTkCheckBox(self.config_frame,
                                                    text=f"Continuous \n Time Trend",
                                                    font=ctk.CTkFont(size=12, weight="bold"))
        self.checkbox_time_trend.pack(pady=(0, 20), padx=20)

        self.button_save = ctk.CTkButton(self.config_frame, text="Save", font=ctk.CTkFont(size=12, weight="bold"))
        self.button_save.pack(pady=(0, 20), padx=20, side="bottom")

    def create_button_widgets(self):
        buttons_symbols = ["▶", "⏸", "↶", "↓"]
        button_width = 30
        button_height = 30

        for i, symbol in enumerate(buttons_symbols):
            button = ctk.CTkButton(self.button_frame, text=symbol, width=button_width, height=button_height,
                                   font=ctk.CTkFont(size=20, weight="bold"))
            button.grid(row=0, column=i, padx=(10 if i == 0 else 5, 10), pady=5)

    def create_graph(self):
        # Create a matplotlib figure and axis
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.ax.set_xlabel("Elapsed time (s)", labelpad=10)
        self.ax.set_ylabel("Count-related value", labelpad=20)
        self.ax.grid(True)

        # Create a FigureCanvasTkAgg object to embed the matplotlib figure in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)



root = live_counter_gui()
root.mainloop()
