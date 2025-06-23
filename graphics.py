from tkinter import Tk, ttk, Toplevel, BOTH, X, Y, WORD, LEFT, RIGHT, TOP, END, N, S, Label, Frame, Button, Radiobutton, Text, Entry, filedialog, StringVar, IntVar, Checkbutton
from PIL import Image, ImageTk
from tags import TagBox
import string
from lora import LoRA
from log_format import str_tail_after
import os

#TODO: Add an export button
#TODO: Fix image resize bug
    #TODO: ensure resizing window actually updates image label size

class Window:
    def __init__(self, gui_width, gui_height, title="LoRA Tag Manager", is_child=False):
        self.__is_running = False
        if is_child:
            self.__root = Toplevel()
        else:
            self.__root = Tk()
        self.__root.title(title)
        self.__root.protocol(name="WM_DELETE_WINDOW", func=self.close)
        self.__root.bind('<Configure>', self.on_resize) 
        self.active_queue_win = None

        # set up master pane
        self.__p_master = Frame(self.__root, height=gui_height, width=gui_width)
        self.__p_master.pack(fill=BOTH, expand=True, padx=5, pady=5)
        # SET STRICT SIZE:
        self.__p_master.pack_propagate(0)
    
    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()
    
    def wait_for_close(self):
        self.__is_running = True
        while self.__is_running:
            self.redraw()
        print("Window closed.")

    def start_queue(self, queue, func_on_yes=None):
        self.active_queue_win = AddTxtQueueWin(300, 125, queue, self, func_on_yes=func_on_yes)
        self.active_queue_win.progress()
        # MAINLOOP
        self.active_queue_win.wait_for_close()

    def end_queue(self):
        self.active_queue_win.close()
        self.active_queue_win = None
        
    def close(self):
        self.__is_running = False
        self.__root.destroy()
    
    def on_resize(self, event):
        pass

class AddTxtQueueWin(Window):
    def __init__(self, gui_width, gui_height, queue, caller_win, func_on_yes=None):
        super().__init__(gui_width, gui_height, title=".txt Caption Lookup Failure", is_child=True)
        self.caller_win = caller_win
        #self._Window__root.attributes('-topmost', True)
        self._Window__root.protocol(name="WM_DELETE_WINDOW", func=self.respond_close_failure)
        self.queue = queue
        self.func_on_yes = func_on_yes
        self.current = None
        # set up pane to display information and prompt user for action
        self.__p_info = Frame(self._Window__p_master, height=3, width=gui_width)
        self.__p_info.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)
        self.__l_info = Label(self.__p_info, text= f"Click YES.")
        self.__l_info.pack(side=LEFT)
        self.__p_options = Frame(self._Window__p_master, height=1, width=gui_width)
        self.__p_options.pack()
        self.checkbox_var = IntVar()
        self.checkbox_var.set(0)
        self.checkbox = Checkbutton(self.__p_options, text="Apply for all in queue", variable=self.checkbox_var, onvalue=1, offvalue=0)
        self.checkbox.pack(side=LEFT)
        self.__bt_yes = Button(self.__p_options, text="Yes", command=self.confirm_yes)
        self.__bt_yes.pack(side=LEFT)
        self.__bt_no = Button(self.__p_options, text="No", command=self.confirm_no)
        self.__bt_no.pack(side=LEFT)
    
    def respond_close_failure(self):
        print("User attempted to close window, but option for queue item not chosen.")
        print(f"Choose 'Yes' or 'No' for the current queue item: {self.current}")

    def confirm_yes(self):
        with open(f'{self.current.replace('.png', '.txt')}', "x") as f:
            pass
        self.func_on_yes(self.current)
        self.progress()
    
    def confirm_no(self):
        if self.checkbox_var.get() == 1:
            self.queue = None
            self.caller_win.end_queue()
        else:
            self.progress()
    
    def progress(self):
        self.current = self.queue.pop()
        if self.current is None:
            self.queue = None
            self.caller_win.end_queue()
            return
        self.__l_info.config(text=f"No corresponding .txt file exists for image: \n'{self.current}'. \nWould you like to create one?")

def require_LoRA(func):
        def wrapper(*args, **kwargs):
            if args[0].lora_in_training is None:
                raise Exception('no LoRA object exists for the current session; load a directory to create one')
            result = func(*args, **kwargs)
            return result
        return wrapper

class TrainLoraWin(Window):
    def __init__(self, gui_width, gui_height, title="LoRA Tag Manager"):
        super().__init__(gui_width, gui_height, title="LoRA Tag Manager")
        self.tag_btlist = []
        self.lora_in_training = None
        self.current_display_image = None

        # set up persistent info pane
        self.__p_info = Frame(self._Window__p_master, height=1, width=gui_width, highlightbackground="gray", highlightthickness=2)
        self.__p_info.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)
        self.directory = ""
        self.__bt_load_dir = Button(self.__p_info, text="Load", command=self.load_directory)
        self.__bt_load_dir.pack(side=LEFT)
        self.__l_info = Label(self.__p_info, text=f"Working under directory: {self.directory}")
        self.__l_info.pack(side=LEFT)

        # set up pane to house main elements
        self.__p_hrzbox = Frame(self._Window__p_master)
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
        self.__nbk_tagmodes.add(self.__nbk_tagmodes_tab1, text="Tag Editor")
        self.__nbk_tagmodes.add(self.__nbk_tagmodes_tab2, text="Caption")
        self.__caption_txt_field = Text(self.__nbk_tagmodes_tab2, wrap=WORD, state='disabled')
        self.__caption_txt_field.pack(padx=5, pady=5)
                # tag editing radio buttons
        self.__p_tag_radio_bts = Frame(self.__nbk_tagmodes_tab1, width=25)
        self.__p_tag_radio_bts.pack(anchor="nw", padx=5, pady=5)
                    # Tkinter string variable
                    # able to store any string value
        self.tag_click_mode = StringVar(self.__p_tag_radio_bts, "Delete")
                    # Dictionary to create multiple buttons
        tag_click_radio_vals = {"Delete Selected" : "Delete",
                "Apply Selected to All" : "Apply_All",
                "Delete Selected from All" : "Delete_All"}
                    # Create buttons
        for (text, value) in tag_click_radio_vals.items():
            Radiobutton(self.__p_tag_radio_bts, text = text, variable = self.tag_click_mode, 
                        value = value).pack(side=LEFT, fill = X, ipady = 5)
                # tagbox (buttons) container
        self.__p_tag_container = Frame(self.__nbk_tagmodes_tab1)
        self.__p_tag_container.pack(anchor="sw", padx=5, pady=5)

                # set up pane for singular tag entry
        self.__p_tagger = Frame(self.__p_editor)
        self.__p_tagger.pack(side=LEFT)
        self.tag_entry_text = StringVar()
        self.__txt_tag_entry = Entry(self.__p_tagger, textvariable=self.tag_entry_text) #, height=1, width=50
        self.__txt_tag_entry.pack(anchor="nw")
        self.tag_entry_text.trace_add('write', self.trace_tag_entry)
        self.__txt_tag_entry.bind("<Return>", lambda event: self.on_tag_entry(event, self))
        self.__txt_tag_entry.bind("<Tab>", self.on_tag_auto)
        self.__txt_tag_entry.bind("<Up>", self.nav_autofill)
        self.__txt_tag_entry.bind("<Down>", self.nav_autofill)
        self.__txt_tag_entry.bind("<FocusIn>", lambda event: self.on_focus_in_entry_widget(event, self.__txt_tag_entry, "Enter a tag..."))
        self.__txt_tag_entry.bind("<FocusOut>", lambda event: self.on_focus_out_entry_widget(event, self.__txt_tag_entry, "Enter a tag..."))
        self.on_focus_out_entry_widget("<FocusOut>", self.__txt_tag_entry, "Enter a tag...")

                    # autofill box
        self.__autofill_box = SuggestBox(self.__p_editor, color='red')

                    # application radio buttons
        self.__p_radio_bts = Frame(self.__p_tagger, width=25)
        self.__p_radio_bts.pack(anchor="sw")
        self.application_mode = StringVar(self.__p_radio_bts, "Apply")
        application_radio_vals = {"Apply to Current" : "Apply",
                "Apply to All" : "Apply_All"}
        for (text, value) in application_radio_vals.items():
            Radiobutton(self.__p_radio_bts, text = text, variable = self.application_mode, 
                        value = value).pack(side=LEFT, fill = X, ipady = 5)

            # set up image viewer pane
        self.__p_viewer = Frame(self.__p_hrzbox, height=gui_height, highlightbackground="gray", highlightthickness=2)
        self.__p_viewer.pack(anchor="e", side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.__p_viewer.pack_propagate(0)
        self.__l_viewer = Label(self.__p_viewer, text="Current: ")
        self.__l_viewer.pack()
        self.__p_display = Frame(self.__p_viewer)
        self.__p_display.pack(fill=BOTH, expand=True)
        self.__bt_decrdisplay = Button(self.__p_display, text=' <- ', command=self.decr_display)
        self.__bt_decrdisplay.grid(column=0, row=0, sticky='w')
        self.__bt_savecurrent = Button(self.__p_display, text='Refresh', command=self.refresh)
        self.__bt_savecurrent.grid(column=1, row=0, columnspan=2)
        self.__bt_incrdisplay = Button(self.__p_display, text=' -> ', command=self.incr_display)
        self.__bt_incrdisplay.grid(column=3, row=0, sticky='e')
        self.__l_image = Label(self.__p_viewer)
        self.__l_image.pack(fill=BOTH, expand=True)

    def on_resize(self, event):
        if not self.display_image:
            self.display_image()

    @require_LoRA
    def get_png_path(self):
        return self.lora_in_training.image_set[self.get_display_index()]
    
    @require_LoRA
    def get_txt_caption(self):
        return self.lora_in_training.dataset[self.get_png_path()][1]

    @require_LoRA
    def get_display_index(self):
        return self.lora_in_training.display_index
    
    @require_LoRA
    def set_display_index(self, val):
        self.lora_in_training.display_index = val

    @require_LoRA
    def tag_in_caption(self, tag):
        return self.lora_in_training.tag_in_caption(tag)

    def refresh(self):
        self.display_training_element(refresh=True)

    def display_training_element(self, refresh=False):
        self.open_image(self.get_png_path())
        self.load_caption(self.get_png_path())

    def incr_display(self):
        if self.get_display_index() == len(self.lora_in_training.image_set) - 1:
            self.set_display_index(0)
        else:
            self.set_display_index(self.get_display_index() + 1)
        self.display_training_element()

    def decr_display(self):
        if self.get_display_index() == 0:
            self.set_display_index(len(self.lora_in_training.image_set) - 1)
        else:
            self.set_display_index(self.get_display_index() - 1)
        self.display_training_element()
    
    def set_caption_display_text(self, text):
        self.__caption_txt_field.config(state='normal')
        self.__caption_txt_field.delete("1.0", "end")
        self.__caption_txt_field.insert(END, text)
        self.__caption_txt_field.config(state='disabled')

    def load_caption(self, png_path):
        '''Loads contents of the editor window and all caption tags as interactive buttons

        1) Deletes contents of editor.
        2) Adds contents of txt_path file corresponding to png_path in the LoRA dataset.
        3) Generates buttons representing each tag within the dataset and displays them in the 'Tags' window.
        '''
        self.set_caption_display_text(self.get_txt_caption())
        self.display_tags_as_boxes(self.__p_tag_container, self.get_txt_caption())
    
    def open_image(self, png_path, refresh=False):
        if png_path and png_path.endswith('.png'):
            self.load_image(png_path)
            self.display_image()
            self.__l_viewer.config(text=f"Current: {str_tail_after(self.directory, '/')}...{str_tail_after(png_path, '/')}")
        else:
            raise Exception('only images with .png extensions may be opened')

    def load_image(self, file_path):
        self.current_display_image = Image.open(file_path)

    def display_image(self, refresh=False):
        if not self.current_display_image:
            raise Exception('No image set to display')
        # FIXME: resizing does not fill entire image label; takes a few refreshes before it does.
        def img_fit_to_height(label):
            label.update_idletasks()
            label.update()
            img = self.current_display_image
            target_height = label.winfo_height()
            # get original aspect ratio as width/height
            original_aspect = img.size[0] / img.size[1]
            target_width = int(target_height * original_aspect)
            resized = img.resize((target_width, target_height))
            return resized

        resized_image = img_fit_to_height(self.__l_image)
        photo = ImageTk.PhotoImage(resized_image) # convert for tkinter compatibility
        self.__l_image.config(image=photo)
        self.__l_image.image = photo

    def load_directory(self):
        self.directory = filedialog.askdirectory()
        if not os.path.isdir(self.directory):
            print('Directory load operation was canceled.')
            return
        self.__l_info.config(text=f"Working under directory: {self.directory}")
        self.lora_in_training = LoRA(self.directory, self)
        if len(self.lora_in_training.dataset) == 0:
            self.lora_in_training = None
            raise Exception(f'No images were found under directory {self.directory}')
        self.display_training_element()

    def add_new_tagbox(self, widget, tag):
        new_bt = TagBox(self, widget, tag)
        self.tag_btlist.append(new_bt)
        self.display_tagbox_grid()

    def display_tags_as_boxes(self, widget, tag_string, reload=True):
        #FIXME: when entering an already existing tag, SOME existing tag is generated (though no doubles are added, as intended)
        '''Deletes tagboxes that should not exist, adds those that should
        '''
        tag_strs = tag_string.rstrip(', ').split(", ")
        if len(self.tag_btlist) > 0:
            keep_bts = []
            for button in self.tag_btlist:
                if button.is_trigger:
                    keep_bts.append(button)
                    tag_strs.remove(button.tag_text)
                elif self.tag_in_caption(button.tag_text):
                    keep_bts.append(button)
                    tag_strs.remove(button.tag_text)
                else:
                    button.destroy()
            self.tag_btlist = keep_bts
        for tag in tag_strs:
            if tag.isspace() or not tag:
                continue
            else:
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

    def on_tag_entry(self, event, win):
        negate = False
        entry = self.__txt_tag_entry
        if self.__autofill_box.selected:
            text = self.__autofill_box.selected.cget("text")
        else:
            text = entry.get().rstrip(", ").replace(",", "").lower()
        if text.startswith('-'):
            negate = True
            text = text.lstrip('-')
        entry.delete(0, "end")
        
        @require_LoRA
        def try_continue(self):
            if text == self.lora_in_training.trigger_word:
                return
            match self.application_mode.get():
                case "Apply":
                    if negate:
                        self.lora_in_training.remove_tag_from_image_caption(text, png_path=self.get_png_path())
                    else:
                        self.lora_in_training.add_tag_to_image_caption(text, png_path=self.get_png_path())
                case "Apply_All":
                    if negate:
                        print(f'Removing tag "{text}" from all .txt files in dataset {self.directory}')
                        self.lora_in_training.remove_tag_from_image_caption(text, png_path=self.get_png_path(), all=True)
                    else:
                        print(f'Applying tag "{text}" to all .txt files in dataset {self.directory}')
                        self.lora_in_training.add_tag_to_image_caption(text, png_path=self.get_png_path(), all=True)
                case _:
                    raise ValueError("only 'Apply' and 'Apply_All' are acceptable actions")
            self.refresh()

        try_continue(self)
        return "break"
    
    def on_tag_auto(self, event):
        option_1_text = self.__autofill_box.labels[0].cget("text")
        if option_1_text:
            if self.tag_entry_text.get().startswith('-'):
                self.tag_entry_text.set(f'-{option_1_text}')
            else:
                self.tag_entry_text.set(option_1_text)
            self.__txt_tag_entry.icursor(END)
        return "break"
    
    @require_LoRA
    def trace_tag_entry(self, var, index, mode):
        text = self.tag_entry_text.get().lower()
        if not text:
            self.__autofill_box.update([])
            return
        words_with_pre = self.lora_in_training.tag_trie.words_with_prefix(text.lstrip('-'))
        options = []
        if len(words_with_pre) > 0:
            for suggestion in words_with_pre:
                if self.lora_in_training.trigger_word == suggestion:
                    continue
                if text.startswith('-'):
                    if not self.tag_in_caption(suggestion):
                        continue
                else:
                    if self.tag_in_caption(suggestion):
                        continue
                options.append(suggestion)
                if len(options) == 3:
                    break
        self.__autofill_box.update(options[:3])
    
    def nav_autofill(self, event):
        if event.keysym == "Up":
            self.__autofill_box.navigate(1)
        elif event.keysym == "Down":
            self.__autofill_box.navigate(-1)

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

    def on_focus_out_entry_widget(self, event, widget, placeholder_text):
        if isinstance(widget, Entry):
            text = widget.get()
        elif isinstance(widget, Text):
            text = widget.get("1.0", "end-1c") # USED FOR TEXT WIDGETS ONLY
        if len(text) == 0:
            widget.config(fg="gray")
            widget.insert(END, placeholder_text)

class SuggestBox:
    def __init__(self, parent, color='black'):
        self.__p_listbox = Frame(parent, height=3, width=50, highlightbackground="gray", highlightthickness=2)
        self.__p_listbox.pack(anchor='n', fill=X, expand=False, padx=5, pady=5)
        self.__l_opt1 = Label(self.__p_listbox, text='Option 1', fg=color, font=("Helvetica", 10, "bold"))
        self.__l_opt1.grid(column=0, row=0, sticky="w")
        self.__l_opt2 = Label(self.__p_listbox, text='Option 2', fg=color, font=("Helvetica", 10, "bold"))
        self.lighten_foreground_color(self.__l_opt2, color, 0.165)
        self.__l_opt2.grid(column=0, row=1, sticky="w")
        self.__l_opt3 = Label(self.__p_listbox, text='Option 3', fg=color, font=("Helvetica", 10, "bold"))
        self.lighten_foreground_color(self.__l_opt3, color, 0.33)
        self.__l_opt3.grid(column=0, row=2, sticky="w")
        self.labels = [self.__l_opt1, self.__l_opt2, self.__l_opt3]
        self.selected = None
        self.default_label_bg_color = self.__l_opt1.cget('bg')
        self.clear()
    
    def navigate(self, dir):
        if self.selected:
            if dir > 0:
                if self.selected == self.labels[1]:
                    self.select(self.labels[0])
                elif self.selected == self.labels[2]:
                    self.select(self.labels[1])
            elif dir < 0:
                if self.selected == self.labels[0]:
                    self.select(self.labels[1])
                elif self.selected == self.labels[1]:
                    self.select(self.labels[2])
        else:
            self.select(self.labels[0])

    def select(self, label):
        self.deselect()
        if label.cget('text'):
            self.selected = label
            label.config(bg='gold')

    def deselect(self):
        if self.selected:
            self.selected.config(bg=self.default_label_bg_color)
            self.selected = None
    
    def set_label_text(self, label, text):
            label.config(text=text)
    
    def update(self, options):
        # if the first option is empty, it means that no text is entered
        if len(options) == 0 or not options[0]:
            self.clear()
            return
        for i in range(0, 3):
            if i > (len(options) - 1):
                self.set_label_text(self.labels[i], '')
                continue
            self.set_label_text(self.labels[i], options[i])
        
    def clear(self):
        for label in self.labels:
            self.set_label_text(label, '')
        self.deselect()

    
    def lighten_foreground_color(self, label, color, amount):
        '''
        Lightens a hexadecimal color by a given amount and updates the label's background.
        Amount should be between 0 and 1, where 1 means full white.
        '''
        rgb_tuple = label.winfo_rgb(color) # Returns a tuple like (0, 0, 65535)
        hex_color = '#%02x%02x%02x' % (rgb_tuple[0]//256, rgb_tuple[1]//256, rgb_tuple[2]//256)

        if not (0 <= amount <= 1):
            raise ValueError("Amount must be between 0 and 1.")

        # Convert hex to RGB tuple
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Lighten each RGB component
        lightened_rgb = []
        for component in rgb:
            new_component = int(component + (255 - component) * amount)
            lightened_rgb.append(min(255, new_component)) # Ensure value doesn't exceed 255

        # Convert back to hex
        lightened_hex = '#%02x%02x%02x' % tuple(lightened_rgb)
        label.config(fg=lightened_hex)