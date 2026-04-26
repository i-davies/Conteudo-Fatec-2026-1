# pylint: disable=no-member,unexpected-keyword-arg,too-many-function-args
import flet as ft
import httpx

API_URL = "http://localhost:5000/api"


async def main(page: ft.Page):
    page.title = "Enquete Tech"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 50

    texto_titulo = ft.Text("Qual a sua tecnologia favorita?", size=24, weight=ft.FontWeight.BOLD)
    coluna_placar = ft.Column(spacing=15)

    async def carregar_placar():
        try:
            async with httpx.AsyncClient() as client:
                resposta = await client.get(f"{API_URL}/votos")
            dados = resposta.json()

            coluna_placar.controls.clear()

            for tecnologia, votos in dados.items():
                linha = ft.Row(
                    [
                        ft.Text(f"{tecnologia}: {votos} votos", size=18, expand=True),
                        ft.Button(content="Votar", data=tecnologia, on_click=registrar_voto),
                    ]
                )
                coluna_placar.controls.append(linha)

            page.update()
        except Exception:
            coluna_placar.controls.clear()
            coluna_placar.controls.append(ft.Text("Erro ao conectar no backend.", color="red"))
            page.update()

    async def registrar_voto(e):
        tecnologia = e.control.data
        try:
            async with httpx.AsyncClient() as client:
                resposta = await client.post(f"{API_URL}/votar", json={"tecnologia": tecnologia})
            dados = resposta.json()

            if dados.get("sucesso"):
                await carregar_placar()
            else:
                page.show_dialog(ft.SnackBar(content=ft.Text(dados.get("mensagem", "Erro desconhecido"))))
        except Exception:
            page.show_dialog(ft.SnackBar(content=ft.Text(f"Falha de conexao ao votar em {tecnologia}")))

    page.add(texto_titulo, ft.Divider(), coluna_placar)
    await carregar_placar()


ft.run(main, view=ft.AppView.WEB_BROWSER)
