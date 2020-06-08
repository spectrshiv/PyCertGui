import tkinter as tk
from tkinter import filedialog
from tkaddons import XYScrolledText
import tkinter.font as font
from certtools import x509Cert
from json import dumps
import OpenSSL.crypto

SMALL = {"Text": {"X": 51, "Y": 10}, "Window": {"X": 470, "Y": 260}}
MEDIUM = {"Text": {"X": 70, "Y": 25}, "Window": {"X": 581, "Y": 500}}
LARGE = {"Text": {"X": 100, "Y": 40}, "Window": {"X": 821, "Y": 741}}


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("PyCertTools")
        self.master.iconbitmap("pycerttools.ico")
        self.size = MEDIUM
        self.master.minsize(self.size["Window"]["X"], self.size["Window"]["Y"])
        self.pack()
        self.create_widgets()
        self.create_context_menu()
        self.create_menubar()
        self.create_commands()
        self.cert_buffer = ""

    def create_widgets(self):
        btn_font = font.Font(size=12)
        lbl_font = font.Font(size=14, weight="bold")
        self.lbl_input = tk.Label(master=self, text='Cert Text', font=lbl_font)
        self.lbl_input.pack()
        self.txt_input = XYScrolledText(master=self, width=self.size["Text"]["X"],
                                        height=self.size["Text"]["Y"], wrap=tk.NONE)
        self.txt_input.pack()
        self.btn_input = tk.Button(master=self, text='parse', font=btn_font)
        self.btn_input.pack(side=tk.LEFT, padx=50, pady=10)
        self.btn_json = tk.Button(master=self, text='json', font=btn_font)
        self.btn_json.pack(side=tk.LEFT, padx=20, pady=10)
        self.btn_clear = tk.Button(master=self, text='clear', font=btn_font)
        self.btn_clear.pack(side=tk.RIGHT, padx=50, pady=10)
        self.btn_open = tk.Button(master=self, text='open', font=btn_font)
        self.btn_open.pack(side=tk.RIGHT, padx=20, pady=10)

    def create_menubar(self):
        self.menu_bar = tk.Menu(self.master)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Exit", command=exit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.master.config(menu=self.menu_bar)

        self.pref_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.ui_menu = tk.Menu(self.pref_menu)
        self.ui_menu.add_command(label="Small", command=lambda: self.ui_size(SMALL))
        self.ui_menu.add_command(label="Medium", command=lambda: self.ui_size(MEDIUM))
        self.ui_menu.add_command(label="Large", command=lambda: self.ui_size(LARGE))
        self.pref_menu.add_cascade(label="Interface Size", menu=self.ui_menu)
        self.menu_bar.add_cascade(label="preferences", menu=self.pref_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="License", command=self.license)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

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
        self.btn_open.bind('<Button-1>', self.open_file)
        self.txt_input.bind("<Button-3>", self.popup)
        self.master.bind("<Control-a>", self.select_all)
        self.master.bind("<Return>", self.parse_cert)

    def open_file(self, event=None):
        print(event)
        filename = filedialog.askopenfilename(initialdir="./",
                                              title="Select Certificate",
                                              filetypes=[("all files", "*.*")])
        if filename == '':
            return "break"
        with open(filename, "r") as certfile:
            self.clear("clear() spawned from open_file()")
            self.txt_input.insert("1.0", certfile.read())
        print(filename)
        return "break"

    def popup(self, event=None):
        print(event)
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            self.popup_menu.grab_release()

    def ui_size(self, size):
        self.size = size
        self.master.minsize(self.size["Window"]["X"], self.size["Window"]["Y"])
        self.txt_input.config(width=self.size["Text"]["X"], height=self.size["Text"]["Y"])

    def clear(self, event=None):
        print(event)
        self.cert_buffer = ""
        self.select_all("select_all() spawned from clear()")
        self.txt_input.delete("1.0", tk.END)

    def copy(self, event=None):
        print(event)
        self.master.clipboard_clear()
        self.master.clipboard_append(self.txt_input.selection_get())

    def cut(self, event=None):
        print(event)
        self.copy("copy() spawned from cut()")
        self.txt_input.delete("sel.first", "sel.last")

    def select_all(self, event=None):
        print(event)
        self.txt_input.tag_remove(tk.SEL, "1.0", tk.END)
        self.txt_input.tag_add(tk.SEL, "1.0", "end-1c")
        self.txt_input.mark_set(tk.INSERT, "1.0")
        self.txt_input.see(tk.INSERT)

    def paste(self, event=None):
        print(event)
        text = self.master.selection_get(selection='CLIPBOARD')
        try:
            self.txt_input.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        self.txt_input.insert('insert', text)

    def prepare_cert(self, event=None):
        print(event)
        try:
            data = self.txt_input.get(1.0, tk.END)
            if self.cert_buffer == "" or "BEGIN CERTIFICATE" in self.txt_input.get('1.0', tk.END).splitlines()[0]:
                self.cert_buffer = data
                cert = x509Cert(data)
            else:
                cert = x509Cert(self.cert_buffer)
            self.txt_input.delete(1.0, tk.END)
            return cert
        except OpenSSL.crypto.Error:
            return "Error"

    def parse_cert(self, event=None):
        if self.prepare_cert(event) == "Error":
            self.clear("clear() spawned by parse_cert()")
            self.txt_input.insert(1.0, "There was a problem parsing your certiicate. Please try again.")
            print("Certificate parsing error.")
            return
        self.txt_input.insert(1.0, self.prepare_cert(event).print())

    def json_cert(self, event=None):
        if self.prepare_cert(event) == "Error":
            self.clear("clear() spawned by json_cert()")
            self.txt_input.insert(1.0, "There was a problem parsing your certiicate. Please try again.")
            print("Certificate parsing error.")
            return
        data = dumps(self.prepare_cert(event).to_json())
        self.txt_input.insert(1.0, data)

    def license(self):
        import webbrowser
        try:
            with open("LICENSE", "r") as file:
                _license = file.read()
        except FileNotFoundError:
            _license = "Someone's been bad and removed my license. I'm not mad, I'm just disappointed."

        link_font = font.Font(size=8)
        self.win_license = tk.Tk()
        self.win_license.title("PyCertTools License")
        self.win_license.iconbitmap("pycerttools.ico")
        self.msg_license = tk.Message(self.win_license, text=_license)

        self.msg_license.pack()
        self.lbl_jinjalicense = tk.Label(master=self.win_license, text="Jinja2 License", font=link_font, fg="blue")
        self.lbl_jinjalicense.pack()
        self.lbl_pyopenssllicense = tk.Label(master=self.win_license, text="PyOpenSSL License",
                                             font=link_font, fg="blue")
        self.lbl_pyopenssllicense.pack()
        self.lbl_jinjalicense.bind('<Button-1>', lambda x: webbrowser.open("https://palletsprojects.com/license/"))
        self.lbl_pyopenssllicense.bind('<Button-1>', lambda x: webbrowser.open("https://raw.githubusercontent.com"
                                                                               "/pyca/pyopenssl/master/LICENSE"))


def run():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()


if __name__ == '__main__':
    run()
