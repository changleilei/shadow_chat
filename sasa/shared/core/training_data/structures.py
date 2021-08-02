# coding=utf8
"""================================
@Author: Mr.Chang
@Date  : 2021/7/30 3:01 下午
==================================="""
import json
import uuid

from sasa.shared.core.conversation import Dialogue

from sasa.shared.core.trackers import DialogueStateTracker
from sasa.shared.exceptions import SasaCoreException
from sasa.shared.core.events import UserUttered, SessionStarted
from sasa.shared.core.events import Event
from sasa.shared.core.domain import Domain
from typing import (
    List,
    Text,
    Optional,
    Dict,
    Tuple,
    Any,
    Set,
    ValuesView,
    Union,
    Sequence,
    cast
)
import typing
import logging

if typing.TYPE_CHECKING:
    import networkx as nx

logger = logging.getLogger(__name__)

# checkpoint id 用于定义story的开始
STORY_START = 'STORY_START'

STORY_END = None

GENERATED_CHECKPOINT_PREFIX = 'GENR_'
CHECKPOINT_CYCLE_PREFIX = 'CYCL_'

GENERATED_HASH_LENGTH = 5

GORM_PREFIX = 'form: '

# storystep id 的前缀，每创建一次实例，会自动加1，可用来排序
STEP_COUNT = 1


# class EventTypeError(SasaCoreException, ValueError):


class Checkpoint(object):

    def __init__(self,
                 name: Optional[Text],
                 conditions: Optional[Dict[Text, Any]] = None
                 ) -> None:
        self.name = name
        self.conditions = conditions if conditions else {}

    def as_story_string(self) -> Text:
        dumper_conds = json.dumps(self.conditions) if self.conditions else ""
        return f'{self.name}{dumper_conds}'

    def filter_trackers(self,
                        trackers: List[DialogueStateTracker]) -> List[DialogueStateTracker]:
        """ 过滤不符合conditions的tracker"""

        if not self.conditions:
            return trackers

        for slot_name, slot_value in self.conditions.items():
            trackers = [t for t in trackers if t.get_slot(slot_name) == slot_value]
        return trackers

    def __repr__(self):
        return 'Checkpoint(name={!r}, conditions={}'.format(
            self.name, json.dumps(self.conditions)
        )


class StoryStep:

    def __init__(self,
                 block_name: Optional[Text] = None,
                 start_checkpoints: Optional[List[Checkpoint]] = None,
                 end_checkpoints: Optional[List[Checkpoint]] = None,
                 events: Optional[List[Union[Event, List[Event]]]] = None,
                 source_name: Optional[Text] = None) -> None:
        self.end_checkpoints = end_checkpoints if end_checkpoints else []
        self.start_checkpoints = start_checkpoints if start_checkpoints else []
        self.events = events if events else []
        self.block_name = block_name
        self.source_name = source_name

        global STEP_COUNT
        self.id = '{}_{}'.format(STEP_COUNT, uuid.uuid4().hex)
        STEP_COUNT += 1

    def create_copy(self, use_new_id: bool) -> "StoryStep":
        copied = StoryStep(
            self.block_name,
            self.start_checkpoints,
            self.end_checkpoints,
            self.events[:],
            self.source_name
        )
        if not use_new_id:
            copied.id = self.id
        return copied

    def add_user_message(self, user_message: UserUttered) -> None:
        self.add_event(user_message)

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def add_events(self, events: List[Event]) -> None:
        self.events.append(events)

    @staticmethod
    def _checkpoint_string(story_step_element: Checkpoint) -> Text:
        return f'> {story_step_element.as_story_string()}\n'

    @staticmethod
    def _user_string(story_step_element: UserUttered, e2e: bool) -> Text:
        return f'* {story_step_element.as_story_string(e2e)}\n'

    @staticmethod
    def _bot_string(story_step_element: Event) -> Text:
        return f'   - {story_step_element.as_story_string()}\n'

    @staticmethod
    def _or_string(story_step_element: Sequence[Event], e2e: bool) -> Text:
        for event in story_step_element:
            if not isinstance(event, UserUttered):
                raise EventTypeError(
                    "OR statement events must be of type 'UserUttered'."
                )

            story_step_element = cast(Sequence[UserUttered], story_step_element)

            result = " OR ".join(
                [element.as_story_string(e2e) for element in story_step_element]
            )
        return f'* {result}\n'

    def as_story_string(self, flat: bool=False, e2e: bool = False) -> Text:
        """折叠，去除caption和checkpoint"""
        if flat:
            result = ""
        else:
            result = f"\n## {self.block_name}\n"
            for checkpoint in self.start_checkpoints:
                if checkpoint.name != STORY_START:
                    result += self._checkpoint_string(checkpoint)

        for event in self.events:
            if (self.is_action_listen(event)
                    or self.is_action_session_start(event)
                    or isinstance(event, SessionStarted)):
                continue
            if isinstance(event, UserUttered):
                result += self._user_string(event, e2e)
            elif isinstance(event, Event):
                converted = event.as_story_string()
                if converted:
                    result += self._bot_string(event)
            elif isinstance(event, list):
                result += self._or_string(event, e2e)
            else:
                raise Exception(f"Unexpected element in story step: {event}")

        if not flat:
            for checkpoint in self.end_checkpoints:
                result += self._checkpoint_string(checkpoint)

        return result

    @staticmethod
    def is_action_listen(event) -> bool:
        pass

    @staticmethod
    def is_action_session_start(event) -> bool:
        pass


class RuleStep(StoryStep):
    """ 建模Rule """

    def __init__(self,
                 block_name: Optional[Text] = None,
                 start_checkpoints: Optional[List[Checkpoint]] = None,
                 end_checkpoints: Optional[List[Checkpoint]] = None,
                 events: Optional[List[Union[Event, List[Event]]]] = None,
                 source_name: Optional[Text] = None,
                 condition_events_indices: Optional[Set[int]] = None
                 ) -> None:
        super().__init__(block_name, start_checkpoints, end_checkpoints, events, source_name)
        self.condition_events_indices = (condition_events_indices if condition_events_indices else ())


    def create_copy(self, use_new_id: bool) -> "StoryStep":
        copied = RuleStep(
            self.block_name,
            self.start_checkpoints,
            self.end_checkpoints,
            self.events[:],
            self.source_name,
            self.condition_events_indices
        )
        if not use_new_id:
            copied.id = self.id
        return copied

    def __repr__(self) -> Text:
        return (
            "RuleStep("
            "block_name={!r},"
            "start_checkpoints={!r},"
            "end_checkpoints={!r},"
            "events={!r})".format(
                self.block_name,
                self.start_checkpoints,
                self.end_checkpoints,
                self.events
            )
        )

    def get_rules_condition(self) -> List[Event]:
        return [
            event for event_id, event in enumerate(self.events) if event_id in self.condition_events_indices
        ]

    def get_rules_events(self) -> List[Event]:
        return [
            event for event_id, event in enumerate(self.events) if event_id in self.condition_events_indices
        ]

    def add_event_as_condition(self, event: Event) -> None:
        """ 添加event到Rule中作为condition的一部分

        :param event: Event
        :return:
        """
        self.condition_events_indices.add((len(self.events)))
        self.events.append(event)


class Story:

    def __init__(self,
                 story_steps: List[StoryStep] = None,
                 story_name: Optional[Text] = None) -> None:
        self.story_name = story_name
        self.story_steps = story_steps if story_steps else []

    @staticmethod
    def from_events(events: List[Event], story_name: Optional[Text] = None) -> "Story":
        """ 从一个event 列表中生成story"""

        story_step = StoryStep(story_name)
        for event in events:
            story_step.add_event(event)

        return Story([story_step], story_name)

    def as_dialogue(self, sender_id: Text, domain: Domain) -> Dialogue:
        events = []
        # for step in self.story_steps:
        #     events.append(
        #         step.
        #     )
        pass
