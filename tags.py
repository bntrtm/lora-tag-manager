from tkinter import Button, LEFT, END, DISABLED

class TagBox:
    def __init__(self, win, parent, tag):
        self.win = win
        self.parent = parent
        self.tag_text = tag
        self.is_trigger = False
        if self.win is not None:
            if self.win.lora_in_training is not None:    
                if tag == self.win.lora_in_training.trigger_word:
                    self.is_trigger = True
        print(f'Generating button for tag: {tag}')
        self.bt = Button(parent, text=tag, command=self.devise_action)
        if self.is_trigger:
            self.bt.config(text=f'{tag}🔒', bg='gold', state=DISABLED)

    def devise_action(self):
        if self.is_trigger is True:
            return
        match self.win.tag_click_mode.get():
            case "Delete":
                self.delete()
            case "Delete_All":
                print(f'Removing tag "{self.tag_text}" from all .txt files in dataset {self.win.directory}')
                self.win.lora_in_training.remove_tag_from_image_caption(self.tag_text, all=True)
            case "Apply_All":
                print(f'Applying tag "{self.tag_text}" to all .txt files in dataset {self.win.directory}')
                self.win.lora_in_training.add_tag_to_image_caption(self.tag_text, all=True)
            case _:
                raise ValueError("only 'Delete' and 'Apply_All' are acceptable actions")
        self.win.refresh()
    
    def delete(self):
        text = self.bt.cget("text")
        print(f'deleting tag in caption: {self.tag_text}')
        tags = self.win._TrainLoraWin__caption_txt_field.get("1.0", "end-1c")
        self.win.lora_in_training.remove_tag_from_image_caption(self.tag_text, png_path=self.win.get_png_path())
        self.win.refresh()
        self.destroy()
    
    def destroy(self):
        self.bt.destroy()
