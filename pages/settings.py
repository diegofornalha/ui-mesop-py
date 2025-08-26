import asyncio

import mesop as me

from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.host_agent_service import UpdateApiKey
from state.state import AppState, SettingsState
from styles.colors import PRIMARY, SUCCESS, TEXT_ON_PRIMARY


def on_selection_change_output_types(e: me.SelectSelectionChangeEvent):
    s = me.state(SettingsState)
    s.output_mime_types = e.values


def on_api_key_change(e: me.InputBlurEvent):
    s = me.state(AppState)
    s.api_key = e.value


@me.stateclass
class UpdateStatus:
    """Status para atualização da chave API"""

    show_success: bool = False


async def update_api_key(e: me.ClickEvent):
    yield  # Allow UI to update

    state = me.state(AppState)
    update_status = me.state(UpdateStatus)

    if state.api_key.strip():
        success = await UpdateApiKey(state.api_key)
        if success:
            update_status.show_success = True

            # Hide success message after 3 seconds
            yield
            await asyncio.sleep(3)
            update_status.show_success = False

    yield  # Allow UI to update after operation completes


def settings_page_content():
    """Conteúdo da Página de Configurações."""
    settings_state = me.state(SettingsState)
    app_state = me.state(AppState)
    update_status = me.state(UpdateStatus)

    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Configurações', 'settings'):
                pass
            with me.box(
                style=me.Style(
                    display='flex',
                    justify_content='space-between',
                    flex_direction='column',
                    gap=30,
                )
            ):
                # Claude Configuration Section
                if hasattr(app_state, 'uses_claude') and app_state.uses_claude:
                    with me.box(
                        style=me.Style(
                            display='flex',
                            flex_direction='column',
                            margin=me.Margin(bottom=30),
                        )
                    ):
                        me.text(
                            'Claude Assistant - Configuração',
                            type='headline-6',
                            style=me.Style(
                                margin=me.Margin(bottom=15),
                                font_family='Google Sans',
                            ),
                        )

                        with me.box(
                            style=me.Style(
                                display='flex',
                                flex_direction='column',
                                gap=10,
                                padding=me.Padding(top=15, bottom=15, left=15, right=15),
                                background='#f0f4f8',
                                border_radius=8,
                            )
                        ):
                            with me.box(
                                style=me.Style(
                                    display='flex',
                                    align_items='center',
                                    gap=10,
                                )
                            ):
                                me.icon(
                                    'check_circle',
                                    style=me.Style(
                                        color=SUCCESS,
                                        font_size=24,
                                    ),
                                )
                                me.text(
                                    'Claude está ativo e funcionando',
                                    style=me.Style(
                                        font_weight='bold',
                                        color='#2e7d32',
                                    ),
                                )
                            
                            me.text(
                                'O Claude utiliza a CLI local e não requer chave de API.',
                                style=me.Style(
                                    margin=me.Margin(top=10),
                                    color='#666',
                                ),
                            )
                            
                            me.text(
                                'Todas as conversas são processadas localmente através do Claude Code SDK.',
                                style=me.Style(
                                    margin=me.Margin(top=5),
                                    color='#666',
                                ),
                            )


                # Legacy API Key Settings (Hidden when using Claude)
                elif not app_state.uses_vertex_ai and not (hasattr(app_state, 'uses_claude') and app_state.uses_claude):
                    with me.box(
                        style=me.Style(
                            display='flex',
                            flex_direction='column',
                            margin=me.Margin(bottom=30),
                        )
                    ):
                        me.text(
                            'Configuração de API Key',
                            type='headline-6',
                            style=me.Style(
                                margin=me.Margin(bottom=15),
                                font_family='Google Sans',
                            ),
                        )
                        
                        me.text(
                            'Nenhum provedor de IA configurado. Para usar Claude, defina USE_CLAUDE=TRUE no ambiente.',
                            style=me.Style(
                                color='#666',
                                margin=me.Margin(bottom=10),
                            ),
                        )
                
                # Add spacing instead of divider with style
                with me.box(
                    style=me.Style(margin=me.Margin(top=10, bottom=10))
                ):
                    me.divider()

                # Output Types Section
                me.select(
                    label='Tipos de Saída Suportados',
                    options=[
                        me.SelectOption(label='Imagem', value='image/*'),
                        me.SelectOption(
                            label='Texto (Simples)', value='text/plain'
                        ),
                    ],
                    on_selection_change=on_selection_change_output_types,
                    style=me.Style(width=500),
                    multiple=True,
                    appearance='outline',
                    value=settings_state.output_mime_types,
                )
