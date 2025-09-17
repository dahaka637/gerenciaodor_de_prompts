from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QFrame,
    QHBoxLayout, QMessageBox, QLabel, QProgressBar
)
from PyQt6.QtGui import QClipboard, QIcon, QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt, QTimer, QSize  # já deve ter a maioria, só adicione o QSize se faltar

import sys
from functions import (
    initialize_prompts_file, load_prompts, save_prompt_to_file,
    delete_prompt
)
import os
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QColorDialog  
import qtawesome as qta
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation

# FEITO: organizar por alfanumerico e alfabetico
# FEITO: salvar inteligente, ou seja atualizar prompt ao inves de crair novo
# FEITO: sistmea de cores de prompt

class PromptManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prompt Manager")
        self.resize(650, 550)
        self._pulse_timer = QTimer()
        self._pulse_value = 255
        self._pulse_direction = -15
        self._original_prompt_name = None



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
        self.text_box.setObjectName("mainTextBox")

        self.text_box.setPlaceholderText("Digite seu texto aqui...")
        main_layout.addWidget(self.text_box)

        # Status Message (altura fixa e sempre visível)
        self.status_label = QLabel(" ")
        self.status_label.setStyleSheet("color: lightgray; font-style: italic;")
        self.status_label.setFixedHeight(20)  # Altura fixa para não causar deslocamento
        main_layout.addWidget(self.status_label)


        # Prompt Selector
        self.selector = QComboBox()
        self.selector.addItem("Selecione um prompt")
        self.selector.setMaxVisibleItems(15)  # Valor ajustável, o padrão é 10
        main_layout.addWidget(self.selector)

        # Copy Button
        # Copy Button (com ícone e estilo bonito)
        self.copy_button = QPushButton("  Copiar para área de transferência")  # Espaço antes para o ícone
        self.copy_button.setObjectName("copyButton")
        self.copy_button.setIcon(qta.icon("fa5s.copy", color="blue"))
        self.copy_button.setIconSize(QSize(16, 16))
        self.copy_button.clicked.connect(self.copy_to_clipboard_action)
        self.copy_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #2196F3;         /* azul suave */
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                color: #0D47A1;                    /* azul escuro para texto */
                background-color: #E3F2FD;         /* azul muito claro de fundo */
            }
            QPushButton:hover {
                background-color: #BBDEFB;         /* leve destaque no hover */
            }

        """)
        main_layout.addWidget(self.copy_button)


        # Clear Button
        # Clear Button
        # self.clear_button = QPushButton("Limpar texto")
        # self.clear_button.setObjectName("clearButton")
        # self.clear_button.clicked.connect(self.clear_text_box_action)
        # main_layout.addWidget(self.clear_button)



        # Set Layout
        self.main_tab.setLayout(main_layout)

        # Load Prompts
        self.load_main_tab_selector()

    def sort_prompts_by_color_similarity(self, prompts, base_color="#444444"):
        """Ordena os prompts pela similaridade de cor em relação à base."""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        def color_distance(c1, c2):
            # Distância Euclidiana no espaço RGB
            return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5

        base_rgb = hex_to_rgb(base_color)

        sorted_prompts = sorted(
            prompts,
            key=lambda prompt: color_distance(hex_to_rgb(prompt.get("color", "#444444")), base_rgb)
        )

        return sorted_prompts

    def load_main_tab_selector(self):
        """Load prompts into the selector on the main tab, with colored items."""
        prompts = self.sort_prompts_by_color_similarity(load_prompts())

        self.populate_prompt_combobox(self.selector, prompts)

    def animar_botao_ao_clicar(self, botao: QPushButton):
        efeito = QGraphicsOpacityEffect(botao)
        botao.setGraphicsEffect(efeito)

        animacao = QPropertyAnimation(efeito, b"opacity")
        animacao.setDuration(300)
        animacao.setStartValue(1.0)
        animacao.setKeyValueAt(0.5, 0.3)
        animacao.setEndValue(1.0)
        animacao.start()
        
        # Impede GC coletar a animação prematuramente
        self.animacao_ativa = animacao

    def copy_to_clipboard_action(self):
        """Combine selected prompt with user text and copy to clipboard."""
        # Obter o texto do usuário
        self.animar_botao_ao_clicar(self.copy_button)

        user_text = self.text_box.toPlainText().strip()

        # Obter o prompt selecionado
        selected_prompt_name = self.selector.currentText()
        if selected_prompt_name == "Selecione um prompt":
            self.show_status("Selecione um prompt válido!", tipo="warning")


            return

        # Carregar o conteúdo do prompt selecionado
        prompts = load_prompts()
        selected_prompt_content = next(
            (prompt["content"] for prompt in prompts if prompt["name"] == selected_prompt_name),
            None
        )

        if not selected_prompt_content:
            self.show_status("O prompt selecionado não foi encontrado.", tipo="error")
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
        self.show_status(message, tipo="success")


    def init_settings_tab(self):
        settings_layout = QVBoxLayout()

        # Prompt Selector
        self.prompt_selector = QComboBox()
        self.prompt_selector.addItem("Selecione um prompt")
        self.prompt_selector.setMaxVisibleItems(15)  
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

        # Label de status/aviso (acima do campo "Nome do Prompt")
        self.config_status_label = QLabel(" ")
        self.config_status_label.setStyleSheet("""
            color: lightgray;
            font-style: italic;
            font-weight: bold;
            font-size: 13px;
        """)
        self.config_status_label.setFixedHeight(20)  # Mantém o espaço reservado
        self.config_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(self.config_status_label)

        # Prompt Content Text Box
        self.prompt_text_box = QTextEdit()
        self.prompt_text_box.setPlaceholderText("Digite o conteúdo do prompt aqui...")
        settings_layout.addWidget(self.prompt_text_box)
        # Seletor de cor
        self.color_label = QLabel("Cor do Prompt (opcional):")
        self.color_button = QPushButton("Escolher Cor")
        self.color_button.clicked.connect(self.choose_color)
        self.selected_color = None  # Armazena a cor escolhida em HEX

        settings_layout.addWidget(self.color_label)
        settings_layout.addWidget(self.color_button)

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
        """Load prompts into the selector on the settings tab, with colored items."""
        prompts = load_prompts()
        self.populate_prompt_combobox(self.prompt_selector, prompts)


    def load_prompt_action(self):
        """Load selected prompt details into input fields."""
        selected_name = self.prompt_selector.currentText()

        if selected_name == "Selecione um prompt":
            # Entrando no modo "novo prompt"
            self.prompt_name_entry.clear()
            self.prompt_text_box.clear()
            self.color_button.setStyleSheet("")
            self.color_button.setText("Escolher Cor")
            self.selected_color = None
            self._original_prompt_name = None
            return

        prompts = load_prompts()
        selected_prompt = next(
            (prompt for prompt in prompts if prompt["name"] == selected_name), None
        )

        if selected_prompt:
            self._original_prompt_name = selected_prompt["name"]
            self.prompt_name_entry.setText(selected_prompt["name"])
            self.prompt_text_box.setPlainText(selected_prompt["content"])

            color = selected_prompt.get("color", "#444444")
            self.selected_color = color
            self.color_button.setStyleSheet(f"background-color: {color}; color: black;")
            self.color_button.setText(color)


    def save_prompt_action(self):
        """Save or edit prompt in the JSON file."""
        name = self.prompt_name_entry.text().strip()
        content = self.prompt_text_box.toPlainText().strip()

        if not name or not content:
            self.show_status("O nome e o conteúdo do prompt não podem estar vazios.", tipo="error")
            return

        # Captura o nome original do prompt selecionado
        original_name = self.prompt_selector.currentText()
        if original_name == "Selecione um prompt":
            original_name = None  # Trata como novo prompt

        try:
            save_prompt_to_file(name, content, self.selected_color, original_name)
            self.show_status(f"Prompt '{name}' salvo com sucesso!", tipo="success")

            self.update_all_selectors()
            self.prompt_selector.setCurrentText(name)  # Atualiza a seleção após salvar
        except ValueError as e:
            self.show_status(str(e), tipo="error")
        except Exception as e:
            self.show_status(f"Erro inesperado: {str(e)}", tipo="error")


    def delete_prompt_action(self):
        """Delete the selected prompt."""
        selected_name = self.prompt_selector.currentText()
        if selected_name == "Selecione um prompt":
            self.show_status("Selecione um prompt válido para excluir.", tipo="error")
            return

        reply = QMessageBox.question(
            self,
            "Confirmação",
            f"Tem certeza de que deseja excluir o prompt '{selected_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_prompt(selected_name)
            self.show_status(f"Prompt '{selected_name}' excluído com sucesso!", tipo="success")

            self.update_all_selectors()
            self.prompt_name_entry.clear()
            self.prompt_text_box.clear()

    def update_all_selectors(self):
        """Update both combo boxes (main and settings) with colored prompt items."""
        prompts = load_prompts()
        self.populate_prompt_combobox(self.selector, prompts)
        self.populate_prompt_combobox(self.prompt_selector, prompts)


    def clear_text_box_action(self):
        """Limpa o conteúdo da caixa de texto do usuário."""
        self.text_box.clear()
        self.show_status("Texto limpo com sucesso.", tipo="info")

    def populate_prompt_combobox(self, combo_box: QComboBox, prompts: list):
        model = QStandardItemModel()
        default_item = QStandardItem("Selecione um prompt")
        #default_item.setFlags(default_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)  # Não selecionável
        model.appendRow(default_item)

        for prompt in prompts:
            name = prompt["name"]
            color_hex = prompt.get("color", "#444444")
            bg_color = QColor(color_hex)

            # Calcular brilho (luminosidade percebida)
            brightness = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())

            # Cor do texto: preto se fundo for claro, branco se fundo for escuro
            text_color = QColor("#000000") if brightness > 160 else QColor("#FFFFFF")

            item = QStandardItem(name)
            item.setBackground(bg_color)
            item.setForeground(text_color)

            model.appendRow(item)

        combo_box.setModel(model)
        combo_box.setCurrentIndex(0)



    def show_status(self, message: str, tipo: str = "info", duration_ms: int = 2000):
        # Mapeia cores por tipo de mensagem
        cores = {
            "success": "#90EE90",  # verde claro
            "warning": "#FFD700",  # amarelo ouro
            "error":   "#FF7F7F",  # vermelho claro
            "info":    "#D3D3D3",  # cinza claro padrão
        }

        self._current_text_color = cores.get(tipo, cores["info"])

        # Aplica estilo inicial (opacidade máxima)
        self._apply_status_styles(255)

        # Define o conteúdo nas duas labels (se existirem)
        self.status_label.setText(message)
        if hasattr(self, "config_status_label"):
            self.config_status_label.setText(message)

        # Inicia temporizador da animação
        self._progress = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_status_progress)
        self._timer.start(duration_ms // 100)

        # Efeito de pulsação
        self._pulse_value = 255
        self._pulse_direction = -15
        self._pulse_timer = QTimer()
        self._pulse_timer.timeout.connect(self._pulse_effect)
        self._pulse_timer.start(30)

    def _apply_status_styles(self, alpha: int):
        style = f"""
            color: rgba({self._hex_to_rgb(self._current_text_color)}, {alpha});
            font-style: italic;
            font-weight: bold;
            font-size: 16px;
            qproperty-alignment: 'AlignCenter';
        """
        self.status_label.setStyleSheet(style)
        if hasattr(self, "config_status_label"):
            self.config_status_label.setStyleSheet(style)

    def _pulse_effect(self):
        self._pulse_value += self._pulse_direction
        if self._pulse_value <= 100 or self._pulse_value >= 255:
            self._pulse_direction *= -1
            self._pulse_value += self._pulse_direction

        self._apply_status_styles(self._pulse_value)

    def _update_status_progress(self):
        self._progress += 1
        if self._progress >= 100:
            self.status_label.setText(" ")
            if hasattr(self, "config_status_label"):
                self.config_status_label.setText(" ")
            self._timer.stop()
            self._pulse_timer.stop()

    def _hex_to_rgb(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip('#')
        return ', '.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()  # Salva como string HEX, ex: "#FF5733"
            self.color_button.setStyleSheet(f"background-color: {self.selected_color}; color: black;")
            self.color_button.setText(self.selected_color)


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
        QTextEdit#mainTextBox {
            background-color: white;
            color: black;
        }

        QPushButton#clearButton {
            border: 2px solid #444444; /* borda normal */
        }

        QPushButton#clearButton:pressed {
            border: 2px solid #FF5C5C; /* vermelho claro só ao clicar */
        }


    """)

    window = PromptManagerApp()
    window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
