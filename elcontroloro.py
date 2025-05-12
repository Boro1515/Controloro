import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import fitz  # PyMuPDF
import re

def analyze_pdf(file_path, threshold=30.0):
    results = []
    doc = fitz.open(file_path)

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text")
        lines = text.splitlines()

        # === Najdi první číslo na stránce jako ID ===
        device_id = f"N:{page_number}"
        for line in lines:
            if line.strip().isdigit():
                device_id = line.strip()
                break

        # === Najdi třídu ochrany ===
        class_match = re.search(r'Třída ochrany:\s*(I{1,2})', text)
        protection_class = class_match.group(1) if class_match else "Neznámá"

        # === Pokud třída ochrany je II, Rpe neřešíme ===
        if protection_class == "II":
            results.append(f"✅ {device_id}: Třída ochrany II – měření Rpe není požadováno.")
        else:
            # === Najdi Rpe hodnotu ===
            rpe_match = re.search(r'Rpe:\s*([\d.,]*)\s*Ω', text)
            if rpe_match:
                value_str = rpe_match.group(1).strip()
                if value_str:
                    try:
                        rpe_value = float(value_str.replace(",", "."))
                        if rpe_value > threshold:
                            results.append(f"⚠️ {device_id}: Rpe = {rpe_value} Ω > {threshold} Ω (překročeno!)")
                        else:
                            results.append(f"✅ {device_id}: Rpe = {rpe_value} Ω (v normě)")
                    except ValueError:
                        results.append(f"❗ {device_id}: Rpe je ve špatném formátu!")
                else:
                    if "není měření odporu" in text.lower() or "měření odporu není možné" in text.lower():
                        results.append(f"ℹ️ {device_id}: Rpe není uvedeno, ale je uvedeno vysvětlení (v pořádku)")
                    else:
                        results.append(f"❗ {device_id}: Rpe není uvedeno a chybí vysvětlení! (nutná kontrola)")
            else:
                results.append(f"❓ {device_id}: Rpe nebylo vůbec nalezeno")

    doc.close()
    return results

def open_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF soubory", "*.pdf")])
    if not file_path:
        return

    try:
        output_text.delete("1.0", tk.END)
        results = analyze_pdf(file_path)
        for line in results:
            output_text.insert(tk.END, line + "\n")
        messagebox.showinfo("Hotovo", "Analýza dokončena.")
    except Exception as e:
        messagebox.showerror("Chyba", f"Nastala chyba při zpracování PDF:\n{str(e)}")

# === GUI ===
root = tk.Tk()
root.title("Kontrola Rpe v PDF")
root.geometry("700x500")

label = tk.Label(root, text="Vyber PDF soubor pro kontrolu hodnoty Rpe:")
label.pack(pady=10)

btn = tk.Button(root, text="📄 Vybrat PDF", command=open_pdf)
btn.pack(pady=5)

output_text = scrolledtext.ScrolledText(root, width=80, height=20)
output_text.pack(padx=10, pady=10)

root.mainloop()
