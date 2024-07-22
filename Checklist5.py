import flet as ft
import requests
from datetime import datetime

# Configuração do Firebase
firebase_config = {
    "apiKey": "AIzaSyCRrkvzSEuDgAkno0sMf8m9ojIJF8JQYzU",
    "authDomain": "ckeclist.firebaseapp.com",
    "databaseURL": "https://ckeclist-default-rtdb.firebaseio.com",
    "projectId": "ckeclist",
    "storageBucket": "ckeclist.appspot.com",
    "messagingSenderId": "687761896588",
    "appId": "1:687761896588:web:167cec18d5015b75ecb7a9"
}

database_url = firebase_config["databaseURL"]

def main(page: ft.Page):
    page.title = "Inspetores"
    
    # Função para reiniciar o aplicativo
    def reset_app(e):
        page.clean()
        setup_page()

    # Função para mostrar os campos de senha e botão de entrar
    def show_password_input(e):
        password_textbox.visible = True
        login_button.visible = True
        page.update()

    # Função para buscar inspetores
    def fetch_inspetores():
        response = requests.get(f"{database_url}/Inspetores.json")
        if response.status_code == 200:
            inspetores = response.json()
            dropdown.options = [
                ft.dropdown.Option(key=inspetor, text=inspetor) for inspetor in inspetores.keys()
            ]
            page.update()
        else:
            result_message.value = "Erro ao buscar inspetores."
            page.update()

    # Função para verificar a senha
    def check_password(e):
        selected_inspetor = dropdown.value
        entered_password = password_textbox.value
        response = requests.get(f"{database_url}/Inspetores/{selected_inspetor}.json")
        if response.status_code == 200:
            inspetor_data = response.json()
            stored_password = str(inspetor_data.get("Senha", ""))
            if stored_password == str(entered_password):
                show_inspetor_data(inspetor_data)
            else:
                result_message.value = "Senha incorreta."
                result_message.color = "red"
        else:
            result_message.value = f"Erro ao verificar senha: {response.status_code} - {response.text}"
            result_message.color = "red"
        page.update()

    # Função para mostrar os dados do inspetor após login correto
    def show_inspetor_data(inspetor_data):
        global nivel_textbox  # Definir como global para acessar na função finalizar_inspecao
        page.clean()
        page.add(
            ft.Row(
                controls=[restart_button],
                alignment=ft.MainAxisAlignment.START
            ),
            ft.TextField(
                label="Inspetor",
                value=dropdown.value,
                read_only=True
            ),
            ft.TextField(
                label="Nível",
                value=str(inspetor_data.get("Nivel", "")),
                read_only=True
            ),
            ft.TextField(
                label="Inspeção",
                value=str(inspetor_data.get("Inspecao", "")),
                read_only=True
            )
        )
        nivel_textbox = page.controls[2]  # Acessa o controle do nível
        nivel = str(inspetor_data.get("Nivel", ""))
        if nivel == "1":
            show_numero_chassi()
        elif nivel == "2":
            show_tipo_dropdown()

    # Função para mostrar campo de número do chassi e botão de iniciar inspeção
    def show_numero_chassi():
        global numero_chassi_textbox, iniciar_inspecao_button
        numero_chassi_textbox = ft.TextField(
            label="Número Chassi",
            read_only=False  # Inicialmente somente leitura
        )
        iniciar_inspecao_button = ft.ElevatedButton(
            text="Iniciar Inspeção",
            on_click=fetch_inspecao_chassi
        )
        page.add(
            numero_chassi_textbox,
            iniciar_inspecao_button
        )
        page.update()

    # Função para mostrar dropdown com tipos
    def show_tipo_dropdown():
        response = requests.get(f"{database_url}/Tipo.json")
        if response.status_code == 200:
            tipos = response.json()
            tipo_dropdown = ft.Dropdown(
                label="Tipo",
                options=[ft.dropdown.Option(key=tipo, text=tipo) for tipo in tipos.keys()]
            )
            page.add(tipo_dropdown)
        else:
            result_message.value = "Erro ao buscar tipos."
            result_message.color = "red"
        page.update()
    
    # Função para buscar e exibir checklist
    def fetch_inspecao_chassi(e):
        numero_chassi_textbox.read_only = False  # Desbloquear campo de texto
        iniciar_inspecao_button.visible = False  # Ocultar botão de iniciar inspeção

        response = requests.get(f"{database_url}/InspecaoChassi/Fatiadoras/FT-170.json")
        if response.status_code == 200:
            ft_170_data = response.json()
            if ft_170_data is not None:
                display_checklist(ft_170_data)
            else:
                result_message.value = "Nenhum dado encontrado para a inspeção."
                result_message.color = "red"
                page.update()
        else:
            result_message.value = f"Erro ao buscar inspeção: {response.status_code} - {response.text}"
            result_message.color = "red"
            page.update()

    # Função para exibir checklist com base nos dados
    def display_checklist(ft_170_data):
        page.clean()
        page.add(ft.Row(controls=[restart_button], alignment=ft.MainAxisAlignment.START))

        for key, value in ft_170_data.items():
            page.add(ft.Text(value=key))
            
            if value == "x":
                page.add(
                    ft.Row(
                        controls=[
                            ft.Checkbox(label="OK"),
                            ft.Checkbox(label="Não conforme")
                        ],
                        alignment=ft.MainAxisAlignment.START
                    )
                )
            elif value == "dx":
                page.add(ft.TextField(label="Insira valor", read_only=False))

        finalizar_inspecao_button = ft.ElevatedButton(
            text="Finalizar Inspeção",
            on_click=finalizar_inspecao
        )
        page.add(finalizar_inspecao_button)
        page.update()

    def finalizar_inspecao(e):
        numero_chassi = numero_chassi_textbox.value
        nivel = nivel_textbox.value  # Acessa o valor do controle de nível
        inspetor = dropdown.value
        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "Chassi": numero_chassi,
            "Equipamento": "FT-170",
            "Nivel": nivel,
            "Inspetor": inspetor,
            "Data": data_atual
        }
        
        response = requests.post(f"{database_url}/InspecaoRealizadas.json", json=data)
        if response.status_code == 200:
            result_message.value = "Inspeção finalizada e salva com sucesso."
            result_message.color = "green"
        else:
            result_message.value = f"Erro ao salvar inspeção: {response.status_code} - {response.text}"
            result_message.color = "red"
        page.update()

    def setup_page():
        global restart_button, dropdown, password_textbox, login_button, result_message
        restart_button = ft.ElevatedButton(text="Reiniciar", on_click=reset_app)
        dropdown = ft.Dropdown(label="Selecione um inspetor", on_change=show_password_input)
        password_textbox = ft.TextField(label="Senha", password=True, visible=False)
        login_button = ft.ElevatedButton(text="Entrar", visible=False, on_click=check_password)
        result_message = ft.Text(value="", color="red")

        page.add(
            ft.Row(controls=[restart_button], alignment=ft.MainAxisAlignment.START),
            dropdown,
            password_textbox,
            login_button,
            result_message
        )

        fetch_inspetores()

    setup_page()

ft.app(target=main)
