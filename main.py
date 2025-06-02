import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import fitz
import re

def analyze_pdf(file_path, threshold_rpe=0.30, threshold_riso=1.0):
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

        # === Najdi název spotřebiče ===
        name_match = re.search(r'Název:\s*(.*)', text)
        device_name = name_match.group(1).strip() if name_match else ""

        # === Najdi třídu ochrany ===
        class_match = re.search(r'Třída ochrany:\s*(I{1,2})', text)
        protection_class = class_match.group(1) if class_match else "Neznámá"
        if protection_class == "Neznámá":
            results.append(f"⚠️ {device_id}: Třída ochrany nebyla nalezena nebo je nečitelná!")

        # === RPE kontrola ===
        if protection_class == "II":
            results.append(f"✅ {device_id}: Třída ochrany II – měření Rpe není požadováno.")
        else:
            rpe_match = re.search(r'Rpe:\s*([\d.,]*)\s*Ω', text)
            if rpe_match:
                value_str = rpe_match.group(1).strip()
                if value_str:
                    try:
                        rpe_value = float(value_str.replace(",", "."))
                        if rpe_value > threshold_rpe:
                            results.append(f"⚠️ {device_id}: Rpe = {rpe_value} Ω > {threshold_rpe} Ω (překročeno!)")
                        else:
                            results.append(f"✅ {device_id}: Rpe = {rpe_value} Ω (v normě)")
                    except ValueError:
                        results.append(f"❗ {device_id}: Rpe je ve špatném formátu!")
                else:
                    if "není měření odporu" in text.lower() or "měření odporu není možné" in text.lower():
                        results.append(f"ℹ️ {device_id}: Rpe není uvedeno, ale je uvedeno vysvětlení (v pořádku)")
                    else:
                        results.append(f"⚠️ {device_id}: Rpe není uvedeno a chybí vysvětlení! (nutná kontrola)")
            else:
                results.append(f"❓ {device_id}: Rpe nebylo vůbec nalezeno")

        # === RisoM-PE kontrola ===
        riso_match = re.search(r'RisoM-PE:\s*([>\d.,]+)\s*MΩ', text)
        if riso_match:
            value_str = riso_match.group(1).replace(",", ".").replace(">", "").strip()
            try:
                riso_value = float(value_str)
                if riso_value < threshold_riso:
                    results.append(f"⚠️ {device_id}: RisoM-PE = {riso_value} MΩ < {threshold_riso} MΩ (nedostatečné)")
                else:
                    results.append(f"✅ {device_id}: RisoM-PE = {riso_value} MΩ (v pořádku)")
            except ValueError:
                results.append(f"❗ {device_id}: RisoM-PE má nečitelný formát!")
        else:
            results.append(f"❓ {device_id}: RisoM-PE nebylo nalezeno")

        # === IaltEq kontrola ===
        ialt_match = re.search(r'IaltEq:\s*([\d.,]+)', text)
        if ialt_match:
            try:
                ialt_value = float(ialt_match.group(1).replace(",", "."))
                limit = 3.5 if protection_class == "I" else 0.25
                if ialt_value > limit:
                    results.append(f"⚠️ {device_id}: IaltEq = {ialt_value} mA > {limit} mA (překročeno!)")
                else:
                    results.append(f"✅ {device_id}: IaltEq = {ialt_value} mA (v normě)")
            except ValueError:
                results.append(f"❗ {device_id}: IaltEq má nečitelný formát!")
        else:
            results.append(f"❓ {device_id}: IaltEq nebyl nalezen")

        # === IdirTouch a reverzní kontrola ===
        idir_match = re.search(r'IdirTouch:\s*([\d.,]+)', text)
        idir_rev_match = re.search(r'reverzní:\s*([\d.,]+)', text)

        idir_reported = False
        for label, match in [('IdirTouch', idir_match), ('IdirTouch (reverzní)', idir_rev_match)]:
            if match:
                try:
                    value = float(match.group(1).replace(",", "."))
                    limit = 0.5 if protection_class == "I" else 0.25
                    if value > limit:
                        results.append(f"⚠️ {device_id}: {label} = {value} mA > {limit} mA (překročeno!)")
                    else:
                        results.append(f"✅ {device_id}: {label} = {value} mA (v normě)")
                    idir_reported = True
                except ValueError:
                    results.append(f"❗ {device_id}: {label} má nečitelný formát!")
                    idir_reported = True

        if not idir_reported:
            if protection_class == "II":
                results.append(f"⚠️ {device_id}: Chybí měření IdirTouch")
            elif protection_class == "I":
                results.append(f"✅ {device_id}: IdirTouch – neměřeno")

        # === SELV/PELV kontrola pro síťový adaptér 5V ===
        if device_name.lower().startswith("síťový adaptér 5v"):
            selv_match = re.search(r'Napětí zdroje SELV/PELV\s*U:\s*([\d.,]+)', text)
            if selv_match:
                try:
                    voltage = float(selv_match.group(1).replace(",", "."))
                    if 4.75 <= voltage <= 5.25:
                        results.append(f"✅ {device_id}: Napětí SELV/PELV = {voltage} V (v pořádku)")
                    else:
                        results.append(f"⚠️ {device_id}: Napětí SELV/PELV = {voltage} V (mimo rozsah 4,75–5,25 V)")
                except ValueError:
                    results.append(f"❗ {device_id}: Napětí SELV/PELV má nečitelný formát!")
            else:
                results.append(f"⚠️ {device_id}: Napětí SELV/PELV nebylo nalezeno")

        results.append("")  # Oddělovač

    doc.close()
    return results

def search_text():
    output_text.tag_remove("highlight", "1.0", tk.END)
    search_term = search_entry.get().strip()
    if not search_term:
        return

    output_text.config(state="normal")
    idx = "1.0"
    first_found_idx = None

    # Použij regulární výraz pro celé slovo
    pattern = r'\y' + re.escape(search_term) + r'\y'

    while True:
        idx = output_text.search(pattern, idx, nocase=True, stopindex=tk.END, regexp=True)
        if not idx:
            break
        end_idx = f"{idx}+{len(search_term)}c"
        output_text.tag_add("highlight", idx, end_idx)
        if not first_found_idx:
            first_found_idx = idx
        idx = end_idx

    if first_found_idx:
        output_text.see(first_found_idx)
    else:
        messagebox.showinfo("Nenalezeno", f"Text '{search_term}' nebyl nalezen.")

    output_text.config(state="disabled")



def open_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF soubory", "*.pdf")])
    if not file_path:
        return

    try:
        output_text.config(state="normal")
        output_text.delete("1.0", tk.END)
        results = analyze_pdf(file_path)
        for line in results:
            output_text.insert(tk.END, line + "\n")
        output_text.config(state="disabled")
        messagebox.showinfo("Hotovo", "Analýza dokončena.")
    except Exception as e:
        messagebox.showerror("Chyba", f"Nastala chyba při zpracování PDF:\n{str(e)}")

# === GUI ===
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Kontrola spotřebičů v PDF")
    root.geometry("800x600")

    label = tk.Label(root, text="Vyber PDF soubor pro kontrolu měřených hodnot:")
    label.pack(pady=10)

    btn = tk.Button(root, text="📄 Vybrat PDF", command=open_pdf)
    btn.pack(pady=5)

    # Hledání
    search_frame = tk.Frame(root)
    search_frame.pack(pady=5)

    search_entry = tk.Entry(search_frame, width=40)
    search_entry.pack(side=tk.LEFT, padx=5)

    search_button = tk.Button(search_frame, text="🔍 Hledat", command=search_text)
    search_button.pack(side=tk.LEFT)

    # Výstup
    output_text = scrolledtext.ScrolledText(root, width=90, height=25)
    output_text.pack(padx=10, pady=10)
    output_text.config(state="disabled")
    output_text.tag_config("highlight", background="yellow", foreground="black")

    root.mainloop()
