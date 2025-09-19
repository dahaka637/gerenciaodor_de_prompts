# 🗂️ Gerenciador de Prompts para IA

## 📌 Sobre o Projeto
O **Gerenciador de Prompts para IA** é uma aplicação desktop desenvolvida em **Python + PyQt6**, projetada para auxiliar profissionais da área **jurídica e policial** na criação, organização e uso de **prompts especializados**.

Com ele, é possível **gerenciar coleções de prompts**, usar rapidamente textos pré-formatados para **transcrições, sínteses, declarações, relatórios e conclusões**, e copiá-los diretamente para a área de transferência, prontos para uso em modelos de **Inteligência Artificial**.

<img width="654" height="583" alt="image" src="https://github.com/user-attachments/assets/4fa238f7-2128-400d-995f-2fda891f9470" />

---

## 🚀 Funcionalidades
- Interface gráfica intuitiva em **PyQt6**.
- **Gerenciamento de prompts** (criar, editar, excluir, colorir).
- **Uso rápido de prompts** com cópia automática para a área de transferência.
- Organização visual com **cores personalizadas**.
- **Sistema de abas** para separar:
  - 📑 **Prompts** → uso e cópia imediata.
  - ⚙️ **Configurações** → criação, edição e exclusão.
- **Animações e feedback visual** (status animado, botões estilizados, efeitos gráficos).
- Prompts **pré-carregados** no arquivo `prompts.json` voltados ao **uso jurídico/policial**.

---
<img width="652" height="584" alt="image" src="https://github.com/user-attachments/assets/33a5dc93-be3f-4462-a001-459446a8a63d" />

## 📂 Estrutura do Projeto
```
gerenciador_de_prompts/
├── main.py           # Interface principal (PyQt6)
├── functions.py      # Funções utilitárias (CRUD de prompts)
├── prompts.json      # Arquivo com prompts pré-carregados
└── icone.ico         # Ícone do aplicativo
```

---

## ⚙️ Requisitos
- **Python 3.10+**
- Dependências:
  ```bash
  pip install pyqt6 pyperclip
  ```

---

## ▶️ Como Executar
1. Clone o repositório:
   ```bash
   git clone https://github.com/dahaka637/gerenciaodor_de_prompts
   cd gerenciaodor_de_prompts
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute o programa:
   ```bash
   python main.py
   ```

---

## 📝 Prompts Pré-Carregados
O arquivo `prompts.json` contém diversos **prompts prontos para uso em IA**, como:
- **Transcrição de Oitiva**
- **Síntese de Boletim de Ocorrência**
- **Síntese de Laudo Pericial**
- **Relato para Boletim de Ocorrência**
- **Declaração Preliminar**
- **II – Da Adequação do Fato Típico**
- **III – Conclusão (com ou sem indiciamento)**
- **Portaria**

Cada prompt já está formatado para atender às necessidades de **formalidade, objetividade e clareza jurídica**, facilitando a integração com modelos de IA.

---

## 📦 Build (opcional)
Para compilar em um executável standalone, recomenda-se o uso do **Nuitka**:

```bash
python -m nuitka ^
  --standalone ^
  --windows-console-mode=disable ^
  --enable-plugin=pyqt6 ^
  --include-data-file=prompts.json=prompts.json ^
  --windows-icon-from-ico=icone.ico ^
  "<DIRETÓRIO>\main.py"
```

> ⚠️ Certifique-se de incluir o arquivo `prompts.json` junto com o executável.

---

## 📜 Licença
Este projeto é de uso **interno** e voltado ao auxílio em procedimentos jurídicos/policiais.  
Consulte as restrições de uso antes de redistribuir.

---

## 🙌 Créditos
- Interface e lógica em Python/PyQt6.
- Prompts especializados desenvolvidos para **otimizar uso com IA**.
