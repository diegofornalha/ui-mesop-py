import asyncio
import base64
import datetime
import json
import os
import uuid

import httpx

from a2a.types import (
    AgentCard,
    Artifact,
    DataPart,
    FilePart,
    FileWithBytes,
    FileWithUri,
    Message,
    Part,
    Role,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)
from google.adk import Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events.event import Event as ADKEvent
from google.adk.events.event_actions import EventActions as ADKEventActions
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from host_agent import HostAgent
from remote_agent_connection import TaskCallbackArg
from utils.agent_card import get_agent_card

from service.server.application_manager import ApplicationManager
from service.types import Conversation, Event


class ADKHostManager(ApplicationManager):
    """An implementation of memory based management with fake agent actions

    This implements the interface of the ApplicationManager to plug into
    the AgentServer. This acts as the service contract that the Mesop app
    uses to send messages to the agent and provide information for the frontend.
    """

    def __init__(
        self,
        http_client: httpx.AsyncClient,
        api_key: str = '',
        uses_vertex_ai: bool = False,
    ):
        self._conversations: list[Conversation] = []
        self._messages: list[Message] = []
        self._tasks: list[Task] = []
        self._events: dict[str, Event] = {}
        self._pending_messageids: list[str] = []
        self._agents: list[AgentCard] = []
        self._artifact_chunks: dict[str, list[Artifact]] = {}
        self._session_service = InMemorySessionService()
        self._artifact_service = InMemoryArtifactService()
        self._memory_service = InMemoryMemoryService()
        self._host_agent = HostAgent([], http_client, self.task_callback)
        self._context_to_conversation: dict[str, str] = {}
        self.user_id = 'test_user'
        self.app_name = 'A2A'
        self.api_key = api_key or os.environ.get('GOOGLE_API_KEY', '')
        self.uses_vertex_ai = (
            uses_vertex_ai
            or os.environ.get('GOOGLE_GENAI_USE_VERTEXAI', '').upper() == 'TRUE'
        )

        # Set environment variables based on auth method
        if self.uses_vertex_ai:
            os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'TRUE'

        elif self.api_key:
            # Use API key authentication
            os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = 'FALSE'
            os.environ['GOOGLE_API_KEY'] = self.api_key

        self._initialize_host()

        # Map of message id to task id
        self._task_map: dict[str, str] = {}
        # Map to manage 'lost' message ids until protocol level id is introduced
        self._next_id: dict[
            str, str
        ] = {}  # dict[str, str]: previous message to next message

    def _initialize_host(self):
        agent = self._host_agent.create_agent()
        self._host_runner = Runner(
            app_name=self.app_name,
            agent=agent,
            artifact_service=self._artifact_service,
            session_service=self._session_service,
            memory_service=self._memory_service,
        )

    async def create_conversation(self) -> Conversation:
        session = await self._session_service.create_session(
            app_name=self.app_name, user_id=self.user_id
        )
        conversationid = session.id
        c = Conversation(conversationid=conversationid, isactive=True)
        self._conversations.append(c)
        return c

    def update_api_key(self, api_key: str):
        """Update the API key and reinitialize the host if needed"""
        if api_key and api_key != self.api_key:
            self.api_key = api_key

            # Only update if not using Vertex AI
            if not self.uses_vertex_ai:
                os.environ['GOOGLE_API_KEY'] = api_key
                # Reinitialize host with new API key
                self._initialize_host()

                # Map of message id to task id
                self._task_map = {}

    def sanitize_message(self, message: Message) -> Message:
        if message.context_id:
            conversation = self.get_conversation(message.context_id)
            if not conversation:
                return message
            # Check if the last event in the conversation was tied to a task.
            if conversation.messages:
                taskid = conversation.messages[-1].taskid
                if taskid and task_still_open(
                    next(
                        filter(lambda x: x and x.id == taskid, self._tasks),
                        None,
                    )
                ):
                    message.taskid = taskid
        return message

    async def process_message(self, message: Message):
        print(f"[DEBUG] Processing message: {message.messageid}")
        messageid = message.messageid
        if messageid:
            self._pending_messageids.append(messageid)
            print(f"[DEBUG] Added to pending: {messageid}")
        contextid = message.context_id
        print(f"[DEBUG] Context ID: {contextid}")
        conversation = self.get_conversation(contextid)
        print(f"[DEBUG] Got conversation: {conversation is not None}")
        self._messages.append(message)
        if conversation:
            conversation.messages.append(message)
        self.add_event(
            Event(
                id=str(uuid.uuid4()),
                actor='user',
                content=message,
                timestamp=datetime.datetime.utcnow().timestamp(),
            )
        )
        final_event = None
        # Determine if a task is to be resumed.
        session = await self._session_service.get_session(
            app_name='A2A', user_id='test_user', session_id=contextid
        )
        taskid = message.taskid
        # Update state must happen in an event
        state_update = {
            'taskid': taskid,
            'context_id': contextid,
            'messageid': message.messageid,
        }
        # Need to upsert session state now, only way is to append an event.
        await self._session_service.append_event(
            session,
            ADKEvent(
                id=ADKEvent.new_id(),
                author='host_agent',
                invocation_id=ADKEvent.new_id(),
                actions=ADKEventActions(state_delta=state_update),
            ),
        )
        print(f"[DEBUG] Starting runner for context: {contextid}")
        try:
            async for event in self._host_runner.run_async(
                user_id=self.user_id,
                session_id=contextid,
                new_message=self.adk_content_from_message(message),
            ):
                print(f"[DEBUG] Received event from runner: {event.author}")
                if (
                    event.actions.state_delta
                    and 'taskid' in event.actions.state_delta
                ):
                    taskid = event.actions.state_delta['taskid']
                self.add_event(
                Event(
                    id=event.id,
                    actor=event.author,
                    content=await self.adk_content_to_message(
                        event.content, contextid, taskid
                    ),
                    timestamp=event.timestamp,
                )
                )
                final_event = event
        except Exception as e:
            print(f"[ERROR] Exception in runner: {str(e)}")
            import traceback
            traceback.print_exc()
            final_event = None
        
        response: Message | None = None
        if final_event:
            if (
                final_event.actions.state_delta
                and 'taskid' in final_event.actions.state_delta
            ):
                taskid = event.actions.state_delta['taskid']
            final_event.content.role = 'model'
            response = await self.adk_content_to_message(
                final_event.content, contextid, taskid
            )
            self._messages.append(response)

        if conversation and response:
            conversation.messages.append(response)
            print(f"[DEBUG] Added response to conversation: {contextid}")
        else:
            print(f"[DEBUG] No response or conversation for: {contextid}")
        
        if messageid in self._pending_messageids:
            self._pending_messageids.remove(messageid)
            print(f"[DEBUG] Removed from pending: {messageid}")

    def add_task(self, task: Task):
        self._tasks.append(task)

    def update_task(self, task: Task):
        for i, t in enumerate(self._tasks):
            if t.id == task.id:
                self._tasks[i] = task
                return

    def task_callback(self, task: TaskCallbackArg, agent_card: AgentCard):
        self.emit_event(task, agent_card)
        if isinstance(task, TaskStatusUpdateEvent):
            current_task = self.add_or_get_task(task)
            current_task.status = task.status
            self.attach_message_to_task(task.status.message, current_task.id)
            self.insert_message_history(current_task, task.status.message)
            self.update_task(current_task)
            return current_task
        if isinstance(task, TaskArtifactUpdateEvent):
            current_task = self.add_or_get_task(task)
            self.process_artifact_event(current_task, task)
            self.update_task(current_task)
            return current_task
        # Otherwise this is a Task, either new or updated
        if not any(filter(lambda x: x and x.id == task.id, self._tasks)):
            self.attach_message_to_task(task.status.message, task.id)
            self.add_task(task)
            return task
        self.attach_message_to_task(task.status.message, task.id)
        self.update_task(task)
        return task

    def emit_event(self, task: TaskCallbackArg, agent_card: AgentCard):
        content = None
        contextid = task.context_id
        if isinstance(task, TaskStatusUpdateEvent):
            if task.status.message:
                content = task.status.message
            else:
                content = Message(
                    parts=[Part(root=TextPart(text=str(task.status.state)))],
                    role=Role.agent,
                    messageid=str(uuid.uuid4()),
                    contextid=contextid,
                    taskid=task.taskid,
                )
        elif isinstance(task, TaskArtifactUpdateEvent):
            content = Message(
                parts=task.artifact.parts,
                role=Role.agent,
                messageid=str(uuid.uuid4()),
                contextid=contextid,
                taskid=task.taskid,
            )
        elif task.status and task.status.message:
            content = task.status.message
        elif task.artifacts:
            parts = []
            for a in task.artifacts:
                parts.extend(a.parts)
            content = Message(
                parts=parts,
                role=Role.agent,
                messageid=str(uuid.uuid4()),
                taskid=task.id,
                contextid=contextid,
            )
        else:
            content = Message(
                parts=[Part(root=TextPart(text=str(task.status.state)))],
                role=Role.agent,
                messageid=str(uuid.uuid4()),
                taskid=task.id,
                contextid=contextid,
            )
        if content:
            self.add_event(
                Event(
                    id=str(uuid.uuid4()),
                    actor=agent_card.name,
                    content=content,
                    timestamp=datetime.datetime.utcnow().timestamp(),
                )
            )

    def attach_message_to_task(self, message: Message | None, taskid: str):
        if message:
            self._task_map[message.messageid] = taskid

    def insert_message_history(self, task: Task, message: Message | None):
        if not message:
            return
        if task.history is None:
            task.history = []
        messageid = message.messageid
        if not messageid:
            return
        if task.history and (
            task.status.message
            and task.status.message.messageid
            not in [x.messageid for x in task.history]
        ):
            task.history.append(task.status.message)
        elif not task.history and task.status.message:
            task.history = [task.status.message]
        else:
            print(
                'Message id already in history',
                task.status.message.messageid if task.status.message else '',
                task.history,
            )

    def add_or_get_task(self, event: TaskCallbackArg):
        taskid = None
        if isinstance(event, Message):
            taskid = event.taskid
        elif isinstance(event, Task):
            taskid = event.id
        else:
            taskid = event.taskid
        if not taskid:
            taskid = str(uuid.uuid4())
        current_task = next(
            filter(lambda x: x.id == taskid, self._tasks), None
        )
        if not current_task:
            contextid = event.context_id
            current_task = Task(
                id=taskid,
                # initialize with submitted
                status=TaskStatus(state=TaskState.submitted),
                artifacts=[],
                contextid=contextid,
            )
            self.add_task(current_task)
            return current_task

        return current_task

    def process_artifact_event(
        self, current_task: Task, task_update_event: TaskArtifactUpdateEvent
    ):
        artifact = task_update_event.artifact
        if not task_update_event.append:
            # received the first chunk or entire payload for an artifact
            if (
                task_update_event.last_chunk is None
                or task_update_event.last_chunk
            ):
                # last_chunk bit is missing or is set to true, so this is the entire payload
                # add this to artifacts
                if not current_task.artifacts:
                    current_task.artifacts = []
                current_task.artifacts.append(artifact)
            else:
                # this is a chunk of an artifact, stash it in temp store for assembling
                if artifact.artifact_id not in self._artifact_chunks:
                    self._artifact_chunks[artifact.artifact_id] = []
                self._artifact_chunks[artifact.artifact_id].append(artifact)
        else:
            # we received an append chunk, add to the existing temp artifact
            current_temp_artifact = self._artifact_chunks[artifact.artifact_id][
                -1
            ]
            # TODO handle if current_temp_artifact is missing
            current_temp_artifact.parts.extend(artifact.parts)
            if task_update_event.last_chunk:
                if current_task.artifacts:
                    current_task.artifacts.append(current_temp_artifact)
                else:
                    current_task.artifacts = [current_temp_artifact]
                del self._artifact_chunks[artifact.artifact_id][-1]

    def add_event(self, event: Event):
        self._events[event.id] = event

    def get_conversation(
        self, conversationid: str | None
    ) -> Conversation | None:
        if not conversationid:
            return None
        return next(
            filter(
                lambda c: c and c.conversationid == conversationid,
                self._conversations,
            ),
            None,
        )

    def get_pending_messages(self) -> list[tuple[str, str]]:
        rval = []
        for messageid in self._pending_messageids:
            if messageid in self._task_map:
                taskid = self._task_map[messageid]
                task = next(
                    filter(lambda x: x.id == taskid, self._tasks), None
                )
                if not task:
                    rval.append((messageid, ''))
                elif task.history and task.history[-1].parts:
                    if len(task.history) == 1:
                        rval.append((messageid, 'Working...'))
                    else:
                        part = task.history[-1].parts[0]
                        # Handle both dict and object formats
                        if isinstance(part, dict):
                            if 'root' in part:
                                p = part['root']
                            else:
                                p = part
                        elif hasattr(part, 'root'):
                            p = part.root
                        else:
                            p = part
                            
                        # Get text content safely
                        text = None
                        if hasattr(p, 'text') or (isinstance(p, dict) and 'text' in p):
                            text = p.get('text') if isinstance(p, dict) else getattr(p, 'text', None)
                        
                        rval.append(
                            (
                                messageid,
                                text if text else 'Working...',
                            )
                        )
            else:
                rval.append((messageid, ''))
        return rval

    def register_agent(self, url):
        agent_data = get_agent_card(url)
        if not agent_data.url:
            agent_data.url = url
        self._agents.append(agent_data)
        self._host_agent.register_agent_card(agent_data)
        # Now update the host agent definition
        self._initialize_host()

    @property
    def agents(self) -> list[AgentCard]:
        return self._agents

    @property
    def conversations(self) -> list[Conversation]:
        return self._conversations

    @property
    def tasks(self) -> list[Task]:
        return self._tasks

    @property
    def events(self) -> list[Event]:
        return sorted(self._events.values(), key=lambda x: x.timestamp)

    def adk_content_from_message(self, message: Message) -> types.Content:
        parts: list[types.Part] = []
        for p in message.parts:
            # Handle both dict and object formats
            if isinstance(p, dict):
                # Se é um dict com 'root', pegar o conteúdo do root
                if 'root' in p:
                    part = p['root']
                else:
                    part = p
            elif hasattr(p, 'root'):
                part = p.root
            else:
                part = p
            
            # Determine the type of part
            # Check if it's a TextPart, DataPart, or FilePart
            if hasattr(part, 'text') or (isinstance(part, dict) and 'text' in part):
                # It's a TextPart
                text = part.get('text') if isinstance(part, dict) else getattr(part, 'text')
                if text:
                    parts.append(types.Part.from_text(text=text))
            elif hasattr(part, 'data') or (isinstance(part, dict) and 'data' in part):
                # It's a DataPart
                data = part.get('data') if isinstance(part, dict) else getattr(part, 'data')
                json_string = json.dumps(data)
                parts.append(types.Part.from_text(text=json_string))
            elif hasattr(part, 'file') or (isinstance(part, dict) and 'file' in part):
                # It's a FilePart
                file_obj = part.get('file') if isinstance(part, dict) else getattr(part, 'file')
                if isinstance(file_obj, FileWithUri):
                    parts.append(
                        types.Part.from_uri(
                            file_uri=file_obj.uri,
                            mime_type=file_obj.mime_type,
                        )
                    )
                else:
                    parts.append(
                        types.Part.from_bytes(
                            data=file_obj.bytes.encode('utf-8'),
                            mime_type=file_obj.mime_type,
                        )
                    )
        return types.Content(parts=parts, role=message.role)

    async def adk_content_to_message(
        self,
        content: types.Content,
        contextid: str | None,
        taskid: str | None,
    ) -> Message:
        parts: list[Part] = []
        if not content.parts:
            return Message(
                parts=[],
                role=content.role if content.role == Role.user else Role.agent,
                contextid=contextid,
                taskid=taskid,
                messageid=str(uuid.uuid4()),
            )
        for part in content.parts:
            if part.text:
                # try parse as data
                try:
                    data = json.loads(part.text)
                    parts.append(Part(root=DataPart(data=data)))
                except:  # noqa: E722
                    parts.append(Part(root=TextPart(text=part.text)))
            elif part.inline_data:
                parts.append(
                    Part(
                        root=FilePart(
                            file=FileWithBytes(
                                bytes=part.inline_data.decode('utf-8'),
                                mime_type=part.file_data.mime_type,
                            ),
                        )
                    )
                )
            elif part.file_data:
                parts.append(
                    Part(
                        root=FilePart(
                            file=FileWithUri(
                                uri=part.file_data.file_uri,
                                mime_type=part.file_data.mime_type,
                            )
                        )
                    )
                )
            # These aren't managed by the A2A message structure, these are internal
            # details of ADK, we will simply flatten these to json representations.
            elif part.video_metadata:
                parts.append(
                    Part(root=DataPart(data=part.video_metadata.model_dump()))
                )
            elif part.thought:
                parts.append(Part(root=TextPart(text='thought')))
            elif part.executable_code:
                parts.append(
                    Part(root=DataPart(data=part.executable_code.model_dump()))
                )
            elif part.function_call:
                parts.append(
                    Part(root=DataPart(data=part.function_call.model_dump()))
                )
            elif part.function_response:
                parts.extend(
                    await self._handle_function_response(
                        part, contextid, taskid
                    )
                )
            else:
                raise ValueError('Unexpected content, unknown type')
        return Message(
            role=content.role if content.role == Role.user else Role.agent,
            parts=parts,
            contextid=contextid,
            taskid=taskid,
            messageid=str(uuid.uuid4()),
        )

    async def _handle_function_response(
        self, part: types.Part, contextid: str | None, taskid: str | None
    ) -> list[Part]:
        parts = []
        try:
            for p in part.function_response.response['result']:
                if isinstance(p, str):
                    parts.append(Part(root=TextPart(text=p)))
                elif isinstance(p, dict):
                    if 'kind' in p and p['kind'] == 'file':
                        parts.append(Part(root=FilePart(**p)))
                    else:
                        parts.append(Part(root=DataPart(data=p)))
                elif isinstance(p, DataPart):
                    if 'artifact-file-id' in p.data:
                        file_part = await self._artifact_service.load_artifact(
                            user_id=self.user_id,
                            session_id=contextid,
                            app_name=self.app_name,
                            filename=p.data['artifact-file-id'],
                        )
                        file_data = file_part.inline_data
                        base64_data = base64.b64encode(file_data.data).decode(
                            'utf-8'
                        )
                        parts.append(
                            Part(
                                root=FilePart(
                                    file=FileWithBytes(
                                        bytes=base64_data,
                                        mime_type=file_data.mime_type,
                                        name='artifact_file',
                                    )
                                )
                            )
                        )
                    else:
                        parts.append(Part(root=DataPart(data=p.data)))
                else:
                    parts.append(Part(root=TextPart(text='Unknown content')))
        except Exception as e:
            print("Couldn't convert to messages:", e)
            parts.append(
                Part(root=DataPart(data=part.function_response.model_dump()))
            )
        return parts

    def process_message_threadsafe(
        self, message: Message, loop: asyncio.AbstractEventLoop
    ):
        """Safely run process_message from a thread using the given event loop."""
        future = asyncio.run_coroutine_threadsafe(
            self.process_message(message), loop
        )
        return (
            future  # You can call future.result() to get the result if needed
        )


def get_message_id(m: Message | None) -> str | None:
    if not m or not m.metadata or 'messageid' not in m.metadata:
        return None
    return m.metadata['messageid']


def task_still_open(task: Task | None) -> bool:
    if not task:
        return False
    return task.status.state in [
        TaskState.submitted,
        TaskState.working,
        TaskState.input_required,
    ]
