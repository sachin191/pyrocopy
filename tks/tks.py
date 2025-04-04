import tkinter as tk
from tkinter import filedialog, messagebox

FRAME_PAD_X=1
FRAME_PAD_Y=1

WIDGET_PAD_X=1
WIDGET_PAD_Y=1

LABEL_WIDTH=10
ENTRY_WIDTH=40

TEXT_WIDTH=40
TEXT_HEIGHT=10

# ToDo
# 1. Add set function for default vales - and parameterize width, height
# 2. Better way to list default values - may be enum
# 3. Add image widget
# 4. Add drop down list
# 5. Add drop down list widget with values get added as entered by user
# 6. Add List item seletion widgte width scorll bars

# Utlity for creating TkInter GUI Applications
class Tks():
    def __init__(self, title = "", width=600, height=400):
        # Create root frame
        self.frame_root = tk.Tk()
        self.frame_root.title(title)
        self.frame_root.minsize(width, height)

        # Create top frame
        self.frame_top = self.CreateFrame(self.frame_root)['frame']
        self.check_button_var_dict = {}
        return 

    # Get Default values
    def GetDeafultFramePadX(self):
        return(FRAME_PAD_X)
    def GetDeafultFramePadY(self):
        return(FRAME_PAD_Y)
    def GetDeafultWidgetPadY(self):
        return(WIDGET_PAD_X)
    def GetDeafultWidgetPadY(self):
        return(WIDGET_PAD_Y)
    def GetDeafultLabelWidth(self):
        return(LABEL_WIDTH)
    def GetDeafultEntryWidth(self):
        return(ENTRY_WIDTH)
    def GetDeafultTextWidth(self):
        return(TEXT_WIDTH)
    def GetDeafultTextHeight(self):
        return(TEXT_HEIGHT)

    def GetFrameRoot(self):
        return self.frame_root
    
    def GetFrameTop(self):
        return self.frame_top

    def PackFrame(self, frame, padx=FRAME_PAD_X, pady=FRAME_PAD_Y, side="", fill=tk.X, expand="", debug=0):
        frame.pack(padx=padx, pady=pady)
        if (side != ""): frame.pack(side=side)
        if (fill != ""): frame.pack(fill=fill)
        if (expand != ""): frame.pack(expand=expand)
        if (debug):
            print(f"Frame side:'{side}' fill:'{fill}' expand:'{expand}'")
        return

    def CreateFrame(self, root, side=tk.LEFT, fill="", expand =""):
        frame = tk.Frame(root)
        frame.pack(padx=FRAME_PAD_X, pady=FRAME_PAD_Y, fill=tk.X)
        return {'frame':frame}

    def PackWidget(self, wgt, padx=FRAME_PAD_X, pady=FRAME_PAD_Y, side=tk.LEFT, fill="", expand ="", debug=0):
        wgt.pack(padx=WIDGET_PAD_X, pady=WIDGET_PAD_Y)
        if (side != ""): wgt.pack(side=side)
        if (fill != ""): wgt.pack(fill=fill)
        if (expand != ""): wgt.pack(expand=expand)
        if (debug):
            print(f"Widget side:'{side}' fill:'{fill}' expand:'{expand}'")
        return

    def CreateFramedEntry(self, root, label_str, entry_width=''):
        frame = tk.Frame(root)
        self.PackFrame(frame)
        label = tk.Label(frame, text=label_str, width=LABEL_WIDTH+15)
        self.PackWidget(label)
        if (entry_width == ''): entry_width = ENTRY_WIDTH-10
        entry = tk.Entry(frame, width=entry_width)
        self.PackWidget(entry)
        return {'frame':frame, 'label':label, 'entry':entry}

    def CreateFramedFileSelect(self, root, label_str, button_str, cmd):
        frame = tk.Frame(root)
        self.PackFrame(frame)
        label = tk.Label(frame, text=label_str, width=LABEL_WIDTH)
        self.PackWidget(label)
        entry = tk.Entry(frame, width=40)
        self.PackWidget(entry)
        button = tk.Button(frame, text=button_str, command=cmd)
        self.PackWidget(button)
        return {'frame':frame, 'label':label, 'entry':entry, 'button':button}

    def CreateFramedButtons(self, root, label_str, button_list,
                            side=tk.LEFT, fill="", expand =""):
        frame = tk.Frame(root)
        self.PackFrame(frame)
        label = ''
        if (label_str != ""):
            label = tk.Label(frame, text=label_str, width=LABEL_WIDTH)
            self.PackWidget(label)
        for button in button_list:
            button = tk.Button(frame, command=button['command'], text=button['text'])
            self.PackWidget(button, side=side, fill=fill, expand=expand)
        return {'frame':frame, 'label':label, 'button':button}

    def CreateFramedCheckButtons(self, root, label_str, chk_button_param_list,
                                 side=tk.LEFT, fill="", expand =""):
        frame = tk.Frame(root)
        self.PackFrame(frame)
        label = ''
        if (label_str != ""):
            label = tk.Label(frame, text=label_str, width=LABEL_WIDTH)
            self.PackWidget(label)
        chk_button_wgt_list = []
        for chk_button in chk_button_param_list:
            text=chk_button['text']
            var_name=chk_button['var']
            var = tk.BooleanVar()
            chk_button_wgt = tk.Checkbutton(frame, text=text, variable=var)
            self.check_button_var_dict.update({var_name:var})
            chk_button_wgt_list.append(chk_button_wgt)
            self.PackWidget(chk_button_wgt, side=side, fill=fill, expand=expand)
        return {'frame':frame, 'label':label, 'check_button':chk_button_wgt_list}
        
    def CreateFramedTextWithScrollBar(self, root):
        frame = tk.Frame(root)
        self.PackFrame(frame, fill=tk.BOTH, expand=1)
        text = tk.Text(frame, height=TEXT_HEIGHT, width=TEXT_WIDTH, wrap=tk.WORD, state=tk.DISABLED)
        self.PackWidget(text, fill=tk.BOTH, expand=1)
        scrollbar = tk.Scrollbar(frame, command=text.yview)
        self.PackWidget(scrollbar, side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)
        return {'frame':frame, 'text':text, 'scrollbar':scrollbar}
