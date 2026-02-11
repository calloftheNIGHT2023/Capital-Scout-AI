import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


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
        self.geometry("900x620")
        self.minsize(860, 580)

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "muted": "#94a3b8",
            "accent": "#22d3ee",
            "accent_dark": "#0ea5b7",
            "text": "#e5e7eb",
            "border": "#1f2937",
            "success": "#22c55e",
        }

        self.output_queue = queue.Queue()

        self.input_path = tk.StringVar(value="data/leads.csv")
        self.output_dir = tk.StringVar(value="outputs")
        self.campaign = tk.StringVar(value="week6-demo")
        self.dry_run = tk.BooleanVar(value=True)

        self._setup_style()
        self._build_ui()
        self._poll_output()

    def _setup_style(self):
        self.configure(bg=self.colors["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "TFrame",
            background=self.colors["bg"],
        )
        style.configure(
            "Card.TFrame",
            background=self.colors["panel"],
            relief="flat",
        )
        style.configure(
            "TLabel",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Segoe UI Semibold", 18),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "TEntry",
            fieldbackground="#0b1220",
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            insertcolor=self.colors["text"],
            relief="flat",
            padding=6,
        )
        style.map(
            "Accent.TButton",
            background=[("active", self.colors["accent_dark"]), ("!disabled", self.colors["accent"])],
            foreground=[("!disabled", "#001018")],
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(12, 6),
            relief="flat",
            background=self.colors["accent"],
            foreground="#001018",
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 10),
            padding=(10, 6),
        )
        style.configure(
            "TCheckbutton",
            background=self.colors["panel"],
            foreground=self.colors["text"],
        )

    def _build_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=(16, 6))
        ttk.Label(header, text="Capital Scout AI", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Outreach automation demo • CSV in, campaigns out",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))

        card = ttk.Frame(self, style="Card.TFrame")
        card.pack(fill="x", padx=20, pady=10)

        form = ttk.Frame(card, style="Card.TFrame")
        form.pack(fill="x", padx=16, pady=16)

        ttk.Label(form, text="Input CSV").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.input_path, width=62).grid(row=0, column=1, padx=8, pady=4)
        ttk.Button(form, text="Browse", command=self._pick_input).grid(row=0, column=2, pady=4)

        ttk.Label(form, text="Output Dir").grid(row=1, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.output_dir, width=62).grid(row=1, column=1, padx=8, pady=4)
        ttk.Button(form, text="Browse", command=self._pick_output).grid(row=1, column=2, pady=4)

        ttk.Label(form, text="Campaign").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.campaign, width=62).grid(row=2, column=1, padx=8, pady=4)

        ttk.Checkbutton(form, text="Dry Run (no OpenAI calls)", variable=self.dry_run).grid(
            row=3, column=1, sticky="w", pady=(8, 2)
        )

        btns = ttk.Frame(card, style="Card.TFrame")
        btns.pack(fill="x", padx=16, pady=(0, 14))
        ttk.Button(btns, text="Run", style="Accent.TButton", command=self._run).pack(side="left")
        ttk.Button(btns, text="Clear Log", command=self._clear_log).pack(side="left", padx=8)

        log_panel = ttk.Frame(self, style="Card.TFrame")
        log_panel.pack(fill="both", expand=True, padx=20, pady=(4, 16))
        ttk.Label(log_panel, text="Run Output").pack(anchor="w", padx=16, pady=(12, 6))

        self.log = tk.Text(
            log_panel,
            height=18,
            bg="#0b1220",
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="flat",
        )
        self.log.pack(fill="both", expand=True, padx=16, pady=(0, 16))

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
