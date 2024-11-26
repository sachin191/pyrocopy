import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

FRAME_PAD_X=1
FRAME_PAD_Y=1

WIDGET_PAD_X=1
WIDGET_PAD_Y=1

LABEL_WIDTH=10
ENTRY_WIDTH=40

TEXTBOX_WIDTH=40
TEXTBOX_HEIGHT=10

class PyrocopyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pyrocopy GUI")

        # Set window size and make it resizable
        root.minsize(420, 300)
        # self.root.geometry("600x600")

        # Create a frame for input fields and buttons
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)

        # Source directory frame
        self.source_frame = tk.Frame(self.input_frame)
        self.source_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)

        self.source_label = tk.Label(self.source_frame, text="Source:", width=LABEL_WIDTH)
        self.source_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.source_entry = tk.Entry(self.source_frame, width=40)
        self.source_entry.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.source_button = tk.Button(self.source_frame, text="Browse", command=self.select_source_directory)
        self.source_button.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Destination directory frame
        self.dest_frame = tk.Frame(self.input_frame)
        self.dest_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)

        self.dest_label = tk.Label(self.dest_frame, text="Destination:", width=LABEL_WIDTH)
        self.dest_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.dest_entry = tk.Entry(self.dest_frame, width=40)
        self.dest_entry.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.dest_button = tk.Button(self.dest_frame, text="Browse", command=self.select_dest_directory)
        self.dest_button.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Create a frame for options (Mirror, Move, Sync, etc.)
        options_frame = tk.Frame(root)
        options_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)

        self.option_label = tk.Label(options_frame, text="Options:", width=LABEL_WIDTH)
        self.option_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Mirror option
        self.mirror_var = tk.BooleanVar()
        self.mirror_check = tk.Checkbutton(options_frame, text="Mirror", variable=self.mirror_var)
        self.mirror_check.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Move option
        self.move_var = tk.BooleanVar()
        self.move_check = tk.Checkbutton(options_frame, text="Move", variable=self.move_var)
        self.move_check.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Sync option
        self.sync_var = tk.BooleanVar()
        self.sync_check = tk.Checkbutton(options_frame, text="Sync", variable=self.sync_var)
        self.sync_check.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Include files frame
        self.include_files_frame = tk.Frame(root)
        self.include_files_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)
        self.include_files_label = tk.Label(self.include_files_frame, text="Include Files (comma separated):", width=LABEL_WIDTH+15)
        self.include_files_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.include_files_entry = tk.Entry(self.include_files_frame, width=ENTRY_WIDTH-10)
        self.include_files_entry.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Include directories frame
        self.include_dirs_frame = tk.Frame(root)
        self.include_dirs_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)
        self.include_dirs_label = tk.Label(self.include_dirs_frame, text="Include Dirs (comma separated):", width=LABEL_WIDTH+15)
        self.include_dirs_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.include_dirs_entry = tk.Entry(self.include_dirs_frame, width=ENTRY_WIDTH-10)
        self.include_dirs_entry.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Exclude files frame
        self.exclude_files_frame = tk.Frame(root)
        self.exclude_files_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)
        self.exclude_files_label = tk.Label(self.exclude_files_frame, text="Exclude Files (comma separated):", width=LABEL_WIDTH+15)
        self.exclude_files_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.exclude_files_entry = tk.Entry(self.exclude_files_frame, width=ENTRY_WIDTH-10)
        self.exclude_files_entry.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Exclude directories frame
        self.exclude_dirs_frame = tk.Frame(root)
        self.exclude_dirs_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)
        self.exclude_dirs_label = tk.Label(self.exclude_dirs_frame, text="Exclude Dirs (comma separated):", width=LABEL_WIDTH+15)
        self.exclude_dirs_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.exclude_dirs_entry = tk.Entry(self.exclude_dirs_frame, width=ENTRY_WIDTH-10)
        self.exclude_dirs_entry.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Level frame
        self.level_frame = tk.Frame(root)
        self.level_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)
        self.level_label = tk.Label(self.level_frame, text="Level (int):", width=LABEL_WIDTH+15)
        self.level_label.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        self.level_entry = tk.Entry(self.level_frame, width=ENTRY_WIDTH-30)
        self.level_entry.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Create a frame for other options
        self.misc_opt_frame = tk.Frame(root)
        self.misc_opt_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)

        # Force (-f) frame
        self.force_var = tk.BooleanVar()
        self.force_check = tk.Checkbutton(self.misc_opt_frame, text="Force", variable=self.force_var)
        self.force_check.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Quiet (-q) or Verbose (-v) frame
        self.quiet_var = tk.BooleanVar()
        self.quiet_check = tk.Checkbutton(self.misc_opt_frame, text="Quiet (-q)", variable=self.quiet_var)
        self.quiet_check.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        self.verbose_var = tk.BooleanVar()
        self.verbose_check = tk.Checkbutton(self.misc_opt_frame, text="Verbose (-v)", variable=self.verbose_var)
        self.verbose_check.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Version option
        self.version_var = tk.BooleanVar()
        self.version_check = tk.Checkbutton(self.misc_opt_frame, text="Show Version", variable=self.version_var)
        self.version_check.pack(side=tk.LEFT, padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Run button
        self.run_button = tk.Button(root, text="Run Pyrocopy", command=self.run_pyrocopy)
        self.run_button.pack(padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)

        # Create a frame for version checkbox and run button
        log_frame = tk.Frame(root)
        log_frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.BOTH, expand=1)
        
        # Text box to display logs
        self.log_text = tk.Text(log_frame, height=TEXTBOX_HEIGHT, width=TEXTBOX_WIDTH, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT,padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y, fill=tk.BOTH, expand=1)

        # Scrollbar for the text box
        self.scrollbar = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=self.scrollbar.set)

    def select_source_directory(self):
        source = filedialog.askdirectory()
        if source:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, source)

    def select_dest_directory(self):
        destination = filedialog.askdirectory()
        if destination:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, destination)

    def log_output(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

    def run_pyrocopy(self):
        # Collect all input values
        source = self.source_entry.get()
        dest = self.dest_entry.get()

        # Basic validation
        if not source or not dest:
            messagebox.showerror("Error", "Source and Destination are required!")
            return
        
        # Prepare the arguments
        args = ["python", "pyrocopy.py"]

        if self.mirror_var.get():
            args.append("--mirror")
        if self.move_var.get():
            args.append("--move")
        if self.sync_var.get():
            args.append("--sync")
        if self.force_var.get():
            args.append("-f")
        if self.quiet_var.get():
            args.append("-q")
        if self.verbose_var.get():
            args.append("-v")
        if self.version_var.get():
            args.append("--version")

        # Include and Exclude files and directories
        include_files = self.include_files_entry.get()
        if include_files:
            args.append(f"-if {include_files}")

        include_dirs = self.include_dirs_entry.get()
        if include_dirs:
            args.append(f"-id {include_dirs}")

        exclude_files = self.exclude_files_entry.get()
        if exclude_files:
            args.append(f"-xf {exclude_files}")

        exclude_dirs = self.exclude_dirs_entry.get()
        if exclude_dirs:
            args.append(f"-xd {exclude_dirs}")

        level = self.level_entry.get()
        if level:
            args.append(f"-l {level}")

        # Add source and destination at the end
        args.append(source)
        args.append(dest)

        # Run the command
        self.log_output("Running Pyrocopy... Please wait.")
        try:
            result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode() + result.stderr.decode()
            self.log_output("Pyrocopy executed successfully!\n" + output)
        except subprocess.CalledProcessError as e:
            self.log_output(f"Error executing Pyrocopy:\n{e.stderr.decode()}")
            messagebox.showerror("Error", f"Error executing Pyrocopy:\n{e.stderr.decode()}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PyrocopyGUI(root)
    root.mainloop()
