import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import numpy as np
import pyvisa


# ============================================================
# BK PRECISION 895
# ============================================================

RESOURCE = "USB0::0x0471::0x2827::480K23104::INSTR"


class BK895App:

    def __init__(self, root):

        self.root = root
        self.root.title("BK Precision 895 - LCR Characterization")
        self.root.geometry("720x700")
        self.root.resizable(False, False)

        self.rm = None
        self.instrument = None

        self.stop_requested = False
        self.measuring = False

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.start_freq = tk.StringVar(value="20")
        self.stop_freq = tk.StringVar(value="1M")
        self.points = tk.StringVar(value="21")

        self.scale = tk.StringVar(value="Logarithmic")

        self.voltage = tk.StringVar(value="0.005")
        self.cycles = tk.StringVar(value="2")

        # 15 s comme dans le script original
        self.delay = tk.StringVar(value="15")

        self.sample = tk.StringVar(value="sample")

        self.folder = tk.StringVar(
            value=os.path.abspath(".")
        )

        self.cprp = tk.BooleanVar(value=True)
        self.csrs = tk.BooleanVar(value=True)

        self.status = tk.StringVar(
            value="Disconnected"
        )

        self.progress_value = tk.DoubleVar(value=0)

        self.create_interface()


    # ========================================================
    # INTERFACE
    # ========================================================

    def create_interface(self):

        main = ttk.Frame(
            self.root,
            padding=15
        )

        main.pack(
            fill="both",
            expand=True
        )


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        ttk.Label(
            main,
            text="BK Precision 895",
            font=("Segoe UI", 18, "bold")
        ).pack()

        ttk.Label(
            main,
            text="LCR Characterization"
        ).pack(
            pady=(0, 15)
        )


        # ----------------------------------------------------
        # CONNECTION
        # ----------------------------------------------------

        connection = ttk.LabelFrame(
            main,
            text="Instrument",
            padding=10
        )

        connection.pack(
            fill="x",
            pady=5
        )


        ttk.Label(
            connection,
            text="VISA Resource:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )


        ttk.Entry(
            connection,
            width=48,
            state="readonly"
        ).grid(
            row=0,
            column=1,
            padx=10
        )


        self.connect_button = ttk.Button(
            connection,
            text="CONNECT",
            command=self.connect
        )

        self.connect_button.grid(
            row=0,
            column=2
        )


        self.idn_label = ttk.Label(
            connection,
            text="Not connected"
        )

        self.idn_label.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="w",
            pady=8
        )


        # ----------------------------------------------------
        # FREQUENCY
        # ----------------------------------------------------

        settings = ttk.LabelFrame(
            main,
            text="Frequency settings",
            padding=10
        )

        settings.pack(
            fill="x",
            pady=5
        )


        ttk.Label(
            settings,
            text="Start frequency:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )


        ttk.Entry(
            settings,
            textvariable=self.start_freq,
            width=15
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=10
        )


        ttk.Label(
            settings,
            text="Hz"
        ).grid(
            row=0,
            column=2
        )


        ttk.Label(
            settings,
            text="Stop frequency:"
        ).grid(
            row=0,
            column=3,
            sticky="w",
            padx=(30, 0)
        )


        ttk.Entry(
            settings,
            textvariable=self.stop_freq,
            width=15
        ).grid(
            row=0,
            column=4,
            sticky="w",
            padx=10
        )


        ttk.Label(
            settings,
            text="Hz"
        ).grid(
            row=0,
            column=5
        )


        ttk.Label(
            settings,
            text="Number of points:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8
        )


        ttk.Entry(
            settings,
            textvariable=self.points,
            width=15
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=10
        )


        ttk.Label(
            settings,
            text="Scale:"
        ).grid(
            row=1,
            column=3,
            sticky="w",
            padx=(30, 0)
        )


        ttk.Combobox(
            settings,
            textvariable=self.scale,
            values=[
                "Logarithmic",
                "Linear"
            ],
            state="readonly",
            width=13
        ).grid(
            row=1,
            column=4,
            padx=10
        )


        # ----------------------------------------------------
        # MEASUREMENT
        # ----------------------------------------------------

        measurement = ttk.LabelFrame(
            main,
            text="Measurement",
            padding=10
        )

        measurement.pack(
            fill="x",
            pady=5
        )


        ttk.Label(
            measurement,
            text="Voltage:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )


        ttk.Entry(
            measurement,
            textvariable=self.voltage,
            width=15
        ).grid(
            row=0,
            column=1,
            padx=10
        )


        ttk.Label(
            measurement,
            text="V"
        ).grid(
            row=0,
            column=2
        )


        ttk.Label(
            measurement,
            text="Cycles:"
        ).grid(
            row=0,
            column=3,
            padx=(30, 0)
        )


        ttk.Entry(
            measurement,
            textvariable=self.cycles,
            width=15
        ).grid(
            row=0,
            column=4,
            padx=10
        )


        ttk.Label(
            measurement,
            text="Wait:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8
        )


        ttk.Entry(
            measurement,
            textvariable=self.delay,
            width=15
        ).grid(
            row=1,
            column=1,
            padx=10
        )


        ttk.Label(
            measurement,
            text="seconds / frequency"
        ).grid(
            row=1,
            column=2,
            columnspan=3,
            sticky="w"
        )


        # ----------------------------------------------------
        # MODES
        # ----------------------------------------------------

        modes = ttk.LabelFrame(
            main,
            text="Measurement modes",
            padding=10
        )

        modes.pack(
            fill="x",
            pady=5
        )


        ttk.Checkbutton(
            modes,
            text="Parallel CP / RP",
            variable=self.cprp
        ).pack(
            side="left",
            padx=20
        )


        ttk.Checkbutton(
            modes,
            text="Series CS / RS",
            variable=self.csrs
        ).pack(
            side="left",
            padx=20
        )


        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        output = ttk.LabelFrame(
            main,
            text="Output",
            padding=10
        )

        output.pack(
            fill="x",
            pady=5
        )


        ttk.Label(
            output,
            text="Sample name:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )


        ttk.Entry(
            output,
            textvariable=self.sample,
            width=30
        ).grid(
            row=0,
            column=1,
            padx=10
        )


        ttk.Label(
            output,
            text="Folder:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=8
        )


        ttk.Entry(
            output,
            textvariable=self.folder,
            width=50
        ).grid(
            row=1,
            column=1,
            padx=10
        )


        ttk.Button(
            output,
            text="Browse",
            command=self.choose_folder
        ).grid(
            row=1,
            column=2
        )


        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons = ttk.Frame(main)

        buttons.pack(
            pady=12
        )


        self.start_button = ttk.Button(
            buttons,
            text="START MEASUREMENT",
            command=self.start
        )

        self.start_button.pack(
            side="left",
            padx=5
        )


        self.stop_button = ttk.Button(
            buttons,
            text="STOP",
            command=self.stop,
            state="disabled"
        )

        self.stop_button.pack(
            side="left",
            padx=5
        )


        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        ttk.Label(
            main,
            textvariable=self.status
        ).pack(
            anchor="w"
        )


        ttk.Progressbar(
            main,
            variable=self.progress_value,
            maximum=100
        ).pack(
            fill="x",
            pady=5
        )


        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        log_frame = ttk.LabelFrame(
            main,
            text="Log",
            padding=5
        )

        log_frame.pack(
            fill="both",
            expand=True
        )


        self.log = tk.Text(
            log_frame,
            height=10,
            state="disabled"
        )

        self.log.pack(
            fill="both",
            expand=True
        )


    # ========================================================
    # LOG
    # ========================================================

    def write_log(self, text):

        def update():

            self.log.config(
                state="normal"
            )

            self.log.insert(
                "end",
                text + "\n"
            )

            self.log.see("end")

            self.log.config(
                state="disabled"
            )

        self.root.after(
            0,
            update
        )


    # ========================================================
    # CONNECT
    # ========================================================

    def connect(self):

        try:

            self.rm = pyvisa.ResourceManager()

            resources = self.rm.list_resources()

            self.write_log(
                "VISA instruments found:"
            )

            for r in resources:

                self.write_log(
                    "  " + r
                )


            self.instrument = self.rm.open_resource(
                RESOURCE
            )


            self.instrument.timeout = 30000

            self.instrument.write_termination = "\n"
            self.instrument.read_termination = "\n"


            idn = self.instrument.query(
                "*IDN?"
            ).strip()


            self.idn_label.config(
                text=idn
            )

            self.status.set(
                "Connected"
            )


            self.write_log(
                "Connected:"
            )

            self.write_log(
                idn
            )


            self.connect_button.config(
                text="RECONNECT"
            )


        except Exception as e:

            messagebox.showerror(
                "Connection error",
                str(e)
            )


    # ========================================================
    # FOLDER
    # ========================================================

    def choose_folder(self):

        folder = filedialog.askdirectory()

        if folder:

            self.folder.set(
                folder
            )


    # ========================================================
    # FREQUENCY PARSER
    # ========================================================

    def parse_frequency(self, value):

        value = (
            value
            .strip()
            .lower()
            .replace(" ", "")
        )


        if value.endswith("mhz"):

            return float(
                value[:-3]
            ) * 1e6


        if value.endswith("khz"):

            return float(
                value[:-3]
            ) * 1e3


        if value.endswith("hz"):

            return float(
                value[:-2]
            )


        if value.endswith("m"):

            return float(
                value[:-1]
            ) * 1e6


        if value.endswith("k"):

            return float(
                value[:-1]
            ) * 1e3


        return float(value)


    # ========================================================
    # FREQUENCIES
    # ========================================================

    def generate_frequencies(self):

        start = self.parse_frequency(
            self.start_freq.get()
        )

        stop = self.parse_frequency(
            self.stop_freq.get()
        )

        points = int(
            self.points.get()
        )


        if start <= 0:

            raise ValueError(
                "Start frequency must be > 0"
            )


        if stop <= start:

            raise ValueError(
                "Stop frequency must be greater than start frequency"
            )


        if points < 2:

            raise ValueError(
                "Number of points must be at least 2"
            )


        if self.scale.get() == "Logarithmic":

            return np.geomspace(
                start,
                stop,
                points
            ).tolist()

        else:

            return np.linspace(
                start,
                stop,
                points
            ).tolist()


    # ========================================================
    # START
    # ========================================================

    def start(self):

        if self.instrument is None:

            messagebox.showwarning(
                "Not connected",
                "Connect the BK Precision 895 first."
            )

            return


        try:

            frequencies = self.generate_frequencies()

            voltage = float(
                self.voltage.get()
            )

            cycles = int(
                self.cycles.get()
            )

            delay = float(
                self.delay.get()
            )

            sample = self.sample.get().strip()


            if not self.cprp.get() and not self.csrs.get():

                raise ValueError(
                    "Select at least one measurement mode."
                )


            if sample == "":

                raise ValueError(
                    "Enter a sample name."
                )


        except Exception as e:

            messagebox.showerror(
                "Invalid settings",
                str(e)
            )

            return


        self.stop_requested = False
        self.measuring = True


        self.start_button.config(
            state="disabled"
        )

        self.stop_button.config(
            state="normal"
        )


        thread = threading.Thread(
            target=self.measurement,
            args=(
                frequencies,
                voltage,
                cycles,
                delay,
                sample
            ),
            daemon=True
        )


        thread.start()


    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        self.stop_requested = True

        self.status.set(
            "Stopping..."
        )

        self.write_log(
            "STOP requested."
        )


    # ========================================================
    # WAIT
    # ========================================================

    def wait(self, seconds):

        end = time.time() + seconds


        while time.time() < end:

            if self.stop_requested:

                return False

            time.sleep(
                0.1
            )


        return True


    # ========================================================
    # MEASUREMENT
    # ========================================================

    def measurement(
        self,
        frequencies,
        voltage,
        cycles,
        delay,
        sample
    ):

        try:

            folder = os.path.join(
                self.folder.get(),
                sample
            )


            os.makedirs(
                folder,
                exist_ok=True
            )


            modes = 0

            if self.cprp.get():

                modes += 1

            if self.csrs.get():

                modes += 1


            total = (
                len(frequencies)
                * cycles
                * modes
            )


            completed = 0


            # ------------------------------------------------
            # GENERAL SETTINGS
            # ------------------------------------------------

            self.instrument.write(
                "*CLS"
            )

            self.instrument.write(
                "VOLTage %g" % voltage
            )

            self.instrument.write(
                "APER FAST,1"
            )


            self.write_log("")
            self.write_log(
                "===== START ====="
            )

            self.write_log(
                "Sample: " + sample
            )

            self.write_log(
                "Output: " + folder
            )


            # =================================================
            # CPRP
            # =================================================

            if self.cprp.get():

                self.instrument.write(
                    "FUNC:IMP CPRP"
                )


                self.write_log("")
                self.write_log(
                    "===== CP / RP ====="
                )


                for cycle in range(cycles):

                    if self.stop_requested:

                        break


                    filename = os.path.join(
                        folder,
                        "CP_RP_%s_%d.txt"
                        % (
                            sample,
                            cycle
                        )
                    )


                    with open(
                        filename,
                        "w",
                        encoding="utf-8"
                    ) as file:


                        file.write(
                            "# Frequency_Hz Capacitance Resistance\n"
                        )


                        for freq in frequencies:

                            if self.stop_requested:

                                break


                            self.instrument.write(
                                "FREQ %e" % freq
                            )


                            if not self.wait(delay):

                                break


                            response = self.instrument.query(
                                "FETC?"
                            ).strip()


                            values = response.split(",")


                            if len(values) < 2:

                                raise RuntimeError(
                                    "Unexpected response: "
                                    + response
                                )


                            C = values[0].strip()
                            R = values[1].strip()


                            file.write(
                                "%e %s %s\n"
                                % (
                                    freq,
                                    C,
                                    R
                                )
                            )


                            file.flush()


                            completed += 1


                            percent = (
                                completed
                                / total
                                * 100
                            )


                            self.root.after(
                                0,
                                lambda p=percent:
                                self.progress_value.set(p)
                            )


                            self.root.after(
                                0,
                                lambda f=freq:
                                self.status.set(
                                    "CP/RP - %.0f Hz"
                                    % f
                                )
                            )


                            self.write_log(
                                "CP/RP | %.0f Hz | %s"
                                % (
                                    freq,
                                    response
                                )
                            )


                    self.write_log(
                        "Saved: " + filename
                    )


            # =================================================
            # CSRS
            # =================================================

            if (
                self.csrs.get()
                and not self.stop_requested
            ):

                self.instrument.write(
                    "*CLS"
                )

                self.instrument.write(
                    "FUNC:IMP CSRS"
                )


                self.write_log("")
                self.write_log(
                    "===== CS / RS ====="
                )


                for cycle in range(cycles):

                    if self.stop_requested:

                        break


                    filename = os.path.join(
                        folder,
                        "CS_RS_%s_%d.txt"
                        % (
                            sample,
                            cycle
                        )
                    )


                    with open(
                        filename,
                        "w",
                        encoding="utf-8"
                    ) as file:


                        file.write(
                            "# Frequency_Hz Capacitance Resistance\n"
                        )


                        for freq in frequencies:

                            if self.stop_requested:

                                break


                            self.instrument.write(
                                "FREQ %e" % freq
                            )


                            if not self.wait(delay):

                                break


                            response = self.instrument.query(
                                "FETC?"
                            ).strip()


                            values = response.split(",")


                            if len(values) < 2:

                                raise RuntimeError(
                                    "Unexpected response: "
                                    + response
                                )


                            C = values[0].strip()
                            R = values[1].strip()


                            file.write(
                                "%e %s %s\n"
                                % (
                                    freq,
                                    C,
                                    R
                                )
                            )


                            file.flush()


                            completed += 1


                            percent = (
                                completed
                                / total
                                * 100
                            )


                            self.root.after(
                                0,
                                lambda p=percent:
                                self.progress_value.set(p)
                            )


                            self.root.after(
                                0,
                                lambda f=freq:
                                self.status.set(
                                    "CS/RS - %.0f Hz"
                                    % f
                                )
                            )


                            self.write_log(
                                "CS/RS | %.0f Hz | %s"
                                % (
                                    freq,
                                    response
                                )
                            )


                    self.write_log(
                        "Saved: " + filename
                    )


            self.instrument.write(
                "*CLS"
            )


            if self.stop_requested:

                self.status.set(
                    "Measurement stopped"
                )

                self.write_log(
                    "===== STOPPED ====="
                )

            else:

                self.progress_value.set(
                    100
                )

                self.status.set(
                    "Measurement completed"
                )

                self.write_log(
                    "===== COMPLETED ====="
                )

                self.write_log(
                    "Results saved in:"
                )

                self.write_log(
                    folder
                )


        except Exception as e:

            self.status.set(
                "Measurement error"
            )

            self.write_log(
                "ERROR: " + str(e)
            )


            self.root.after(
                0,
                lambda:
                messagebox.showerror(
                    "Measurement error",
                    str(e)
                )
            )


        finally:

            self.measuring = False

            self.root.after(
                0,
                self.measurement_finished
            )


    # ========================================================
    # FINISHED
    # ========================================================

    def measurement_finished(self):

        self.start_button.config(
            state="normal"
        )

        self.stop_button.config(
            state="disabled"
        )


    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):

        if self.measuring:

            answer = messagebox.askyesno(
                "Measurement running",
                "A measurement is running. Stop and close?"
            )


            if not answer:

                return


            self.stop_requested = True


        try:

            if self.instrument:

                self.instrument.close()


            if self.rm:

                self.rm.close()


        except Exception:

            pass


        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = BK895App(
        root
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        app.close
    )

    root.mainloop()