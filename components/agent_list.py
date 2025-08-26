import mesop as me
import pandas as pd

from a2a.types import AgentCard
from state.agent_state import AgentState


@me.component
def agents_list(
    agents: list[AgentCard],
):
    """Componente da lista de agentes."""
    df_data: dict[str, list[str | bool | None]] = {
        'Endereço': [],
        'Nome': [],
        'Descrição': [],
        'Organização': [],
        'Modos de Entrada': [],
        'Modos de Saída': [],
        'Extensões': [],
        'Streaming': [],
    }
    for agent_info in agents:
        df_data['Endereço'].append(agent_info.url)
        df_data['Nome'].append(agent_info.name)
        df_data['Descrição'].append(agent_info.description)
        df_data['Organização'].append(
            getattr(agent_info.provider, 'organization', '') if hasattr(agent_info, 'provider') and agent_info.provider else ''
        )
        df_data['Modos de Entrada'].append(', '.join(getattr(agent_info, 'defaultInputModes', getattr(agent_info, 'default_input_modes', []))))
        df_data['Modos de Saída'].append(
            ', '.join(getattr(agent_info, 'defaultOutputModes', getattr(agent_info, 'default_output_modes', [])))
        )
        df_data['Streaming'].append(getattr(agent_info.capabilities, 'streaming', False) if hasattr(agent_info, 'capabilities') and agent_info.capabilities else False)
        df_data['Extensões'].append(
            ', '.join([ext.uri for ext in agent_info.capabilities.extensions])
            if hasattr(agent_info, 'capabilities') and agent_info.capabilities and hasattr(agent_info.capabilities, 'extensions') and agent_info.capabilities.extensions
            else ''
        )
    df = pd.DataFrame(
        pd.DataFrame(df_data),
        columns=[
            'Endereço',
            'Nome',
            'Descrição',
            'Organização',
            'Modos de Entrada',
            'Modos de Saída',
            'Extensões',
            'Streaming',
        ],
    )
    with me.box(
        style=me.Style(
            display='flex',
            justify_content='space-between',
            flex_direction='column',
        )
    ):
        me.table(
            df,
            header=me.TableHeader(sticky=True),
            columns={
                'Endereço': me.TableColumn(sticky=True),
                'Nome': me.TableColumn(sticky=True),
                'Descrição': me.TableColumn(sticky=True),
            },
        )
        with me.content_button(
            type='raised',
            on_click=add_agent,
            key='new_agent',
            style=me.Style(
                display='flex',
                flex_direction='row',
                gap=5,
                align_items='center',
                margin=me.Margin(top=10),
            ),
        ):
            me.icon(icon='upload')


def add_agent(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Manipulador do botão importar agente."""
    state = me.state(AgentState)
    state.agent_dialog_open = True
