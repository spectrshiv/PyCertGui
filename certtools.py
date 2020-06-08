from OpenSSL import crypto
import sys
from pprint import pprint, pformat
import atexit
from jinja2 import Template
from json import dumps


class x509Cert:
    def __init__(self, certdata):
        self.x509cert = crypto.load_certificate(crypto.FILETYPE_PEM, certdata)
        self.subject = self.decode_x509name(self.x509cert.get_subject())
        self.extensions = self.get_x509extensions()
        self.issuer = self.decode_x509name(self.x509cert.get_issuer())
        self.notbefore = self.x509cert.get_notBefore()
        self.notafter = self.x509cert.get_notAfter()
        self.algorithm = self.x509cert.get_signature_algorithm()
        self.expired = self.x509cert.has_expired()
        self.serial = self.x509cert.get_serial_number()

    def get_x509extensions(self):
        ret = []
        extension_count = range(self.x509cert.get_extension_count())
        for i in extension_count:
            extension = self.x509cert.get_extension(i)
            ret.append([extension.get_short_name().decode(), extension.__str__().replace('\n', ''), extension.get_critical()])
        return ret

    def to_json(self):

        json = {"Subject": {x: y for x, y in self.subject},
                "Issuer": {x: y for x, y in self.issuer},
                "Extensions": {x: {"Data": y, "Critical": bool(z)} for x, y, z in self.extensions},
                "Not_Before": self.timeparse(self.notbefore.decode()),
                "Not_After": self.timeparse(self.notafter.decode()),
                "Expired": self.expired,
                "Signature_Algorithm": self.algorithm.decode(),
                "Serial_Number": self.serial}
        if "subjectAltName" in json["Extensions"].keys():
            json["Subject_Alt_Name"] = json["Extensions"].pop("subjectAltName")
            data = json["Subject_Alt_Name"].pop("Data").split(',')
            try:
                for i in data:
                    k, v = i.split(':')
                    k = k.strip()
                    v = v.strip()
                    if k not in json["Subject_Alt_Name"].keys():
                        json["Subject_Alt_Name"][k] = []
                    json["Subject_Alt_Name"][k].append(v)
            except:
                print(data)
                input('stopped')
        return json

    def to_json_pretty(self):
        return pformat(self.to_json())

    def print(self):
        template = """Subject: 
{% for key, value in x509json.Subject.items() %}\t{{ key }}: {{ value }} \n{% endfor %}
Issuer:
{% for key, value in x509json.Issuer.items() %}\t{{ key }}: {{ value }} \n{% endfor %}
Extensions:
{% for key, value in x509json.Extensions.items() %}\t{{ key }}: {% for k, v in value.items() %}\t{{ k }}: {{ v }}\n{% endfor %} {% endfor %}
{% if "Subject_Alt_Name" in x509json.keys() %}Subject Alt Names:\n{% for k,v in x509json.Subject_Alt_Name.items() %}\t{{ k }}:\n{% if v is iterable and v is not string %}{% for x in v %}\t\t{{ x }}\n{% endfor %}{% else %}\t\t{{ v }}\n{% endif %}{% endfor %}{% endif %} 
Not Before: {{ x509json.Not_Before }}
Not After: {{ x509json.Not_After }}
Expired: {{ x509json.Expired }}
Signature Algorithm: {{ x509json.Signature_Algorithm }}
Serial Number: {{ x509json.Serial_Number }}
        """
        x509_template = Template(template)
        return x509_template.render(x509json=self.to_json())

    @staticmethod
    def decode_x509name(x509name):
        ret = []
        for k, v in x509name.get_components():
            ret.append([k.decode(), v.decode()])
        return ret

    @staticmethod
    def critical(critical):
        if critical:
            return "Critical"
        else:
            return "Normal"

    @staticmethod
    def timeparse(timestamp):
        year = timestamp[0:4]
        month = timestamp[4:6]
        day = timestamp[6:8]
        hour = timestamp[8:10]
        minute = timestamp[10:12]
        second = timestamp[12:14]
        return f'{hour}:{minute}:{second}z {month}-{day}-{year}'


def cert_from_clipboard():
    import tkinter
    tk = tkinter.Tk()

    @atexit.register
    def tk_cleanup():
        tk.destroy()

    tk.withdraw()
    data = tk.clipboard_get()
    return x509Cert(data)


def cert_from_file(file):
    with open(file, 'rb') as data:
        _cert = x509Cert(data.read())
    return _cert


help = """ certtools.py usage
------------------
From Clipboard:
    Run with no command line arguments, certtools will parse the copied base64 certificate from 
    the clipboard and display it as text. If no suitable data is found in the clipboard, a prompt 
    will be presented to select a file path.
    
Command Line Arguments:
    certtools.py [cert path] [json|text]
"""

if __name__ == '__main__':
    try:
        if sys.argv[1] in ['h', 'help', '-h', '?']:
            print(help)
            sys.exit(0)
        cert = cert_from_file(sys.argv[1])
    except IndexError:
        try:
            cert = cert_from_clipboard()
        except crypto.Error:
            try:
                certfile = input("Certificate location: ")
                cert = cert_from_file(certfile)
            except FileNotFoundError:
                print("File not found. Please try again.")
                sys.exit(1)
            except FileExistsError:
                print("File not found. Please try again.")
                sys.exit(1)
            except crypto.Error:
                print("Cert file not valid. Must be base64 encoded pem")
                sys.exit(1)
    try:
        if sys.argv[2] == "json":
            print(dumps(cert.to_json()))
        elif sys.argv[2] == "text":
            print(cert.print())
    except IndexError:
        print(cert.print())
    sys.exit(0)
