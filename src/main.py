import asyncio
import logging
from dataclasses import dataclass, field
import flet as ft
from flet_notify import FletNotify, NotificationImportance, FletNotifyException

logging.basicConfig(level=logging.WARNING)
for _noisy in ("flet", "flet_transport", "flet_controls", "asyncio"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)

BG = "#0f0f11"
SURFACE = "#1a1a1f"
SURFACE2 = "#222228"
BORDER = "#2e2e38"
PRIMARY = "#6c63ff"
PRIMARY_DIM = "#3d3880"
ACCENT = "#00d8b4"
TEXT_MUTED = "#6b6b80"
RED = "#ff5b5b"


@dataclass
@ft.observable
class AppState:
    """Estado global reativo do app, compartilhado entre todos os componentes."""

    notification_count: int = 0
    dev_mode: bool = False
    notifier: object = field(default=None, repr=False)

    def increment(self):
        """Incrementa o contador de notificações enviadas."""
        self.notification_count += 1


def _build_theme() -> ft.Theme:
    """Constrói e retorna o tema dark customizado do app."""
    color_scheme = ft.ColorScheme(
        primary=PRIMARY,
        on_primary=ft.Colors.WHITE,
        secondary=ACCENT,
        on_secondary=ft.Colors.BLACK,
        surface=SURFACE,
        on_surface=ft.Colors.WHITE,
        surface_container_highest=SURFACE2,
        outline=BORDER,
        error=RED,
    )
    return ft.Theme(
        color_scheme=color_scheme,
        color_scheme_seed=PRIMARY,
        expansion_tile_theme=ft.ExpansionTileTheme(
            bgcolor=SURFACE,
            collapsed_bgcolor=SURFACE,
            icon_color=PRIMARY,
            collapsed_icon_color=TEXT_MUTED,
            text_color=ft.Colors.WHITE,
            collapsed_text_color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=12),
            collapsed_shape=ft.RoundedRectangleBorder(radius=12),
            tile_padding=ft.Padding.symmetric(horizontal=16, vertical=4),
        ),
        outlined_button_theme=ft.OutlinedButtonTheme(
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: ft.Colors.WHITE,
                    ft.ControlState.HOVERED: PRIMARY,
                },
                side={
                    ft.ControlState.DEFAULT: ft.BorderSide(1, BORDER),
                    ft.ControlState.HOVERED: ft.BorderSide(1, PRIMARY),
                },
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            )
        ),
        floating_action_button_theme=ft.FloatingActionButtonTheme(
            bgcolor=PRIMARY,
            foreground_color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=16),
        ),
        snackbar_theme=ft.SnackBarTheme(
            bgcolor=SURFACE2,
            content_text_style=ft.TextStyle(color=ft.Colors.WHITE),
            behavior=ft.SnackBarBehavior.FLOATING,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )


def _tile_style() -> dict:
    """Retorna o dicionário de estilo padrão aplicado a todos os ExpansionTiles."""
    return dict(
        bgcolor=SURFACE,
        collapsed_bgcolor=SURFACE,
        tile_padding=ft.Padding.symmetric(horizontal=16, vertical=4),
        shape=ft.RoundedRectangleBorder(radius=12),
        collapsed_shape=ft.RoundedRectangleBorder(radius=12),
    )


def _show_snack(message: str, error: bool = False):
    """Exibe um SnackBar flutuante com a mensagem fornecida."""
    ft.context.page.show_dialog(
        ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=RED if error else SURFACE2,
            duration=2000,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin.all(10),
            shape=ft.RoundedRectangleBorder(radius=12),
        )
    )


def _dev_simulate(state: AppState, action: str) -> bool:
    """Simula o envio em modo desenvolvimento, incrementando o contador e exibindo feedback."""
    if state.dev_mode:
        state.increment()
        _show_snack(f"🔧 DEV: {action}")
        return True
    return False


@ft.component
def CounterBadge(count: int):
    """Exibe o badge com o contador de notificações enviadas na app bar."""
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.SEND, size=14, color=PRIMARY),
                ft.Text(
                    value=str(count),
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY,
                ),
            ],
            spacing=5,
            tight=True,
        ),
        bgcolor=PRIMARY_DIM,
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
    )


@ft.component
def AppBar(state: AppState):
    """Renderiza a barra de título do app com o badge de contador reativo."""
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, size=26, color=ACCENT),
                ft.Text(
                    "Notificações",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Container(expand=True),
                CounterBadge(count=state.notification_count),
            ],
            spacing=10,
        ),
        bgcolor=SURFACE,
        padding=ft.Padding.symmetric(horizontal=18, vertical=14),
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
    )


@ft.component
def SimpleSection(state: AppState):
    """Seção com botões para envio de notificações simples: normal, silenciosa e persistente."""

    async def send_normal(e):
        if _dev_simulate(state, "Notificação normal"):
            return
        try:
            state.notifier.send("Nova Mensagem", "Você tem uma nova mensagem!")
            state.increment()
            _show_snack("✅ Notificação enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def send_silent(e):
        if _dev_simulate(state, "Notificação silenciosa"):
            return
        try:
            state.notifier.send("Sincronização", "Dados atualizados", silent=True)
            state.increment()
            _show_snack("🔕 Notificação silenciosa enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def send_persistent(e):
        if _dev_simulate(state, "Notificação persistente"):
            return
        try:
            state.notifier.send("Música Tocando", "Artist - Song Title", ongoing=True)
            state.increment()
            _show_snack("📌 Notificação persistente enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    tile = ft.ExpansionTile(
        title=ft.Text("📨 Notificações Simples", color=ft.Colors.WHITE),
        subtitle=ft.Text(
            "Básicas, silenciosas e persistentes", color=TEXT_MUTED, size=12
        ),
        controls=[
            ft.Container(
                content=ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "Normal",
                                    icon=ft.Icons.NOTIFICATIONS,
                                    on_click=send_normal,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "Silenciosa",
                                    icon=ft.Icons.NOTIFICATIONS_OFF,
                                    on_click=send_silent,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "Persistente",
                                    icon=ft.Icons.PUSH_PIN,
                                    on_click=send_persistent,
                                    expand=True,
                                )
                            ],
                        ),
                    ]
                ),
                padding=10,
            )
        ],
        **_tile_style(),
    )
    tile.initially_expanded = True
    return tile


@ft.component
def ProgressSection(state: AppState):
    """Seção com botões para notificações com barra de progresso determinada e indeterminada."""

    async def send_determinate(e):
        if state.dev_mode:
            e.control.disabled = True
            ft.context.page.update()
            state.increment()
            _show_snack("🔧 DEV: Simulando progress determinado")
            await asyncio.sleep(2)
            e.control.disabled = False
            ft.context.page.update()
            return
        try:
            e.control.disabled = True
            ft.context.page.update()
            status = (
                state.notifier.create(
                    title="Download em andamento", message="Iniciando download..."
                )
                .with_progress()
                .send()
            )
            state.increment()
            for i in range(0, 101, 10):
                await asyncio.sleep(0.3)
                status.update_progress(i, message=f"{i}% concluído")
            status.remove_progress("Download concluído!", show_briefly=True)
            _show_snack("✅ Download finalizado")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            ft.context.page.update()

    async def send_indeterminate(e):
        if state.dev_mode:
            e.control.disabled = True
            ft.context.page.update()
            state.increment()
            _show_snack("🔧 DEV: Simulando progress indeterminado")
            await asyncio.sleep(2)
            e.control.disabled = False
            ft.context.page.update()
            return
        try:
            e.control.disabled = True
            ft.context.page.update()
            status = (
                state.notifier.create(title="Processando", message="Aguarde...")
                .with_progress()
                .send()
            )
            state.increment()
            await asyncio.sleep(3)
            status.remove_progress("Processamento concluído!", show_briefly=True)
            _show_snack("✅ Processamento finalizado")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            ft.context.page.update()

    return ft.ExpansionTile(
        title=ft.Text("📊 Progress Bar", color=ft.Colors.WHITE),
        subtitle=ft.Text("Determinado e indeterminado", color=TEXT_MUTED, size=12),
        controls=[
            ft.Container(
                content=ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "sm": 6},
                            controls=[
                                ft.OutlinedButton(
                                    "Determinado (0-100%)",
                                    icon=ft.Icons.DOWNLOADING,
                                    on_click=send_determinate,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6},
                            controls=[
                                ft.OutlinedButton(
                                    "Indeterminado",
                                    icon=ft.Icons.AUTORENEW,
                                    on_click=send_indeterminate,
                                    expand=True,
                                )
                            ],
                        ),
                    ]
                ),
                padding=10,
            )
        ],
        **_tile_style(),
    )


@ft.component
def ButtonsSection(state: AppState):
    """Seção com botões para notificações com um, dois ou três botões de ação."""

    async def send_one_button(e):
        if _dev_simulate(state, "Notificação com 1 botão"):
            return
        try:

            def on_confirm():
                _show_snack("👍 Botão 'Confirmar' clicado")

            state.notifier.create(
                title="Confirmar ação", message="Deseja prosseguir?"
            ).add_button("Confirmar", on_confirm).send()
            state.increment()
            _show_snack("✅ Notificação com botão enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def send_two_buttons(e):
        if _dev_simulate(state, "Notificação com 2 botões"):
            return
        try:

            def on_accept():
                _show_snack("✅ Aceito!")

            def on_reject():
                _show_snack("❌ Rejeitado!")

            state.notifier.create(
                title="Solicitação de amizade", message="João quer ser seu amigo"
            ).add_button("Aceitar", on_accept).add_button("Rejeitar", on_reject).send()
            state.increment()
            _show_snack("✅ Notificação com 2 botões enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def send_three_buttons(e):
        if _dev_simulate(state, "Notificação com 3 botões"):
            return
        try:

            def on_yes():
                _show_snack("👍 Sim selecionado")

            def on_no():
                _show_snack("👎 Não selecionado")

            def on_maybe():
                _show_snack("🤔 Talvez selecionado")

            state.notifier.create(
                title="Enquete rápida", message="Você gostou da apresentação?"
            ).add_button("Sim", on_yes).add_button("Não", on_no).add_button(
                "Talvez", on_maybe
            ).send()
            state.increment()
            _show_snack("✅ Notificação com 3 botões enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    return ft.ExpansionTile(
        title=ft.Text("🎮 Com Botões de Ação", color=ft.Colors.WHITE),
        subtitle=ft.Text("Interatividade com callbacks", color=TEXT_MUTED, size=12),
        controls=[
            ft.Container(
                content=ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "1 Botão",
                                    icon=ft.Icons.TOUCH_APP,
                                    on_click=send_one_button,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "2 Botões",
                                    icon=ft.Icons.SWIPE,
                                    on_click=send_two_buttons,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "3 Botões",
                                    icon=ft.Icons.EXPAND,
                                    on_click=send_three_buttons,
                                    expand=True,
                                )
                            ],
                        ),
                    ]
                ),
                padding=10,
            )
        ],
        **_tile_style(),
    )


@ft.component
def ImagesSection(state: AppState):
    """Seção com botões para notificações com large icon, big picture ou ambas as imagens."""

    async def send_large_icon(e):
        if _dev_simulate(state, "Notificação com ícone grande"):
            return
        try:
            state.notifier.create(
                title="João Silva", message="Curtiu sua foto"
            ).set_large_icon("assets/profile.png").send()
            state.increment()
            _show_snack("✅ Notificação com ícone enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def send_big_picture(e):
        if _dev_simulate(state, "Notificação com big picture"):
            return
        try:
            state.notifier.create(
                title="Nova foto compartilhada",
                message="Maria compartilhou uma foto com você",
            ).set_big_picture("assets/post.png").send()
            state.increment()
            _show_snack("✅ Notificação com imagem enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def send_both_images(e):
        if _dev_simulate(state, "Notificação com ambas imagens"):
            return
        try:
            state.notifier.create(
                title="@usuario comentou",
                message="Que foto incrível! Adorei os detalhes.",
            ).set_large_icon("assets/profile.png").set_big_picture(
                "assets/photo.png"
            ).send()
            state.increment()
            _show_snack("✅ Notificação completa enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    return ft.ExpansionTile(
        title=ft.Text("🖼️ Com Imagens", color=ft.Colors.WHITE),
        subtitle=ft.Text("Ícones grandes e big pictures", color=TEXT_MUTED, size=12),
        controls=[
            ft.Container(
                content=ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "Ícone Grande",
                                    icon=ft.Icons.ACCOUNT_CIRCLE,
                                    on_click=send_large_icon,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "Big Picture",
                                    icon=ft.Icons.IMAGE,
                                    on_click=send_big_picture,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6, "md": 4},
                            controls=[
                                ft.OutlinedButton(
                                    "Ambas Imagens",
                                    icon=ft.Icons.COLLECTIONS,
                                    on_click=send_both_images,
                                    expand=True,
                                )
                            ],
                        ),
                    ]
                ),
                padding=10,
            )
        ],
        **_tile_style(),
    )


@ft.component
def TextSection(state: AppState):
    """Seção com botões para notificações no estilo inbox e big text expandido."""

    async def send_inbox(e):
        if _dev_simulate(state, "Notificação inbox style"):
            return
        try:
            state.notifier.create(
                title="5 novas mensagens", message="WhatsApp"
            ).add_line("João: E aí, bora codar hoje?").add_line(
                "Maria: Reunião às 15h, não esqueça!"
            ).add_line(
                "Pedro: PR aprovado! 🎉"
            ).add_line(
                "Ana: Parabéns pelo projeto!"
            ).add_line(
                "Carlos: Pizza depois do trabalho?"
            ).send()
            state.increment()
            _show_snack("✅ Notificação inbox enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def send_big_text(e):
        if _dev_simulate(state, "Notificação big text"):
            return
        try:
            long_text = (
                "O Python 3.13 traz melhorias significativas em performance, "
                "incluindo um novo GIL opcional que permite verdadeiro paralelismo "
                "em threads. Além disso, o interpretador agora é até 20% mais rápido "
                "em benchmarks comuns, e a gestão de memória foi otimizada para "
                "aplicações de longa duração. O suporte a type hints foi expandido "
                "com novos recursos do PEP 692, tornando o código mais seguro e "
                "expressivo. Experimente hoje mesmo e veja a diferença!"
            )
            state.notifier.create(
                title="Python 3.13 Lançado!",
                message="Confira as novidades desta versão",
            ).set_big_text(long_text).send()
            state.increment()
            _show_snack("✅ Notificação com texto expandido enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    return ft.ExpansionTile(
        title=ft.Text("📝 Estilos de Texto", color=ft.Colors.WHITE),
        subtitle=ft.Text("Inbox e textos expandidos", color=TEXT_MUTED, size=12),
        controls=[
            ft.Container(
                content=ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"xs": 12, "sm": 6},
                            controls=[
                                ft.OutlinedButton(
                                    "Inbox Style",
                                    icon=ft.Icons.INBOX,
                                    on_click=send_inbox,
                                    expand=True,
                                )
                            ],
                        ),
                        ft.Column(
                            col={"xs": 12, "sm": 6},
                            controls=[
                                ft.OutlinedButton(
                                    "Big Text",
                                    icon=ft.Icons.SUBJECT,
                                    on_click=send_big_text,
                                    expand=True,
                                )
                            ],
                        ),
                    ]
                ),
                padding=10,
            )
        ],
        **_tile_style(),
    )


@ft.component
def AdvancedSection(state: AppState):
    """Seção com recursos avançados: updates em tempo real, canal customizado e sequência completa."""

    async def send_realtime(e):
        if state.dev_mode:
            e.control.disabled = True
            ft.context.page.update()
            state.increment()
            _show_snack("🔧 DEV: Simulando updates em tempo real")
            await asyncio.sleep(3)
            e.control.disabled = False
            ft.context.page.update()
            return
        try:
            e.control.disabled = True
            ft.context.page.update()
            status = state.notifier.create(
                title="Processando tarefa", message="Iniciando processamento..."
            ).send()
            state.increment()
            _show_snack("⚙️ Iniciando updates em tempo real")
            await asyncio.sleep(1.5)
            status.update_message("Fase 1/3: Carregando dados...")
            await asyncio.sleep(1.5)
            status.update_message("Fase 2/3: Processando informações...")
            await asyncio.sleep(1.5)
            status.update_message("Fase 3/3: Finalizando...")
            await asyncio.sleep(1)
            status.update_title("Concluído!")
            status.update_message("Todas as fases completadas com sucesso")
            _show_snack("✅ Updates concluídos")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            ft.context.page.update()

    async def create_channel(e):
        if _dev_simulate(state, "Criação de canal customizado"):
            return
        try:
            FletNotify.create_channel(
                channel_id="app_custom",
                channel_name="Notificações Personalizadas",
                description="Canal com configurações customizadas",
                importance=NotificationImportance.HIGH,
            )
            await asyncio.sleep(0.5)
            state.notifier.send(
                title="Canal Customizado",
                message="Esta notificação usa um canal personalizado!",
                channel_id="app_custom",
            )
            state.increment()
            _show_snack("✅ Canal criado e notificação enviada")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    async def run_full_test(e):
        if state.dev_mode:
            e.control.disabled = True
            ft.context.page.update()
            _show_snack("🔧 DEV: Simulando sequência completa")
            for _ in range(5):
                state.increment()
                await asyncio.sleep(0.5)
            e.control.disabled = False
            ft.context.page.update()
            return
        try:
            e.control.disabled = True
            ft.context.page.update()
            _show_snack("🧪 Iniciando sequência completa...")
            state.notifier.send("Passo 1/5", "Notificação simples")
            state.increment()
            await asyncio.sleep(1)
            state.notifier.send("Passo 2/5", "Silenciosa", silent=True)
            state.increment()
            await asyncio.sleep(1)
            state.notifier.create("Passo 3/5", "Com botão").add_button(
                "OK", lambda: None
            ).send()
            state.increment()
            await asyncio.sleep(1)
            state.notifier.create("Passo 4/5", "Inbox").add_line("Linha 1").add_line(
                "Linha 2"
            ).add_line("Linha 3").send()
            state.increment()
            await asyncio.sleep(1)
            progress = (
                state.notifier.create("Passo 5/5", "Progress").with_progress().send()
            )
            state.increment()
            for i in range(0, 101, 25):
                await asyncio.sleep(0.5)
                progress.update_progress(i, message=f"{i}%")
            progress.remove_progress("Sequência completa!", show_briefly=True)
            _show_snack("✅ Sequência finalizada!")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)
        finally:
            e.control.disabled = False
            ft.context.page.update()

    return ft.ExpansionTile(
        title=ft.Text("🔬 Recursos Avançados", color=ft.Colors.WHITE),
        subtitle=ft.Text(
            "Updates em tempo real e canais customizados", color=TEXT_MUTED, size=12
        ),
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.OutlinedButton(
                            "Updates em Tempo Real",
                            icon=ft.Icons.UPDATE,
                            on_click=send_realtime,
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            "Criar Canal Customizado",
                            icon=ft.Icons.SETTINGS,
                            on_click=create_channel,
                            expand=True,
                        ),
                        ft.OutlinedButton(
                            "Executar Sequência Completa",
                            icon=ft.Icons.PLAY_CIRCLE,
                            on_click=run_full_test,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                padding=10,
            )
        ],
        **_tile_style(),
    )


@ft.component
def App():
    """Componente raiz do app, inicializa o estado e compõe todos os componentes da tela."""
    state, _ = ft.use_state(AppState())

    page = ft.context.page
    page.title = "Notificações"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 0
    page.bgcolor = BG
    page.dark_theme = _build_theme()
    page.theme_mode = ft.ThemeMode.DARK

    state.dev_mode = page.platform != ft.PagePlatform.ANDROID

    if not state.dev_mode and state.notifier is None:
        try:
            state.notifier = FletNotify(page)
            state.notifier.check_permission()
        except Exception:
            pass

    async def cancel_all(e):
        """Cancela todas as notificações ativas ao clicar no FAB."""
        if state.dev_mode:
            _show_snack("🔧 DEV: Cancelamento de todas as notificações")
            return
        try:
            FletNotify.cancel_all()
            _show_snack("🗑️ Todas as notificações foram canceladas")
        except Exception as ex:
            _show_snack(f"Erro: {ex}", error=True)

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.DELETE_SWEEP,
        on_click=cancel_all,
        tooltip="Limpar todas as notificações",
    )

    if state.dev_mode:
        _show_snack(f"⚠️ Modo desenvolvimento: executando em {page.platform.value}")

    return ft.SafeArea(
        content=ft.Column(
            [
                AppBar(state=state),
                ft.Container(
                    content=ft.Column(
                        [
                            SimpleSection(state=state),
                            ProgressSection(state=state),
                            ButtonsSection(state=state),
                            ImagesSection(state=state),
                            TextSection(state=state),
                            AdvancedSection(state=state),
                            ft.Container(height=80),
                        ],
                        spacing=10,
                    ),
                    padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                ),
            ]
        ),
        expand=True,
    )


def main(page: ft.Page):
    """Ponto de entrada do app, registra o componente raiz na página."""
    page.render(App)


ft.run(main, assets_dir="assets")
