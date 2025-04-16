import tkinter as tk
from tkinter import filedialog, messagebox
from Tks import tks
import subprocess

# ToDo
# 1. Do thorough testing - check functionality
# 2. Separate Tks as a package in differnt git repo and use it as module
# 3. self.widgets as a directory
# 4. same variable for copy options:

class PyrocopyApp:
    def __init__(self, tks, root):
        self.tks = tks
        self.frame_root = root
        pass

    def CreateAppGUI(self):
        # Create source and destination directory frame
        wgt = self.tks.CreateFramedFileSelect(self.frame_root, "Source:", "Browse", self.select_source_directory)
        self.wgt_entry_source = wgt['entry']
        wgt = self.tks.CreateFramedFileSelect(self.frame_root, "Destination:", "Browse", self.select_dest_directory)
        self.wgt_entry_dest = wgt['entry']

        # Create a frame for options (Mirror, Move, Sync, etc.)
        chk_button_param_list=[
            {'text':"Mirror", 'var':'mirror_var'},
            {'text':"Move",   'var':'move_var'},
            {'text':"Sync",   'var':'sync_var'}
        ]
        self.tks.CreateFramedCheckButtons(self.frame_root, "Options:", chk_button_param_list )

        # Create entry fields for include/exclude files/directories and levels
        wgt = self.tks.CreateFramedEntry(self.frame_root, "Include Files (comma separated):")
        self.include_files_entry = wgt['entry']
        wgt = self.tks.CreateFramedEntry(self.frame_root, "Include Dirs (comma separated):")
        self.include_dirs_entry = wgt['entry']
        wgt = self.tks.CreateFramedEntry(self.frame_root, "Exclude Files (comma separated):")
        self.exclude_files_entry = wgt['entry']
        wgt = self.tks.CreateFramedEntry(self.frame_root, "Exclude Dirs (comma separated):")
        self.exclude_dirs_entry = wgt['entry']

        wgt = self.tks.CreateFramedEntry(self.frame_root, "Level (int):", entry_width=self.tks.GetDeafultEntryWidth()-30)
        self.level_entry = wgt['entry']

        # Create a frame for other options
        chk_button_param_list=[
            {'text':"Force",        'var':'force_var'},
            {'text':"Quiet (-q)",   'var':'quiet_var'},
            {'text':"Verbose (-v)", 'var':'verbose_var'},
            {'text':"Show Version", 'var':'version_var'}
        ]
        self.tks.CreateFramedCheckButtons(self.frame_root, "", chk_button_param_list )

        # Create run button and textbox to display logs
        self.tks.CreateFramedButtons(self.frame_root, "", [{'text':"Run Pyrocopy",'command':self.run_pyrocopy}], fill=tk.X, expand=1)
        wgt = self.tks.CreateFramedTextWithScrollBar(self.frame_root)
        self.wgt_text_log = wgt['text']

        return

    def select_source_directory(self):
        source = filedialog.askdirectory()
        if source:
            self.wgt_entry_source.delete(0, tk.END)
            self.wgt_entry_source.insert(0, source)

    def select_dest_directory(self):
        destination = filedialog.askdirectory()
        if destination:
            self.wgt_entry_dest.delete(0, tk.END)
            self.wgt_entry_dest.insert(0, destination)

    def log_output(self, text):
        self.wgt_text_log.config(state=tk.NORMAL)
        self.wgt_text_log.insert(tk.END, text + "\n")
        self.wgt_text_log.config(state=tk.DISABLED)
        self.wgt_text_log.yview(tk.END)

    def run_pyrocopy(self):
        # Collect all input values
        source = self.wgt_entry_source.get()
        dest = self.wgt_entry_dest.get()

        # Basic validation
        if not source or not dest:
            messagebox.showerror("Error", "Source and Destination are required!")
            return
        
        # Prepare the arguments
        args = ["python", "pyrocopy.py"]

        if self.tks.check_button_var_dict['mirror_var'].get():
            args.append("--mirror")
        if self.tks.check_button_var_dict['move_var'].get():
            args.append("--move")
        if self.tks.check_button_var_dict['sync_var'].get():
            args.append("--sync")
        if self.tks.check_button_var_dict['force_var'].get():
            args.append("-f")
        if self.tks.check_button_var_dict['quiet_var'].get():
            args.append("-q")
        if self.tks.check_button_var_dict['verbose_var'].get():
            args.append("-v")
        if self.tks.check_button_var_dict['version_var'].get():
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
            # output = args
            self.log_output(f"Pyrocopy executed successfully!\n{output}")
        except subprocess.CalledProcessError as e:
            self.log_output(f"Error executing Pyrocopy:\n{e.stderr.decode()}")
            messagebox.showerror("Error", f"Error executing Pyrocopy:\n{e.stderr.decode()}")

if __name__ == "__main__":
    tks = tks.Tks(title = "Pyrocopy App", width=380, height=400)
    root = tks.GetFrameRoot()
    app = PyrocopyApp(tks, root)
    app.CreateAppGUI()
    root.mainloop()