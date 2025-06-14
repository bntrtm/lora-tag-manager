from tkinter import Entry, END



# TAG ENTRY LOGIC

def on_text_change(event, win):
    entry = win._Window__txt_tag_entry
    #text = entry.get("1.0", "end-1c") # THIS WAS FOR TEXT OBJECTS, not for entries

    text = entry.get().replace(",", "")
    entry.delete(0, "end")
    add_new_tag(win, text)
    return "break"
    return None

def add_new_tag(win, tag):
    caption_field = win._Window__caption_txt_field
    caption_field.insert(END, f"{tag}, ")
    print(f'+TAG: "{tag}"->{win.directory}')
    win.add_new_tagbox(win._Window__p_tag_container, tag)