import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox


def _run_command(cmd, output_queue):
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        for line in proc.stdout:
            output_queue.put(line)
        proc.wait()
        output_queue.put(f"\n[exit code {proc.returncode}]\n")
    except Exception as exc:
        output_queue.put(f"\n[error] {exc}\n")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Capital Scout AI Desktop")
        self.geometry("820x520")

        self.output_queue = queue.Queue()

        self.input_path = tk.StringVar(value="data/leads.csv")
        self.output_dir = tk.StringVar(value="outputs")
        self.campaign = tk.StringVar(value="week6-demo")
        self.dry_run = tk.BooleanVar(value=True)

        self._build_ui()
        self._poll_output()

    def _build_ui(self):
        form = tk.Frame(self)
        form.pack(fill="x", padx=12, pady=8)

        tk.Label(form, text="Input CSV").grid(row=0, column=0, sticky="w")
        tk.Entry(form, textvariable=self.input_path, width=60).grid(row=0, column=1, padx=6)
        tk.Button(form, text="Browse", command=self._pick_input).grid(row=0, column=2)

        tk.Label(form, text="Output Dir").grid(row=1, column=0, sticky="w")
        tk.Entry(form, textvariable=self.output_dir, width=60).grid(row=1, column=1, padx=6)
        tk.Button(form, text="Browse", command=self._pick_output).grid(row=1, column=2)

        tk.Label(form, text="Campaign").grid(row=2, column=0, sticky="w")
        tk.Entry(form, textvariable=self.campaign, width=60).grid(row=2, column=1, padx=6)

        tk.Checkbutton(form, text="Dry Run (no OpenAI calls)", variable=self.dry_run).grid(
            row=3, column=1, sticky="w"
        )

        btns = tk.Frame(self)
        btns.pack(fill="x", padx=12, pady=6)
        tk.Button(btns, text="Run", command=self._run).pack(side="left")
        tk.Button(btns, text="Clear Log", command=self._clear_log).pack(side="left", padx=6)

        self.log = tk.Text(self, height=20)
        self.log.pack(fill="both", expand=True, padx=12, pady=8)

    def _pick_input(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.input_path.set(path)

    def _pick_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def _run(self):
        input_path = self.input_path.get().strip()
        out_dir = self.output_dir.get().strip()
        campaign = self.campaign.get().strip()

        if not input_path or not out_dir or not campaign:
            messagebox.showerror("Missing fields", "Please fill in Input CSV, Output Dir, and Campaign.")
            return

        cmd = [
            sys.executable,
            "run_agent.py",
            "--input",
            input_path,
            "--out",
            out_dir,
            "--campaign",
            campaign,
        ]
        if self.dry_run.get():
            cmd.append("--dry-run")

        self.log.insert("end", f"> {' '.join(cmd)}\n")
        self.log.see("end")

        t = threading.Thread(target=_run_command, args=(cmd, self.output_queue), daemon=True)
        t.start()

    def _clear_log(self):
        self.log.delete("1.0", "end")

    def _poll_output(self):
        while True:
            try:
                line = self.output_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self.log.insert("end", line)
                self.log.see("end")
        self.after(100, self._poll_output)


if __name__ == "__main__":
    App().mainloop()
