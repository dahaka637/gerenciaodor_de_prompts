from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QFrame,
    QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QClipboard, QIcon
from PyQt6.QtCore import Qt
import sys
from functions import (
    initialize_prompts_file, load_prompts, save_prompt_to_file,
    delete_prompt, custom_messagebox
)
import os




class PromptManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prompt Manager")
        self.setFixedSize(600, 500)

        # Initialize Tabs
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.settings_tab = QWidget()
        self.tabs.addTab(self.main_tab, "Prompts")
        self.tabs.addTab(self.settings_tab, "Configurações")

        # Initialize Tabs Layouts
        self.init_main_tab()
        self.init_settings_tab()

        # Set Central Widget
        self.setCentralWidget(self.tabs)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "logo.ico")
        self.setWindowIcon(QIcon(icon_path))

    def init_main_tab(self):
        main_layout = QVBoxLayout()

        # User Input Text Box
        self.text_box = QTextEdit()
        self.text_box.setPlaceholderText("Digite seu texto aqui...")
        main_layout.addWidget(self.text_box)

        # Prompt Selector
        self.selector = QComboBox()
        self.selector.addItem("Selecione um prompt")
        main_layout.addWidget(self.selector)

        # Copy Button
        self.copy_button = QPushButton("Copiar para área de transferência")
        self.copy_button.clicked.connect(self.copy_to_clipboard_action)
        main_layout.addWidget(self.copy_button)

        # Set Layout
        self.main_tab.setLayout(main_layout)

        # Load Prompts
        self.load_main_tab_selector()

    def load_main_tab_selector(self):
        """Load prompts into the selector on the main tab."""
        self.selector.clear()
        self.selector.addItem("Selecione um prompt")
        prompts = load_prompts()
        for prompt in prompts:
            self.selector.addItem(prompt["name"])

    def copy_to_clipboard_action(self):
        """Combine selected prompt with user text and copy to clipboard."""
        # Obter o texto do usuário
        user_text = self.text_box.toPlainText().strip()

        # Obter o prompt selecionado
        selected_prompt_name = self.selector.currentText()
        if selected_prompt_name == "Selecione um prompt":
            custom_messagebox(
                "Selecione um prompt válido.", "warning", parent_window=self
            )
            return

        # Carregar o conteúdo do prompt selecionado
        prompts = load_prompts()
        selected_prompt_content = next(
            (prompt["content"] for prompt in prompts if prompt["name"] == selected_prompt_name),
            None
        )

        if not selected_prompt_content:
            custom_messagebox(
                "O prompt selecionado não foi encontrado.", "error", parent_window=self
            )
            return

        # Combinar o prompt com o texto do usuário, ou usar apenas o prompt
        if user_text:
            final_text = f'{selected_prompt_content} "{user_text}"'
            message = "O texto foi copiado para a área de transferência!"
        else:
            final_text = selected_prompt_content
            message = "Apenas o conteúdo do prompt foi copiado para a área de transferência!"

        # Copiar para a área de transferência
        QApplication.clipboard().setText(final_text)
        custom_messagebox(message, "success", parent_window=self)


    def init_settings_tab(self):
        settings_layout = QVBoxLayout()

        # Prompt Selector
        self.prompt_selector = QComboBox()
        self.prompt_selector.addItem("Selecione um prompt")
        settings_layout.addWidget(self.prompt_selector)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        settings_layout.addWidget(divider)

        # Prompt Name Entry
        self.prompt_name_entry = QLineEdit()
        self.prompt_name_entry.setPlaceholderText("Nome do prompt")
        settings_layout.addWidget(self.prompt_name_entry)

        # Prompt Content Text Box
        self.prompt_text_box = QTextEdit()
        self.prompt_text_box.setPlaceholderText("Digite o conteúdo do prompt aqui...")
        settings_layout.addWidget(self.prompt_text_box)

        # Save and Delete Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Salvar")
        self.delete_button = QPushButton("Excluir")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)
        settings_layout.addLayout(button_layout)

        # Set Layout
        self.settings_tab.setLayout(settings_layout)

        # Connect Events
        self.save_button.clicked.connect(self.save_prompt_action)
        self.delete_button.clicked.connect(self.delete_prompt_action)
        self.prompt_selector.currentIndexChanged.connect(self.load_prompt_action)

        # Load Prompts
        self.load_prompt_selector()

    def load_prompt_selector(self):
        """Load prompts into the selector on the settings tab."""
        self.prompt_selector.clear()
        self.prompt_selector.addItem("Selecione um prompt")
        prompts = load_prompts()
        for prompt in prompts:
            self.prompt_selector.addItem(prompt["name"])

    def load_prompt_action(self):
        """Load selected prompt details into input fields."""
        selected_name = self.prompt_selector.currentText()
        if selected_name == "Selecione um prompt":
            self.prompt_name_entry.clear()
            self.prompt_text_box.clear()
            return

        prompts = load_prompts()
        selected_prompt = next(
            (prompt for prompt in prompts if prompt["name"] == selected_name), None
        )

        if selected_prompt:
            self.prompt_name_entry.setText(selected_prompt["name"])
            self.prompt_text_box.setPlainText(selected_prompt["content"])

    def save_prompt_action(self):
        """Save or edit prompt in the JSON file."""
        name = self.prompt_name_entry.text().strip()
        content = self.prompt_text_box.toPlainText().strip()

        if not name or not content:
            custom_messagebox(
                "O nome e o conteúdo do prompt não podem estar vazios.", "error", parent_window=self
            )
            return

        try:
            save_prompt_to_file(name, content)
            custom_messagebox(
                f"Prompt '{name}' salvo com sucesso!", "success", parent_window=self
            )
            self.update_all_selectors()
        except ValueError as e:
            custom_messagebox(str(e), "error", parent_window=self)
        except Exception as e:
            custom_messagebox(f"Erro inesperado: {str(e)}", "error", parent_window=self)

    def delete_prompt_action(self):
        """Delete the selected prompt."""
        selected_name = self.prompt_selector.currentText()
        if selected_name == "Selecione um prompt":
            custom_messagebox(
                "Selecione um prompt válido para excluir.", "error", parent_window=self
            )
            return

        reply = QMessageBox.question(
            self,
            "Confirmação",
            f"Tem certeza de que deseja excluir o prompt '{selected_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_prompt(selected_name)
            custom_messagebox(
                f"Prompt '{selected_name}' excluído com sucesso!", "success", parent_window=self
            )
            self.update_all_selectors()
            self.prompt_name_entry.clear()
            self.prompt_text_box.clear()

    def update_all_selectors(self):
        """Update selectors on both tabs."""
        prompts = load_prompts()
        # Update Main Tab Selector
        self.selector.clear()
        self.selector.addItem("Selecione um prompt")
        for prompt in prompts:
            self.selector.addItem(prompt["name"])
        # Update Settings Tab Selector
        self.prompt_selector.clear()
        self.prompt_selector.addItem("Selecione um prompt")
        for prompt in prompts:
            self.prompt_selector.addItem(prompt["name"])


def main():
    initialize_prompts_file()
    app = QApplication(sys.argv)

    # Set Application Style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #202020;
            color: #E0E0E0;
        }
        QComboBox {
            background-color: #282828;
            color: #FFFFFF;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 4px;
            font-size: 14px;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #383838;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            background-color: #282828;
            color: #FFFFFF;
            border: 1px solid #444444;
        }
        QTextEdit, QLineEdit {
            background-color: #282828;
            color: #FFFFFF;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 4px;
        }
        QTextEdit:focus, QLineEdit:focus {
            border: 1px solid #888888;
            outline: none;
        }
        QPushButton {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #444444;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #444444;
            color: #FFFFFF;
        }
        QPushButton:pressed {
            background-color: #555555;
            color: #FFFFFF;
        }
    """)

    window = PromptManagerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
