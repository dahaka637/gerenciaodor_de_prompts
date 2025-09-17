import os
import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
import sys

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_FILE = os.path.join(SCRIPT_DIR, "prompts.json")


def initialize_prompts_file():
    """Initialize the prompts.json file if it doesn't exist."""
    if not os.path.exists(PROMPTS_FILE):
        print(f"Arquivo {PROMPTS_FILE} não encontrado. Criando um novo...")
        initial_data = {"prompts": []}
        with open(PROMPTS_FILE, "w") as file:
            json.dump(initial_data, file, indent=4)
    else:
        print(f"Arquivo {PROMPTS_FILE} já existe.")

def save_prompt_to_file(name, content, color="#444444", original_name=None):
    """
    Save or edit a prompt in the prompts.json file.

    :param name: Novo nome do prompt
    :param content: Conteúdo do prompt
    :param color: Cor associada ao prompt (em HEX), padrão: #444444
    :param original_name: Nome original do prompt, se estiver sendo editado
    """
    if not name or not content:
        raise ValueError("O nome e o conteúdo do prompt não podem estar vazios.")

    data = load_json_data()
    updated = False

    for prompt in data["prompts"]:
        # Atualiza se encontrou o nome original ou o nome atual
        if prompt["name"] == (original_name or name):
            prompt["name"] = name
            prompt["content"] = content
            prompt["color"] = color
            updated = True
            break

    if not updated:
        # Caso novo, adiciona com a cor
        data["prompts"].append({
            "name": name,
            "content": content,
            "color": color
        })

    save_json_data(data)
    print(f"Prompt '{name}' salvo com sucesso!")




def load_prompts():
    """Load prompts from the prompts.json file and garantee default fields."""
    data = load_json_data()
    prompts = data.get("prompts", [])
    
    for prompt in prompts:
        if "color" not in prompt:
            prompt["color"] = "#444444"  # Valor padrão

    return prompts



def delete_prompt(name):
    """Delete a prompt by name from the prompts.json file."""
    data = load_json_data()
    original_length = len(data["prompts"])
    data["prompts"] = [prompt for prompt in data.get("prompts", []) if prompt["name"] != name]

    if len(data["prompts"]) < original_length:
        save_json_data(data)
        print(f"Prompt '{name}' excluído com sucesso!")
    else:
        print(f"Prompt '{name}' não encontrado.")


def load_json_data():
    """Load data from the prompts.json file."""
    try:
        with open(PROMPTS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Erro ao carregar prompts. Retornando dados padrão.")
        return {"prompts": []}


def save_json_data(data):
    """Save data to the prompts.json file."""
    with open(PROMPTS_FILE, "w") as file:
        json.dump(data, file, indent=4)


def custom_messagebox(content, message_type="info", parent_window=None):
    """
    Display a custom MessageBox with colored border and text.

    :param content: Message content.
    :param message_type: "success", "error", "warning", or "info".
    :param parent_window: Parent window for positioning.
    """
    # Check if QApplication exists
    app_created = QApplication.instance() is not None
    if not app_created:
        app = QApplication(sys.argv)

    # Styles and emojis for message types
    styles = {
        "success": {"color": "#4CAF50", "emoji": "✅", "border_color": "#4CAF50", "title": "Sucesso"},
        "error": {"color": "#F44336", "emoji": "❌", "border_color": "#F44336", "title": "Erro"},
        "warning": {"color": "#FFC107", "emoji": "⚠️", "border_color": "#FFC107", "title": "Alerta"},
        "info": {"color": "#2196F3", "emoji": "ℹ️", "border_color": "#2196F3", "title": "Informação"},
    }

    style = styles.get(message_type, styles["info"])

    # MessageBox UI
    dialog = QDialog()
    dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
    dialog.setFixedSize(300, 140)
    dialog.setStyleSheet(f"""
        QDialog {{
            background-color: rgba(30, 30, 30, 0.9);
            border: 3px solid {style['border_color']};
            border-radius: 5px;
        }}
    """)

    # Position Dialog
    if parent_window:
        parent_geometry = parent_window.geometry()
        dialog.move(
            parent_geometry.x() + (parent_geometry.width() - dialog.width()) // 2,
            parent_geometry.y() + (parent_geometry.height() - dialog.height()) // 2
        )

    # Layout
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 5, 10, 5)
    layout.setSpacing(5)

    # Title Label
    title_label = QLabel(f"{style['emoji']} {style['title']}")
    title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    title_label.setStyleSheet(f"color: {style['color']};")
    layout.addWidget(title_label)

    # Content Label
    content_label = QLabel(content)
    content_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    content_label.setWordWrap(True)
    content_label.setStyleSheet(f"color: {style['color']};")
    layout.addWidget(content_label)

    # Progress Bar
    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setTextVisible(False)
    progress_bar.setStyleSheet(f"""
        QProgressBar {{
            border: none;
            height: 6px;
            background-color: rgba(50, 50, 50, 0.7);
            border-radius: 6px;
        }}
        QProgressBar::chunk {{
            background-color: {style['color']};
            border-radius: 6px;
        }}
    """)
    layout.addWidget(progress_bar)

    dialog.setLayout(layout)

    # Auto-close Timer
    timer = QTimer()
    timer.setInterval(15)
    progress_value = [0]

    def update_progress():
        if progress_value[0] >= 100:
            timer.stop()
            dialog.accept()
        else:
            progress_value[0] += 1
            progress_bar.setValue(progress_value[0])

    timer.timeout.connect(update_progress)
    timer.start()

    # Close on Click
    def close_on_click(event):
        timer.stop()
        dialog.accept()

    dialog.mousePressEvent = close_on_click

    # Display MessageBox
    dialog.exec()

    # Cleanup
    if not app_created:
        app.exit()
