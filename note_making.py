import tkinter as tk
from tkinter import scrolledtext, Canvas, Frame, Scrollbar, Text
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["notes_db"]
collection = db["notes"]

def open_insert_window():
    insert_window = tk.Toplevel(root)
    insert_window.title("Insert Note")
    insert_window.config(bg='#FA8072', pady=10, padx=10)
    
    tk.Label(insert_window, text="Title", font="Helvetica 15 bold", bg="#FA8072", fg="white").pack()
    new_title_entry = tk.Entry(insert_window, width=40)
    new_title_entry.pack()
    
    tk.Label(insert_window, text="Note", font="Helvetica 15 bold", bg="#FA8072", fg="white").pack()
    new_note_text = scrolledtext.ScrolledText(insert_window, width=40, height=5, wrap="word")
    new_note_text.pack()
    
    def save_new_note():
        title = new_title_entry.get()
        note = new_note_text.get("1.0", tk.END).strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if title and note:
            collection.insert_one({"title": title, "note": note, "timestamp": timestamp})
            insert_window.destroy()
            display_notes()
    
    tk.Button(insert_window, text="Save Note", command=save_new_note, bg='#87CEEB').pack()

def delete_note(note_id):
    collection.delete_one({"_id": ObjectId(note_id)})
    display_notes()

def update_note(note_id, old_title, old_note):
    def submit_update():
        new_title = title_update_entry.get()
        new_note = note_update_text.get("1.0", tk.END).strip()
        
        if new_title and new_note:
            collection.update_one({"_id": ObjectId(note_id)}, {"$set": {"title": new_title, "note": new_note, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
            update_window.destroy()
            display_notes()
    
    update_window = tk.Toplevel(root)
    update_window.title("Update Note")
    update_window.config(bg="#FA8072", padx=10, pady=10)
    tk.Label(update_window, text="Title", font="Helvetica 15 bold", bg="#FA8072", fg="white").pack()
    title_update_entry = tk.Entry(update_window, width=40)
    title_update_entry.insert(0, old_title)
    title_update_entry.pack()
    
    tk.Label(update_window, text="Note", font="Helvetica 15 bold", bg="#FA8072", fg="white").pack()
    note_update_text = scrolledtext.ScrolledText(update_window, width=40, height=5, wrap="word")
    note_update_text.insert("1.0", old_note)
    note_update_text.pack()
    
    tk.Button(update_window, text="Update", command=submit_update, bg='#87CEEB').pack()

def display_notes():
    for widget in notes_container.winfo_children():
        widget.destroy()
    for note in collection.find().sort("timestamp", -1):
        if not note:
            print("hello")
        frame = tk.Frame(notes_container)
        frame.pack(fill="x", padx=5, pady=2)
        
        text_frame = tk.Frame(frame)
        text_frame.pack(side="left", fill="x", expand=True)
        
        note_text_widget = Text(text_frame, wrap="word", height=6, width=50)
        note_text_widget.insert("1.0", f"Title: {note['title']}\nNote: {note['note']}\nTime: {note['timestamp']}")
        note_text_widget.config(state="disabled")
        note_text_widget.pack(fill="x", expand=True)
        
        button_frame = tk.Frame(frame)
        button_frame.pack(side="right")
        
        delete_btn = tk.Button(button_frame, text="Delete", command=lambda nid=note['_id']: delete_note(str(nid)), height=2, width=12, bg='#E9967A')
        delete_btn.pack()
        
        update_btn = tk.Button(button_frame, text="Update", command=lambda nid=note['_id'], t=note['title'], n=note['note']: update_note(str(nid), t, n), height=2, width=12, bg='#87CEEB')
        update_btn.pack()
        
    
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# GUI Setup
root = tk.Tk()
root.title("Note Maker")
root.geometry("600x550")
root.config(padx=30, pady=30, bg='#FFA07A')



tk.Label(root, text="Saved Notes", font="Helvetica 15 bold", bg="#FFA07A", fg="white").pack()

# Scrollable Frame Setup
frame_container = tk.Frame(root)
frame_container.pack(fill="both", expand=True)

canvas = Canvas(frame_container)
v_scrollbar = Scrollbar(frame_container, orient="vertical", command=canvas.yview)

notes_container = Frame(canvas)

notes_container.bind(
    "<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=notes_container, anchor="nw")
canvas.configure(yscrollcommand=v_scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
v_scrollbar.pack(side="right", fill="y")

tk.Button(root, text="+", command=open_insert_window, height=2, width=4).pack(side='right')

display_notes()
root.mainloop()