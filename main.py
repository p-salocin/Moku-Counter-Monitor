import customtkinter as ctk
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox
from moku.instruments import TimeFrequencyAnalyzer

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

        # Global variables to hold the Moku connection and data
        self.moku_ip = None
        self.record_time = None
        self.input_channel = None
        self.continuous_time_trend = None
        self.tfa = None
        self.running_graph = True

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

        config_label_moku = ctk.CTkLabel(self.config_frame, text="MOKU IPv6", font=ctk.CTkFont(size=16, weight="bold"))
        config_label_moku.pack(pady=(20, 10), padx=20)

        self.ip_entry = ctk.CTkEntry(self.config_frame, textvariable=ctk.StringVar(), placeholder_text="Enter Moku IP")
        self.ip_entry.pack(pady=(0, 20), padx=20)
        self.ip_entry.set("fe80::7269:79ff:feb0:dce") # Default IP for the Moku Pro in the lab

        record_label = ctk.CTkLabel(self.config_frame, text="Record Time (s)", font=ctk.CTkFont(size=16, weight="bold"))
        record_label.pack(pady=(0, 10), padx=20)

        self.record_entry = ctk.CTkEntry(self.config_frame, textvariable=ctk.StringVar(), placeholder_text="Enter Record Time")
        self.record_entry.pack(pady=(0, 20), padx=20)
        self.record_entry.set("60") # Default record time

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

        self.input1_radio.set(True) # Set as default channel

        self.checkbox_time_trend = ctk.CTkCheckBox(self.config_frame,
                                                    text=f"Continuous \n Time Trend",
                                                    font=ctk.CTkFont(size=12, weight="bold"))
        self.checkbox_time_trend.pack(pady=(0, 20), padx=20)

        self.button_connect = ctk.CTkButton(self.config_frame, text="Connect", font=ctk.CTkFont(size=12, weight="bold"), command=self.get_config_info)
        self.button_disconnect = ctk.CTkButton(self.config_frame, text="Disconnect", font=ctk.CTkFont(size=12, weight="bold"), command=self.disconnect_from_moku)

        self.button_disconnect.pack(pady=(0, 20), padx=20, side="bottom")
        self.button_connect.pack(pady=(0, 20), padx=20, side="bottom")


    def create_button_widgets(self):

        button_size = 30
        button_radius = 30

        # Create the buttons 
        self.play_button = ctk.CTkButton(self.button_frame, text="▶", height=button_size, width=button_size, font=ctk.CTkFont(size=20, weight="bold"), corner_radius=button_radius, command=self.start_live_graph)

        self.pause_button = ctk.CTkButton(self.button_frame, text="⏸", height=button_size, width=button_size, font=ctk.CTkFont(size=20, weight="bold"), corner_radius=button_radius, command=self.stop_live_graph)

        self.rewind_button = ctk.CTkButton(self.button_frame, text="↶", height=button_size, width=button_size, font=ctk.CTkFont(size=20, weight="bold"), corner_radius=button_radius)

        self.download_button = ctk.CTkButton(self.button_frame, text="↓", height=button_size, width=button_size, font=ctk.CTkFont(size=20, weight="bold"), corner_radius=button_radius)

        # Place the buttons on the grid

        self.play_button.grid(row=0, column=0, padx=(10, 10), pady=(5, 5))
        self.pause_button.grid(row=0, column=1, padx=(5, 10), pady=(5, 5))
        self.rewind_button.grid(row=0, column=2, padx=(5, 10), pady=(5, 5))
        self.download_button.grid(row=0, column=3, padx=(5, 10), pady=(5, 5))

    def create_graph(self):
        # Create a matplotlib figure and axis
        plt.style.use("dark_background")
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.set_xlabel("Elapsed time (s)", labelpad=10)
        self.ax.set_ylabel("Count-related value", labelpad=20)
        self.ax.grid(True, color='gray', linewidth=0.5, alpha=0.7)

        # Create a FigureCanvasTkAgg object to embed the matplotlib figure in the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def get_config_info(self):
        # Store the configuration values
        self.moku_ip = self.ip_entry.get()
        self.record_time = self.record_entry.get()
        self.input_channel = self.input_select.get()
        self.continuous_time_trend = self.checkbox_time_trend.get()

        self.connect_to_moku()

    def time_frequency_analyzer_config(self):

        input_names = ["Input1", "Input2", "Input3", "Input4"]

        self.tfa.set_event_detector(id=1, source=input_names[self.input_channel - 1], threshold=0, edge="Rising")
        self.tfa.set_interpolation(mode="linear")
        self.tfa.set_acquisition_mode(mode="Windowed", window_length=100e-3)
        self.tfa.set_interval_policy(multiple_start_events="Use first", incomplete_intervals="Close")
        self.tfa.set_interval_analyzer(id=1, start_event_id=1, stop_event_id=1)

    def connect_to_moku(self):
        if self.moku_ip:
            try:
                self.tfa = TimeFrequencyAnalyzer(f"[{self.moku_ip}]", force_connect=True)
                self.time_frequency_analyzer_config()
                messagebox.showinfo("Connection Successful", f"Successfully connected to Moku at {self.moku_ip}")
            except Exception as e:
                messagebox.showerror("Connection Failed", f"Failed to connect to Moku at {self.moku_ip}. {e}. Please verify your connection.")
        else:
            messagebox.showwarning("Connection Warning", "Moku IP is not set. Please enter a valid the IPv6 address.")

    def disconnect_from_moku(self):
        if self.tfa:
            try:
                self.tfa.relinquish_ownership()
                self.tfa = None
                messagebox.showinfo("Disconnection Successful", "Successfully disconnected from Moku.")
            except Exception as e:
                messagebox.showerror("Disconnection Failed", f"Failed to disconnect from Moku. {e}.")
        else:
            messagebox.showwarning("Disconnection Warning", "Moku is not connected. Please connect to Moku first.")

    def update_live_graph(self):

        if not self.running_graph:
            return  # If the graph is not running, exit the function

        data = self.tfa.get_data()
        stats = data['interval1']['statistics']
        y = stats.get('count', 0)

        self.times.append(time.time() - self.t_start)
        self.values.append(y)

        self.line.set_xdata(self.times)
        self.line.set_ydata(self.values)

        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw_idle()

        # Schedule the next update
        self.after(50, self.update_live_graph)
        

    def start_live_graph(self):
        if not self.tfa:
            messagebox.showwarning("Connection Warning", "Moku is not connected. Please connect to Moku first.")
            return
        if self.running_graph:
            pass  # Already running, do nothing

        self.running_graph = True
        self.times = []
        self.values = []
        self.t_start = time.time()

        self.update_live_graph()  # Start the update loop

    def stop_live_graph(self):
        self.running_graph = False  # Stop the update loop


root = live_counter_gui()
root.mainloop()
