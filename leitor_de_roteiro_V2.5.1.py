import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import re

def execute_script_from_file(file_path, selected_steps, log_widget):
    try:
        with open(file_path, 'r') as file:
            steps = file.readlines()

        url = None
        for line in steps:
            if line.startswith("Link:"):
                url = line.strip().replace("Link:", "").strip()
                break
        
        if not url or not re.match(r'^https?://', url):
            messagebox.showerror("Erro", "Nenhuma URL válida encontrada no arquivo.")
            return

        driver = webdriver.Chrome()
        driver.get(url)
        log_widget.insert(tk.END, f"URL carregada: {url}\n")
        log_widget.see(tk.END)
        time.sleep(2)

        for i, step in enumerate(steps[1:]):
            if selected_steps[i].get():
                step = step.strip()
                log_widget.insert(tk.END, f"Executando passo {i+1}: {step}\n")
                log_widget.see(tk.END)

                if step.startswith("Clique:"):
                    try:
                        tag = extract_between(step, "Elemento ", " com ID")
                        element_id = extract_between(step, "ID='", "', classe")
                        element_class = extract_between(step, "classe='", "', texto")
                        text = extract_between(step, "texto='", "'")

                        element = None
                        if element_id:
                            element = driver.find_element(By.ID, element_id)
                        elif text.strip():
                            element = driver.find_element(By.XPATH, f"//{tag}[contains(text(), '{text.strip()}')]")
                        elif element_class:
                            element = driver.find_element(By.CLASS_NAME, element_class.split()[0])

                        if element:
                            ActionChains(driver).move_to_element(element).click(element).perform()
                            log_widget.insert(tk.END, f"Elemento clicado: {tag}, texto='{text.strip()}'\n")
                            log_widget.see(tk.END)
                        else:
                            log_widget.insert(tk.END, f"Elemento não encontrado: {step}\n")
                            log_widget.see(tk.END)

                        time.sleep(1)

                    except Exception as e:
                        log_widget.insert(tk.END, f"Erro ao processar o passo: {step}. Erro: {e}\n")
                        log_widget.see(tk.END)

        driver.quit()
        messagebox.showinfo("Execução concluída", "O roteiro foi executado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao executar o roteiro: {e}")

def extract_between(text, start, end):
    try:
        return text.split(start)[1].split(end)[0]
    except IndexError:
        return ""

def select_file():
    file_path = filedialog.askopenfilename(
        title="Selecione o arquivo de roteiro",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if file_path:
        file_name = os.path.basename(file_path)
        with open(file_path, 'r') as file:
            steps = file.readlines()
        
        url = None
        for line in steps:
            if line.startswith("Link:"):
                url = line.strip().replace("Link:", "").strip()
                break

        if not url or not re.match(r'^https?://', url):
            messagebox.showerror("Erro", "Nenhuma URL válida encontrada no arquivo.")
            return

        num_steps = len(steps) - 1

        label_file_info.config(text=f"Arquivo: {file_name}\nPassos: {num_steps}")
        label_url.config(text=f"URL: {url}")

        global file_to_execute
        file_to_execute = file_path

        for widget in frame_steps.winfo_children():
            widget.destroy()

        global selected_steps
        selected_steps = [tk.BooleanVar() for _ in range(num_steps)]

        for i, step in enumerate(steps[1:]):
            step = step.strip()
            checkbox = tk.Checkbutton(frame_steps, text=step, variable=selected_steps[i], bg='#f8f0fc', selectcolor='#e9d1e8', anchor="w", font=("Arial", 10))
            checkbox.grid(row=i, column=0, sticky="w", pady=5)

def select_all():
    for var in selected_steps:
        var.set(True)

def deselect_all():
    for var in selected_steps:
        var.set(False)

def filter_steps(event=None):
    filter_text = entry_filter.get().lower()
    for i, widget in enumerate(frame_steps.winfo_children()):
        step_text = widget.cget("text").lower()  # Acessando o texto real do passo
        if filter_text in step_text:
            widget.grid(row=i, column=0)
        else:
            widget.grid_remove()

def start_test():
    if 'file_to_execute' in globals():
        execute_script_from_file(file_to_execute, selected_steps, log_text)
    else:
        messagebox.showwarning("Aviso", "Selecione um arquivo de roteiro primeiro!")

root = tk.Tk()
root.title("Executor de Roteiros")
root.geometry("1100x800")

# Tela principal com grid
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1, minsize=350)
root.grid_columnconfigure(1, weight=3, minsize=350)

# Seletor de arquivo
btn_select_file = tk.Button(root, text="Selecionar Arquivo de Roteiro", command=select_file)
btn_select_file.grid(row=0, column=0, columnspan=2, pady=20)

label_file_info = tk.Label(root, text="Nenhum arquivo selecionado", justify="left")
label_file_info.grid(row=1, column=0, columnspan=2, pady=10)

label_url = tk.Label(root, text="Nenhuma URL carregada", justify="left")
label_url.grid(row=2, column=0, columnspan=2, pady=10)

entry_filter = tk.Entry(root, width=50)
entry_filter.grid(row=3, column=0, columnspan=2, pady=10)
entry_filter.bind("<KeyRelease>", filter_steps)

# Frame de passos e logs
frame_steps = tk.Frame(root)
frame_steps.grid(row=4, column=0, sticky="nsew")

# Botões de seleção - Definindo os botões antes de usá-los
btn_select_all = tk.Button(root, text="Selecionar Todos", command=select_all)
btn_select_all.grid(row=5, column=0, pady=5)

btn_deselect_all = tk.Button(root, text="Desmarcar Todos", command=deselect_all)
btn_deselect_all.grid(row=6, column=0, pady=5)

btn_start_test = tk.Button(root, text="Iniciar Teste", command=start_test)
btn_start_test.grid(row=7, column=0, pady=20)

# Tela de log
log_frame = tk.Frame(root)
log_frame.grid(row=4, column=1, sticky="nsew")

log_text = tk.Text(log_frame, height=25, width=80, wrap=tk.WORD, bg="#f0f0f0", font=("Arial", 10))
log_text.grid(row=0, column=0, sticky="nsew")

log_scroll = tk.Scrollbar(log_frame, command=log_text.yview)
log_scroll.grid(row=0, column=1, sticky="ns")
log_text.config(yscrollcommand=log_scroll.set)

root.mainloop()