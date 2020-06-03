import tkinter as tk
from certtools import x509Cert


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.create_context_menu()
        self.create_commands()

    def create_widgets(self):
        self.lbl_input = tk.Label(master=self, text='Cert Text')
        self.lbl_input.pack()
        self.txt_input = tk.Text(master=self)
        self.txt_input.pack()
        self.btn_input = tk.Button(master=self, text='parse')
        self.btn_input.pack()

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
        self.btn_input.bind('<Button-1>', self.parse_cert)
        self.txt_input.bind("<Button-3>", self.popup)
        self.master.bind("<Control-a>", self.select_all)

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

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
        self.txt_input.delete("sel.first", "sel.last")
        self.txt_input.insert('insert', text)

    def parse_cert(self, event):
        print(event)
        data = self.txt_input.get(1.0, tk.END)
        cert = x509Cert(data)
        self.txt_input.delete(1.0, tk.END)
        self.txt_input.insert(1.0, cert.print())


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
