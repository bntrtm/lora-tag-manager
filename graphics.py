from tkinter import Tk, ttk, BOTH, X, Y, WORD, LEFT, RIGHT, TOP, END, S, Label, Frame, Button, Radiobutton, Text, Entry, filedialog, StringVar
from PIL import Image, ImageTk
from logic import on_text_change, add_new_tag
from tags import TagBox
import string

class Window:
    def __init__(self, gui_width, gui_height):
        self.__root = Tk()
        self.__root.title("LoRA Training Text Editor")
        self.__is_running = False
        self.__root.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self.tag_btlist = []
        
        # set up master pane
        self.__p_master = Frame(self.__root, height=gui_height, width=gui_width)
        self.__p_master.pack(fill=BOTH, expand=True, padx=5, pady=5)
        # SET STRICT SIZE:
        self.__p_master.pack_propagate(0)

        # set up persistent info pane
        self.__p_info = Frame(self.__p_master, height=1, width=gui_width, highlightbackground="gray", highlightthickness=2)
        self.__p_info.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)
        self.directory = ""
        self.__bt_load_dir = Button(self.__p_info, text="Load", command=self.load_directory)
        self.__bt_load_dir.pack(side=LEFT)
        self.__l_info = Label(self.__p_info, text=f"Working under directory: {self.directory}")
        self.__l_info.pack(side=LEFT)

        # set up pane to house main elements
        self.__p_hrzbox = Frame(self.__p_master)
        self.__p_hrzbox.pack(side=TOP, fill=BOTH, expand=True)
        #self.__p_hrzbox.pack_propagate(0)
            # set up text editor pane
        self.__p_editor = Frame(self.__p_hrzbox, height=gui_height, highlightbackground="gray", highlightthickness=2)
        self.__p_editor.pack(anchor="w", side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.__l_editor = Label(self.__p_editor, text = "Tag Text Editor")
        self.__l_editor.pack()
        self.__nbk_tagmodes = ttk.Notebook(self.__p_editor, height=18)
        self.__nbk_tagmodes.pack(fill=BOTH, expand=True)
        self.__nbk_tagmodes_tab1 = ttk.Frame(self.__nbk_tagmodes)
        self.__nbk_tagmodes_tab1.pack(padx=5, pady=5)
        self.__nbk_tagmodes_tab2 = ttk.Frame(self.__nbk_tagmodes)
        self.__nbk_tagmodes_tab2.pack()
        self.__nbk_tagmodes.add(self.__nbk_tagmodes_tab1, text="Tags")
        self.__nbk_tagmodes.add(self.__nbk_tagmodes_tab2, text="Editor")
        self.__caption_txt_field = Text(self.__nbk_tagmodes_tab2, wrap=WORD)
        self.__caption_txt_field.insert(END, "anime style, character, blue man, robotic joints, neutral expression, exprNEU, ")
        self.__caption_txt_field.pack(padx=5, pady=5)
                # tag editing radio buttons
        self.__p_tag_radio_bts = Frame(self.__nbk_tagmodes_tab1, width=25)
        self.__p_tag_radio_bts.pack(anchor="nw", padx=5, pady=5)
                    # Tkinter string variable
                    # able to store any string value
        self.tag_click_mode = StringVar(self.__p_tag_radio_bts, "Delete")
                    # Dictionary to create multiple buttons
        tag_click_radio_vals = {"Delete Selected" : "Delete",
                "Apply Selected to All" : "Apply_All"}
                    # Create buttons
        for (text, value) in tag_click_radio_vals.items():
            Radiobutton(self.__p_tag_radio_bts, text = text, variable = self.tag_click_mode, 
                        value = value).pack(side=LEFT, fill = X, ipady = 5)
                # tagbox (buttons) container
        self.__p_tag_container = Frame(self.__nbk_tagmodes_tab1)
        self.__p_tag_container.pack(anchor="sw", padx=5, pady=5)
        self.load_tags_as_boxes(self.__p_tag_container, self.__caption_txt_field.get("1.0", "end"))

                # set up pane for singular tag entry
        self.__p_tagger = Frame(self.__p_editor)
        self.__p_tagger.pack(side=LEFT)
        self.tag_entry_text = StringVar()
        self.__txt_tag_entry = Entry(self.__p_tagger, textvariable=self.tag_entry_text) #, height=1, width=50
        self.__txt_tag_entry.pack(anchor="nw")
        self.__txt_tag_entry.bind("<Return>", lambda event: on_text_change(event, self))
        self.__txt_tag_entry.bind("<FocusIn>", lambda event: self.on_focus_in_entry_widget(event, self.__txt_tag_entry, "Enter a tag..."))
        self.__txt_tag_entry.bind("<FocusOut>", lambda event: self.on_focus_out_entry_widget(event, self.__txt_tag_entry, "Enter a tag..."))
        self.on_focus_out_entry_widget("<FocusOut>", self.__txt_tag_entry, "Enter a tag...")
                    # application radio buttons
        self.__p_radio_bts = Frame(self.__p_tagger, width=25)
        self.__p_radio_bts.pack(anchor="sw")
                    # Tkinter string variable
                    # able to store any string value
        self.application_mode = StringVar(self.__p_radio_bts, "Current")
                    # Dictionary to create multiple buttons
        application_radio_vals = {"Apply to Current" : "Current",
                "Apply to All" : "All"}
                    # Create buttons
        for (text, value) in application_radio_vals.items():
            Radiobutton(self.__p_radio_bts, text = text, variable = self.application_mode, 
                        value = value).pack(side=LEFT, fill = X, ipady = 5)

            # set up image viewer pane
        self.__p_viewer = Frame(self.__p_hrzbox, height=gui_height, highlightbackground="gray", highlightthickness=2)
        self.__p_viewer.pack(anchor="e", side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.__l_viewer = Label(self.__p_viewer, text="Current: ")
        self.__l_viewer.pack()
        self.__l_image = Label(self.__p_viewer)
        self.__l_image.pack(anchor=S)
        # FOR TESTING ONLY
        self.open_image('./testing/Blue_Neutral.png')
    
    def open_image(self, path):
        #file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if path and path.endswith('.png'):
            self.display_image(path)
        else:
            print("No image!")

    def display_image(self, file_path):
        image = Image.open(file_path) # open image
        photo = ImageTk.PhotoImage(image) # convert for tkinter compatibility
        self.__l_image.config(image=photo)
        self.__l_viewer.image = photo
        self.__l_viewer.config(text=f"Current: {file_path}")

    def load_directory(self):
        self.directory = filedialog.askdirectory()
        self.__l_info.config(text=f"Working under directory: {self.directory}")

    def add_new_tagbox(self, widget, tag_string):
        new_bt = TagBox(self, widget, tag_string)
        self.tag_btlist.append(new_bt)
        self.display_tagbox_grid()

    def load_tags_as_boxes(self, widget, tag_string, reload=False):
        if reload:
            for button in self.tag_btlist:
                button.delete()
            self.tag_btlist = []
            #self.load_tags_as_boxes(widget, tag_string)
        tag_strs = tag_string.split(", ")
        for tag in tag_strs:
            if not tag.isspace():
                self.add_new_tagbox(self.__p_tag_container, tag)
        self.display_tagbox_grid()
    
    def display_tagbox_grid(self):
        col_n = 0
        row_n = 0
        for tagbox in self.tag_btlist:
            span = max((len(tagbox.tag_text) // 15), 1)
            tagbox.bt.grid(sticky="w", row=row_n, column=col_n, padx=2, pady=2, columnspan=span)
            col_n += span
            if col_n > 3:
                col_n = 0
                row_n += 1                

    def on_focus_in_entry_widget(self, event, widget, placeholder_text):
        if isinstance(widget, Entry):
            text = widget.get()
        elif isinstance(widget, Text):
            text = widget.get("1.0", "end-1c") # USED FOR TEXT WIDGETS ONLY
        else:
            return
        if text == placeholder_text:
            widget.delete(0, "end")
            widget.config(fg="black")

    def vcmd():
        disallowed_chars = ["\n", "!"]
        for char in disallowed_chars:
            if char in new_value:
                return False
        return True

    def on_focus_out_entry_widget(self, event, widget, placeholder_text):
        if isinstance(widget, Entry):
            text = widget.get()
        elif isinstance(widget, Text):
            text = widget.get("1.0", "end-1c") # USED FOR TEXT WIDGETS ONLY
        if len(text) == 0:
            widget.config(fg="gray")
            widget.insert(END, placeholder_text)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()
    
    def wait_for_close(self):
        self.__is_running = True
        while self.__is_running:
            self.redraw()
        print("window closed...")

    def close(self):
        self.__is_running = False