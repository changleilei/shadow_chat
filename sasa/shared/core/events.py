# coding=utf8
"""================================
@Author: Mr.Chang
@Date  : 2021/7/30 3:38 下午
==================================="""
from sasa.shared.nlu.constants import INTENT_NAME_KEY, INTENT
from typing import (
    List,
    Dict,
    Text,
    Any,
    Type,
    Optional,
    TYPE_CHECKING,
    Iterable,
    cast,
    Tuple,
)

from abc import ABC

class Event:
    pass


class UserUttered(Event):
    """user 之前对bot说的话
    一个新的 'Turn' 将会在 Tracker中创建
    """
    type_name = 'user'

    def __int__(self,
                text: Optional[Text] = None,
                intent: Optional[Text] = None,
                entities: Optional[List[Dict]] = None,
                parse_data: Optional[Dict[Text, Any]] = None,
                timestamp: Optional[float] = None,
                input_channel: Optional[Text] = None,
                message_id: Optional[Text] = None,
                metadata: Optional[Dict] = None,
                user_text_for_featurization: Optional[bool] = None) -> None:
        """为用户的输入创建Event

        :param text:
        :param intent:
        :param entities:
        :param parse_data:
        :param timestamp:
        :param input_channel:
        :param message_id:
        :param metadata:
        :param user_text_for_featurization:
        :return:
        """
        self.text = text
        self.intent = intent if intent else {}
        self.entities = entities if entities else []
        self.input_channel = input_channel
        self.message_id = message_id

        super(UserUttered, self).__int__(timestamp, metadata)

        self.user_text_for_featurization = user_text_for_featurization

        if self.text and not self.intent_name:
            self.user_text_for_featurization = True
        elif self.intent_name and not self.text:
            self.user_text_for_featurization = False

        self.parse_data = {
            INTENT: self.intent
        }



    @property
    def intent_name(self) -> Optional[Text]:
        return self.intent.get(INTENT_NAME_KEY)


class AlwaysEqualEventMixin(Event, ABC):
    pass

class SessionStarted(AlwaysEqualEventMixin):
    pass