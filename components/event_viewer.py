import asyncio

import mesop as me
import pandas as pd

from state.host_agent_service import GetEvents, convert_event_to_state


def flatten_content(content: list[tuple[str, str]]) -> str:
    parts = []
    for p in content:
        if p[1] == 'text/plain' or p[1] == 'application/json':
            parts.append(p[0])
        else:
            parts.append(p[1])

    return '\n'.join(parts)


@me.component
def event_list():
    """Componente da lista de eventos"""
    df_data = {
        'ID da Conversa': [],
        'Ator': [],
        'Função': [],
        'ID': [],
        'Conteúdo': [],
    }
    events = asyncio.run(GetEvents())
    for e in events:
        event = convert_event_to_state(e)
        df_data['ID da Conversa'].append(event.contextId)  # Usar camelCase
        df_data['Função'].append(event.role)
        df_data['ID'].append(event.id)
        df_data['Conteúdo'].append(flatten_content(event.content))
        df_data['Ator'].append(event.actor)
    if not df_data['ID da Conversa']:
        me.text('Nenhum evento encontrado')
        return
    df = pd.DataFrame(
        pd.DataFrame(df_data),
        columns=['ID da Conversa', 'Ator', 'Função', 'ID', 'Conteúdo'],
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
                'ID da Conversa': me.TableColumn(sticky=True),
                'Ator': me.TableColumn(sticky=True),
                'Função': me.TableColumn(sticky=True),
                'ID': me.TableColumn(sticky=True),
                'Conteúdo': me.TableColumn(sticky=True),
            },
        )
