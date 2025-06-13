from tkinter import Tk, BOTH, X, Y, LEFT, RIGHT, TOP, END, NW, SW, S, Label, Frame, Button, Text, filedialog
from PIL import Image, ImageTk

class Window:
    def __init__(self, gui_width, gui_height):
        self.__root = Tk()
        self.__root.title("LoRA Training Text Editor")
        self.__is_running = False
        self.__root.protocol(name="WM_DELETE_WINDOW", func=self.close)
        
        # set up master pane
        self.__p_master = Frame(self.__root, height=gui_height, width=gui_width)
        self.__p_master.pack(fill=BOTH, expand=True, padx=5, pady=5)
        # SET STRICT SIZE:
        ## self.__p_master.pack_propagate(0)

        # set up persistent info pane
        self.__p_info = Frame(self.__p_master, height=1, width=gui_width, highlightbackground="gray", highlightthickness=2)
        self.__p_info.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)
        self.directory = ""
        self.__bt_load_dir = Button(self.__p_info, text=f"Load", command=self.load_directory)
        self.__bt_load_dir.pack(side=LEFT)
        self.__l_info = Label(self.__p_info, text=f"Working under directory: {self.directory}")
        self.__l_info.pack(side=LEFT)

        # set up pane housing main elements
        self.__p_hrzbox = Frame(self.__p_master)
        self.__p_hrzbox.pack(side=TOP, fill=BOTH, expand=True)
        #self.__p_hrzbox.pack_propagate(0)
            # set up text editor pane
        self.__p_editor = Frame(self.__p_hrzbox, height=gui_height, highlightbackground="gray", highlightthickness=2)
        self.__p_editor.pack(anchor="w", side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        self.__l_editor = Label(self.__p_editor, text = "Prompt Text Editor")
        self.__l_editor.pack()
        self.__txt_field = Text(self.__p_editor, height=9, width=50)
        self.__txt_field.insert(END, "prompts listed here")
        self.__txt_field.pack()
        #self.__txt_field.place(relheight=0.9, relwidth=0.9, relx=2, rely=2)
                # set up promp-by-prompt pane
        self.__p_prompter = Frame(self.__p_editor)
        self.__p_prompter.pack(side=LEFT)
        self.__txt_prompt_entry = Text(self.__p_prompter, height=1, width=50)
        self.__txt_prompt_entry.pack()
        self.__txt_prompt_entry.insert(END, "prompt goes here")

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