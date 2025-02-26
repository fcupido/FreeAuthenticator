import pyotp
import time
import tkinter as tk

def read_secret_keys(file_path):
    secret_keys = []
    current_entry = {}

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('Name:'):
                if current_entry:
                    secret_keys.append(current_entry)
                current_entry = {'name': line.split(': ')[1].strip()}
            elif line.startswith('Secret:'):
                current_entry['secret'] = line.split(': ')[1].strip()
            elif line.startswith('Issuer:'):
                current_entry['issuer'] = line.split(': ')[1].strip()
            elif line.startswith('Type:'):
                current_entry['type'] = line.split(': ')[1].strip()

        if current_entry:
            secret_keys.append(current_entry)

    return secret_keys

def generate_otp(secret_key):
    totp = pyotp.TOTP(secret_key)
    return totp.now()

def copy_to_clipboard(otp):
    root.clipboard_clear()
    root.clipboard_append(otp)

def update_otps():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    for i, key in enumerate(secret_keys):
        otp = generate_otp(key['secret'])
        entry_frame = tk.Frame(scrollable_frame, bg='white', bd=1, relief='solid')
        entry_frame.grid(row=i // 4, column=i % 4, padx=10, pady=10, sticky='nsew')

        name_label = tk.Label(entry_frame, text=key['name'], font=('Helvetica', 14, 'bold'), bg='white')
        name_label.pack(anchor='w', padx=10, pady=5)

        issuer_label = tk.Label(entry_frame, text=f"Issuer: {key.get('issuer', 'N/A')}", font=('Helvetica', 10), bg='white')
        issuer_label.pack(anchor='w', padx=10)

        type_label = tk.Label(entry_frame, text=f"Type: {key['type']}", font=('Helvetica', 10), bg='white')
        type_label.pack(anchor='w', padx=10)

        otp_label = tk.Label(entry_frame, text=f"OTP: {otp}", font=('Helvetica', 12), bg='white', fg='blue')
        otp_label.pack(anchor='w', padx=10, pady=5)

        otp_button = tk.Button(entry_frame, text="Copy OTP", command=lambda otp=otp: copy_to_clipboard(otp), bg='blue', fg='white')
        otp_button.pack(anchor='e', padx=10, pady=5)

    # Schedule the next update aligned with the minute
    now = time.time()
    next_update = (30 - (now % 30)) * 1000
    root.after(int(next_update), update_otps)

def update_timer():
    now = time.time()
    seconds_until_next_update = 30 - int(now % 30)
    root.title(f"OTP Manager: Next update in: {seconds_until_next_update} seconds")
    root.after(1000, update_timer)

def create_gui(secret_keys):
    global root, scrollable_frame
    root = tk.Tk()
    root.title("OTP Manager")
    root.geometry("1600x600")
    root.configure(bg='white')

    canvas = tk.Canvas(root, bg='white')
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='white')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    update_timer()
    update_otps()
    root.mainloop()

if __name__ == '__main__':
    secret_keys = read_secret_keys('secrets.txt')
    create_gui(secret_keys)
