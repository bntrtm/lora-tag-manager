from tkinter import Button, LEFT, END

class TagBox():
    def __init__(self, win, parent, tag):
        self.win = win
        self.parent = parent
        self.tag_text = tag
        print(f'Generating button for tag: {tag}')
        self.bt = Button(parent, text=tag, command=self.devise_action)
        #self.bt.pack(side=LEFT)

    def devise_action(self):
        match self.win.tag_click_mode.get():
            case "Delete":
                self.delete()
            case "Apply_All":
                self.proliferate_tag()
            case _:
                raise ValueError("only 'Delete' and 'Apply_All' are acceptable actions")
                print(self.win.tag_click_mode.get())
                return
    
    def delete(self):
        text = self.bt.cget("text")
        print(f'deleting tag in caption: {self.tag_text}')
        tags = self.win._Window__caption_txt_field.get("1.0", "end-1c")
        replaced = tags.replace(f"{self.tag_text}, ", "")
        self.win._Window__caption_txt_field.delete("1.0", "end")
        self.win._Window__caption_txt_field.insert(END, replaced)
        self.bt.destroy()
    
    def proliferate_tag(self):
        print(f'Applying tag "{self.tag_text}" to all .txt files in dataset {self.win.directory}')
        return