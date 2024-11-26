import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
import time
driver = None
interactions = []
is_recording = False
def capture_interaction(event_type, element_info):
    """Função para registrar interações"""
    interaction = f"{event_type}: {element_info}"
    interactions.append(interaction)
    print(interaction)
def monitor_interactions():
    global is_recording
    if not is_recording:
        return
    
    try:
        events = driver.execute_script("return document.interactions;")
        driver.execute_script("document.interactions = [];")

        for event in events:
            if event['type'] == 'click':
                element_info = f"Elemento {event['tag']} com ID='{event['id']}' e classe='{event['class']}'"
                capture_interaction("Clique", element_info)
            elif event['type'] == 'keypress':
                element_info = f"Tecla '{event['key']}' pressionada no elemento {event['tag']} com ID='{event['id']}' e classe='{event['class']}'"
                capture_interaction("Tecla pressionada", element_info)
        if is_recording:
            root.after(1000, monitor_interactions)

    except Exception as e:
        print(f"Erro ao monitorar interações: {e}")

def start_recording():
    global driver, interactions, is_recording
    interactions = [] 
    url = url_entry.get()
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    script = """
    document.interactions = []; // Lista de interações

    // Captura cliques
    document.addEventListener('click', function(event) {
        document.interactions.push({
            type: 'click',
            tag: event.target.tagName,
            id: event.target.id || '',
            class: event.target.className || ''
        });
    });

    // Captura teclas pressionadas
    document.addEventListener('keydown', function(event) {
        document.interactions.push({
            type: 'keypress',
            key: event.key,
            tag: event.target.tagName,
            id: event.target.id || '',
            class: event.target.className || ''
        });
    });

    return true;
    """
    driver.execute_script(script)
    is_recording = True
    monitor_interactions()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
def save_file():
    global is_recording, driver
    is_recording = False
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])

    if file_path: 
        with open(file_path, "w") as file:
            file.write("\n".join(interactions)) 
        print(f"Interações salvas em {file_path}")
    
    driver.quit()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED) 
root = tk.Tk()
root.title("Monitor de Interações")
url_label = tk.Label(root, text="Link do site:")
url_label.pack()
url_entry = tk.Entry(root, width=50)
url_entry.insert(0, "https://testeauto_integrada.testescard.limber.net.br")
url_entry.pack()
start_button = tk.Button(root, text="Iniciar Gravação", command=start_recording)
start_button.pack(pady=10)
stop_button = tk.Button(root, text="Parar Gravação", command=save_file, state=tk.DISABLED)
stop_button.pack(pady=10)
root.mainloop()