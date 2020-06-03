import tkinter as tk
import tkinter.font as font
from certtools import x509Cert


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("PyCertTools")
        self.master.iconbitmap("pycerttools.ico")
        self.pack()
        self.create_widgets()
        self.create_context_menu()
        self.create_commands()

    def create_widgets(self):
        btn_font = font.Font(size=14)
        lbl_font = font.Font(size=20, weight="bold")
        self.lbl_input = tk.Label(master=self, text='Cert Text', font=lbl_font)
        self.lbl_input.pack()
        self.txt_input = tk.Text(master=self)
        self.txt_input.pack()
        self.btn_input = tk.Button(master=self, text='parse', font=btn_font)
        self.btn_input.pack(side=tk.LEFT, padx=50, pady=10)
        self.btn_json = tk.Button(master=self, text='json', font=btn_font)
        self.btn_json.pack(side=tk.LEFT, padx=20, pady=10)
        self.btn_clear = tk.Button(master=self, text='clear', font=btn_font)
        self.btn_clear.pack(side=tk.RIGHT, padx=50, pady=10)

    def create_context_menu(self):
        self.popup_menu = tk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Cut",
                                    command=self.cut)
        self.popup_menu.add_command(label="Copy",
                                    command=self.copy)
        self.popup_menu.add_command(label="Paste",
                                    command=self.paste)
        self.popup_menu.add_command(label="Select All",
                                    command=self.select_all)

    def create_commands(self):
        self.btn_clear.bind('<Button-1>', self.clear)
        self.btn_input.bind('<Button-1>', self.parse_cert)
        self.btn_json.bind('<Button-1>', self.json_cert)
        self.txt_input.bind("<Button-3>", self.popup)
        self.master.bind("<Control-a>", self.select_all)
        self.master.bind("<Return>", self.parse_cert)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def clear(self, event=None):
        self.select_all()
        self.txt_input.delete("1.0", tk.END)

    def copy(self):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.txt_input.selection_get())

    def cut(self):
        self.copy()
        self.txt_input.delete("sel.first", "sel.last")

    def select_all(self, event=None):
        self.txt_input.tag_remove(tk.SEL, "1.0", tk.END)
        self.txt_input.tag_add(tk.SEL, "1.0", "end-1c")
        self.txt_input.mark_set(tk.INSERT, "1.0")
        self.txt_input.see(tk.INSERT)

    def paste(self):
        text = self.master.selection_get(selection='CLIPBOARD')
        try:
            self.txt_input.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        self.txt_input.insert('insert', text)

    def parse_cert(self, event):
        print(event)
        data = self.txt_input.get(1.0, tk.END)
        cert = x509Cert(data)
        self.txt_input.delete(1.0, tk.END)
        self.txt_input.insert(1.0, cert.print())

    def json_cert(self, even):
        data = self.txt_input.get(1.0, tk.END)
        cert = x509Cert(data)
        self.txt_input.delete(1.0, tk.END)
        self.txt_input.insert(1.0, cert.to_json())

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
