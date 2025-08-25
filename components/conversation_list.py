import mesop as me
import pandas as pd

from state.host_agent_service import CreateConversation
from state.state import AppState, StateConversation


@me.component
def conversation_list(conversations: list[StateConversation]):
    """Componente da lista de conversas"""
    df_data: dict[str, list[str | int]] = {
        'ID': [],
        'Nome': [],
        'Status': [],
        'Mensagens': [],
    }
    for conversation in conversations:
        df_data['ID'].append(conversation.conversationId)
        df_data['Nome'].append(conversation.conversationName)
        df_data['Status'].append('Aberta' if conversation.isActive else 'Fechada')
        df_data['Mensagens'].append(len(conversation.messageIds))
    df = pd.DataFrame(
        pd.DataFrame(df_data), columns=['ID', 'Nome', 'Status', 'Mensagens']
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
            on_click=on_click,
            header=me.TableHeader(sticky=True),
            columns={
                'ID': me.TableColumn(sticky=True),
                'Nome': me.TableColumn(sticky=True),
                'Status': me.TableColumn(sticky=True),
                'Mensagens': me.TableColumn(sticky=True),
            },
        )
        with me.content_button(
            type='raised',
            on_click=add_conversation,
            key='new_conversation',
            style=me.Style(
                display='flex',
                flex_direction='row',
                gap=5,
                align_items='center',
                margin=me.Margin(top=10),
            ),
        ):
            me.icon(icon='add')


async def add_conversation(e: me.ClickEvent):  # pylint: disable=unused-argument
    """Manipulador do botão adicionar conversa"""
    response = await CreateConversation()
    me.state(AppState).messages = []
    me.navigate(
        '/conversation',
        query_params={'conversationid': response.conversationId},
    )
    yield


def on_click(e: me.TableClickEvent):
    state = me.state(AppState)
    conversation = state.conversations[e.row_index]
    state.current_conversation_id = conversation.conversationId
    me.query_params.update({'conversationid': conversation.conversationId})
    me.navigate('/conversation', query_params=me.query_params)
    yield
