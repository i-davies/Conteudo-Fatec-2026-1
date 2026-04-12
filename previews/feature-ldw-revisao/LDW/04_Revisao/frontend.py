import flet as ft
import httpx

API_URL = "http://localhost:5000/api"

def main(page: ft.Page):
    page.title = "Enquete Tech"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 50

    texto_titulo = ft.Text("Qual a sua tecnologia favorita?", size=24, weight="bold")
    coluna_placar = ft.Column(spacing=15)

    def carregar_placar():
        """Busca os votos atuais do Backend através de um GET"""
        try:
            resposta = httpx.get(f"{API_URL}/votos")
            dados = resposta.json()
            
            # Limpa a tela para redesenhar
            coluna_placar.controls.clear()
            
            for tecnologia, votos in dados.items():
                linha = ft.Row([
                    ft.Text(f"{tecnologia}: {votos} votos", size=18, expand=True),
                    ft.ElevatedButton("Votar", on_click=lambda e, t=tecnologia: registrar_voto(t))
                ])
                coluna_placar.controls.append(linha)
                
            page.update()
        except Exception:
            coluna_placar.controls.clear()
            coluna_placar.controls.append(ft.Text("Erro ao conectar no banco/backend.", color="red"))
            page.update()

    def registrar_voto(tecnologia):
        """Envia um POST ao Backend para contabilizar um voto"""
        try:
            httpx.post(f"{API_URL}/votar", json={"tecnologia": tecnologia})
            # O sistema é reativo: se o dado mudou no Backend, buscamos novamente
            carregar_placar()
        except Exception:
            page.snack_bar = ft.SnackBar(ft.Text(f"Falha ao votar em {tecnologia}"))
            page.snack_bar.open = True
            page.update()

    # Montando a tela inicial
    page.add(texto_titulo, ft.Divider(), coluna_placar)
    
    # Executa a primeira busca
    carregar_placar()

ft.app(target=main)
