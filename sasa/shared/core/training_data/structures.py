# coding=utf8
"""================================
@Author: Mr.Chang
@Date  : 2021/7/30 3:01 下午
==================================="""
import json
import uuid

from sasa.shared.core.trackers import DialogueStateTracker
from sasa.shared.exceptions import SasaCoreException
from sasa.shared.core.events import UserUttered
from sasa.shared.core.events import Event
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
                 start_checkpoint: Optional[List[Checkpoint]] = None,
                 end_checkpoint: Optional[List[Checkpoint]] = None,
                 events: Optional[List[Union[Event, List[Event]]]] = None,
                 source_name: Optional[Text] = None) -> None:
        self.end_checkpoint = end_checkpoint if end_checkpoint else []
        self.start_checkpoint = start_checkpoint if start_checkpoint else []
        self.events = events if events else []
        self.block_name = block_name
        self.source_name = source_name

        global STEP_COUNT
        self.id = '{}_{}'.format(STEP_COUNT, uuid.uuid4().hex)
        STEP_COUNT += 1

    def create_copy(self,
                    use_new_id: bool) -> "StoryStep":
        copied = StoryStep(
            self.block_name,
            self.start_checkpoint,
            self.end_checkpoint,
            self.events[:],
            self.source_name
        )
        if not use_new_id:
            copied.id = self.id
        return copied

    def add_user_message(self, user_message: UserUttered) -> None:
        pass
