import queue
import subprocess
import sys
import threading
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


def _run_command(cmd, output_queue, cwd=None):
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=cwd,
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
        self.title("Capital Scout AI")
        self.geometry("900x600")
        self.minsize(780, 540)

        self.colors = {
            "bg": "#f3f3f3",
            "topbar": "#cfd8e3",
            "text": "#1f2937",
            "muted": "#6b7280",
            "upload": "#c3a457",
            "upload_active": "#b79643",
            "success": "#1fb57f",
            "success_active": "#17a271",
            "slate": "#6a7c95",
            "slate_active": "#5a6d85",
            "white": "#ffffff",
        }

        self.output_queue = queue.Queue()
        self.log_window = None
        self.log_text = None
        self.is_running = False
        self.project_dir = Path(__file__).resolve().parent

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

        style.configure("TFrame", background=self.colors["bg"])
        style.configure(
            "TLabel",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Subtitle.TLabel",
            background=self.colors["bg"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Field.TLabel",
            background=self.colors["bg"],
            foreground="#334155",
            font=("Segoe UI Semibold", 9),
        )

        style.configure(
            "TEntry",
            fieldbackground=self.colors["white"],
            foreground=self.colors["text"],
            padding=5,
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "TCheckbutton",
            background=self.colors["bg"],
            foreground=self.colors["text"],
            font=("Segoe UI", 10),
        )

        style.configure(
            "Upload.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(18, 10),
            relief="flat",
            background=self.colors["upload"],
            foreground=self.colors["white"],
        )
        style.map(
            "Upload.TButton",
            background=[("active", self.colors["upload_active"]), ("!disabled", self.colors["upload"])],
            foreground=[("!disabled", self.colors["white"])],
        )

        style.configure(
            "Start.TButton",
            font=("Segoe UI Semibold", 11),
            padding=(16, 10),
            relief="flat",
            background=self.colors["success"],
            foreground=self.colors["white"],
        )
        style.map(
            "Start.TButton",
            background=[("active", self.colors["success_active"]), ("!disabled", self.colors["success"])],
            foreground=[("!disabled", self.colors["white"])],
        )

        style.configure(
            "View.TButton",
            font=("Segoe UI Semibold", 11),
            padding=(16, 10),
            relief="flat",
            background=self.colors["slate"],
            foreground=self.colors["white"],
        )
        style.map(
            "View.TButton",
            background=[("active", self.colors["slate_active"]), ("!disabled", self.colors["slate"])],
            foreground=[("!disabled", self.colors["white"])],
        )

        style.configure(
            "Small.TButton",
            font=("Segoe UI", 9),
            padding=(10, 6),
            relief="flat",
        )

    def _build_ui(self):
        top_bar = tk.Frame(self, bg=self.colors["topbar"], height=26)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=14, pady=(12, 14))

        header = ttk.Frame(body)
        header.pack(fill="x", pady=(0, 14))
        ttk.Label(header, text="Capital Scout AI", font=("Segoe UI Semibold", 19)).pack(side="left")
        ttk.Label(header, text="v1.0.0", style="Subtitle.TLabel").pack(side="right", pady=(4, 0))

        action_row = ttk.Frame(body)
        action_row.pack(fill="x", pady=(0, 8))
        ttk.Button(
            action_row,
            text="  ^   Upload CSV File",
            style="Upload.TButton",
            command=self._pick_input,
        ).pack(side="left")
        ttk.Button(action_row, text="Browse Output", style="Small.TButton", command=self._pick_output).pack(
            side="left", padx=8
        )

        self.file_hint = ttk.Label(body, text="", style="Subtitle.TLabel")
        self.file_hint.pack(anchor="w", pady=(0, 8))
        self.status_label = ttk.Label(body, text="Status: Idle", style="Subtitle.TLabel")
        self.status_label.pack(anchor="w", pady=(0, 8))

        form = ttk.Frame(body)
        form.pack(fill="x", pady=(0, 12))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Input CSV", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.input_path).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=3)

        ttk.Label(form, text="Output Dir", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.output_dir).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=3)

        ttk.Label(form, text="Campaign", style="Field.TLabel").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(form, textvariable=self.campaign).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=3)

        ttk.Checkbutton(form, text="Dry Run (no OpenAI calls)", variable=self.dry_run).grid(
            row=3, column=1, sticky="w", padx=(8, 0), pady=(6, 0)
        )

        ttk.Label(
            body,
            text="Preview Copy (A/B Test)",
            font=("Segoe UI Semibold", 12),
            foreground="#243042",
        ).pack(anchor="w")

        preview = tk.Frame(body, bg=self.colors["bg"])
        preview.pack(fill="both", expand=True, pady=(8, 14))

        bottom = ttk.Frame(body)
        bottom.pack(fill="x")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)

        self.start_btn = ttk.Button(bottom, text="Start Generation", style="Start.TButton", command=self._run)
        self.start_btn.grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(bottom, text="View Logs", style="View.TButton", command=self._open_logs).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )
        ttk.Button(bottom, text="Clear Logs", style="Small.TButton", command=self._clear_logs).grid(
            row=1, column=1, sticky="e", pady=(8, 0)
        )

    def _pick_input(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            self.input_path.set(path)
            shown = path if len(path) <= 82 else f"...{path[-79:]}"
            self.file_hint.configure(text=f"Selected: {shown}")

    def _pick_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def _run(self):
        if self.is_running:
            self._open_logs()
            return

        input_path = self.input_path.get().strip()
        out_dir = self.output_dir.get().strip()
        campaign = self.campaign.get().strip()

        if not input_path or not out_dir or not campaign:
            messagebox.showerror("Missing fields", "Please provide input/output/campaign.")
            return

        cmd = [
            sys.executable,
            str(self.project_dir / "run_agent.py"),
            "--input",
            input_path,
            "--out",
            out_dir,
            "--campaign",
            campaign,
        ]
        if self.dry_run.get():
            cmd.append("--dry-run")

        self.is_running = True
        self.start_btn.state(["disabled"])
        self.status_label.configure(text="Status: Running...")
        self._open_logs()
        self._append_log(f"> {' '.join(cmd)}\n")
        self._append_log("[info] Running generation...\n")

        t = threading.Thread(
            target=_run_command,
            args=(cmd, self.output_queue),
            kwargs={"cwd": str(self.project_dir)},
            daemon=True,
        )
        t.start()

    def _open_logs(self):
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.lift()
            return

        self.log_window = tk.Toplevel(self)
        self.log_window.title("Run Logs")
        self.log_window.geometry("780x420")
        self.log_window.configure(bg=self.colors["bg"])

        frame = ttk.Frame(self.log_window)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        self.log_text = tk.Text(
            frame,
            bg="#ffffff",
            fg="#1f2937",
            relief="solid",
            bd=1,
            wrap="word",
            insertbackground="#1f2937",
        )
        self.log_text.pack(fill="both", expand=True)

    def _clear_logs(self):
        if self.log_window and self.log_window.winfo_exists():
            self.log_text.delete("1.0", "end")

    def _append_log(self, text):
        if not self.log_window or not self.log_window.winfo_exists():
            return
        self.log_text.insert("end", text)
        self.log_text.see("end")

    def _poll_output(self):
        while True:
            try:
                line = self.output_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self._append_log(line)
                if line.strip().startswith("[exit code"):
                    self.is_running = False
                    self.start_btn.state(["!disabled"])
                    if "[exit code 0]" in line:
                        self.status_label.configure(text="Status: Completed")
                        self._open_output_folder()
                    else:
                        self.status_label.configure(text="Status: Failed")
        self.after(100, self._poll_output)

    def _open_output_folder(self):
        output_path = Path(self.output_dir.get().strip()).expanduser()
        if not output_path.is_absolute():
            output_path = self.project_dir / output_path
        try:
            output_path.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(str(output_path))
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(output_path)])
            else:
                subprocess.Popen(["xdg-open", str(output_path)])
        except Exception as exc:
            self._append_log(f"[warn] Could not open output folder: {exc}\n")


if __name__ == "__main__":
    App().mainloop()
