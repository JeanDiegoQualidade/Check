import flet as ft
import requests
from datetime import datetime

# Configuração do Firebase
firebase_config = {
    "apiKey": "AIzaSyCRrkvzSEuDgAkno0sMf8m9ojIJF8m9ojIJF8JQYzU",
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
        global numero_chassi_textbox, nivel_textbox, tipo_dropdown, subtipo_dropdown, checklist_container, finalizar_button
        
        numero_chassi_textbox = ft.TextField(
            label="Número Chassi",
            read_only=True  # Inicialmente somente leitura
        )
        
        # Definir como global para acessar na função finalizar_inspecao
        global nivel_textbox, tipo_dropdown, subtipo_dropdown, checklist_container
        
        page.clean()
        
        # Função para buscar os tipos do Firebase
        def fetch_tipos():
            response = requests.get(f"{database_url}/Tipo.json")
            if response.status_code == 200:
                tipos = response.json()
                return [ft.dropdown.Option(key=tipo, text=tipo) for tipo in tipos.keys()]
            else:
                return []
        
        # Função para buscar subtipos do tipo selecionado
        def fetch_subtipos(tipo):
            response = requests.get(f"{database_url}/Tipo/{tipo}.json")
            if response.status_code == 200:
                subtipos = response.json()
                return [ft.dropdown.Option(key=subtipo, text=subtipo) for subtipo in subtipos.keys()]
            else:
                return []
        
        # Função para buscar checklist do subtipo selecionado na camada InspecaoChassi
        def fetch_checklist(subtipo):
            response = requests.get(f"{database_url}/InspecaoChassi/{subtipo}.json")
            if response.status_code == 200:
                checklist_data = response.json()
                # Verifica se a resposta é um dicionário
                if isinstance(checklist_data, dict):
                    return checklist_data
                else:
                    print(f"Formato de dados inesperado: {checklist_data}")
                    return {}
            else:
                print(f"Erro ao buscar checklist: {response.status_code}")
                return {}
        
        # Evento para quando um tipo é selecionado
        def on_tipo_change(e):
            selected_tipo = tipo_dropdown.value
            if (selected_tipo):
                subtipo_options = fetch_subtipos(selected_tipo)
                subtipo_dropdown.options = subtipo_options
                subtipo_dropdown.visible = True
                page.update()
        
        # Evento para quando um subtipo é selecionado
        def on_subtipo_change(e):
            selected_subtipo = subtipo_dropdown.value
            if (selected_subtipo):
                checklist_data = fetch_checklist(selected_subtipo)
                build_checklist(checklist_data)
                checklist_container.visible = True
                page.update()
        
        # Função para construir o checklist
        def build_checklist(checklist_data):
            checklist_container.clean()
            controls = []
            for item, value in checklist_data.items():
                if value == "x":
                    controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(value=item),
                                ft.Checkbox(label="Conforme"),
                                ft.Checkbox(label="Não Conforme")
                            ]
                        )
                    )
                elif value == "dx":
                    controls.append(
                        ft.Row(
                            controls=[
                                ft.Text(value=item),
                                ft.TextField(label="Detalhe")
                            ]
                        )
                    )
            # Atualiza o Column com os controles do checklist
            checklist_container.controls = controls
            page.update()

            # Adiciona o botão "Finalizar Inspeção"
            finalizar_button = ft.ElevatedButton(
                text="Finalizar Inspeção",
                on_click=finalizar_inspecao
            )
            page.add(finalizar_button)
    ###################################################    
    def finalizar_inspecao(e):
        chassi_number = numero_chassi_textbox.value
        checklist_results = {}
        for control in checklist_container.controls:
            if isinstance(control, ft.Row):
                item_name = control.controls[0].value
                if len(control.controls) == 3:  # Checkbox
                    conforme = control.controls[1].value
                    nao_conforme = control.controls[2].value
                    checklist_results[item_name] = {
                        "Conforme": conforme,
                        "NaoConforme": nao_conforme
                    }
                elif len(control.controls) == 2:  # TextField for details
                    detalhe = control.controls[1].value
                    checklist_results[item_name] = {
                        "Detalhe": detalhe
                    }
        
        inspecao_data = {
            "Chassi": chassi_number,
            "Data": datetime.now().strftime("%Y-%m-%d"),
            "Checklist": checklist_results
        }
        
        # Criar o conteúdo do arquivo .txt
        txt_content = f"Chassi: {chassi_number}\nData: {datetime.now().strftime('%Y-%m-%d')}\n\nChecklist:\n"
        for item, details in checklist_results.items():
            txt_content += f"- {item}\n"
            for key, value in details.items():
                txt_content += f"  {key}: {value}\n"
        
        # Caminho para salvar o arquivo .txt
        txt_path = "/storage/emulated/0/DriverSyncFiles/Checklist_finalizado.txt"
        
        # Salvar o arquivo .txt
        try:
            with open(txt_path, 'w') as file:
                file.write(txt_content)
            result_message.value = "Inspeção finalizada e arquivo salvo com sucesso."
            result_message.color = "green"
        except Exception as e:
            result_message.value = f"Erro ao salvar arquivo: {e}"
            result_message.color = "red"
        
        page.update()
        ################################################
        # Obter opções de tipos
        tipo_options = fetch_tipos()
        
        # Adiciona campos à página
        page.add(
            numero_chassi_textbox,
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
            ),
            ft.Dropdown(
                label="Tipo",
                options=tipo_options,
                on_change=on_tipo_change
            ),
            ft.Dropdown(
                label="Subtipo",
                options=[],
                visible=False,
                on_change=on_subtipo_change
            ),
            ft.Column(
                controls=[],
                scroll=ft.ScrollMode.AUTO,  # Adiciona rolagem automática
                width=page.width,  # Ajuste a largura conforme necessário
                height=500  # Ajuste a altura conforme necessário
            )
        )
        
        # Atualiza referências globais
        nivel_textbox = page.controls[3]  # Acessa o controle do nível
        tipo_dropdown = page.controls[5]  # Acessa o controle da lista suspensa de tipos
        subtipo_dropdown = page.controls[6]  # Acessa o controle da lista suspensa de subtipos
        checklist_container = page.controls[7]  # Acessa o Column para o checklist

        nivel = str(inspetor_data.get("Nivel", ""))
        if nivel == "1":
            show_numero_chassi(inspetor_data)

                
    # Função para mostrar campo de número do chassi e botão de iniciar inspeção
    def show_numero_chassi(inspetor_data):
        generate_chassi_number(inspetor_data)

    # Função para gerar o número do chassi
    def generate_chassi_number(inspetor_data):
        # Busca a sequência atual do Firebase
        response = requests.get(f"{database_url}/Sequencia.json")
        if response.status_code == 200:
            try:
                # Verifica se a resposta é um dicionário válido
                data = response.json()
                if isinstance(data, dict) and "Sequencia" in data:
                    current_sequence = data["Sequencia"]
                else:
                    current_sequence = 0
                
                # Calcula o ano e a semana atuais
                now = datetime.now()
                year = now.strftime("%y")
                week = now.strftime("%U")
                new_sequence = current_sequence + 1

                # Constrói o número do chassi
                chassi_number = f"{week}{year}{new_sequence:1d}"
                
                # Atualiza o campo de número do chassi
                numero_chassi_textbox.value = chassi_number
                page.update()

                # Incrementa a sequência no Firebase
                requests.put(f"{database_url}/Sequencia.json", json={"Sequencia": new_sequence})
            except (AttributeError, TypeError, ValueError) as e:
                print(f"Erro ao gerar número do chassi: {e}")
                numero_chassi_textbox.value = "Erro ao gerar número do chassi"
                page.update()
        else:
            print(f"Erro ao conectar: {response.status_code} - {response.text}")
            numero_chassi_textbox.value = "Erro ao conectar"
            page.update()

    def setup_page():
        global dropdown, password_textbox, login_button, result_message, restart_button
        dropdown = ft.Dropdown(
            options=[],
            hint_text="Selecione um inspetor",
            on_change=show_password_input
        )
        password_textbox = ft.TextField(
            label="Senha",
            password=True,
            visible=False
        )
        login_button = ft.ElevatedButton(
            text="Entrar",
            on_click=check_password,
            visible=False
        )
        result_message = ft.Text("")
        restart_button = ft.ElevatedButton(
            text="Reiniciar",
            on_click=reset_app
        )
        page.add(
            dropdown,
            password_textbox,
            login_button,
            result_message
        )
        fetch_inspetores()

    setup_page()

ft.app(target=main)
