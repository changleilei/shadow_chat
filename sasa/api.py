import sasa.shared.constants
import typing

if typing.TYPE_CHECKING:
    from typing import Any, Text, Dict, Union, List, Optional, NoReturn
    from sasa.model_training import TrainingResult
    import asyncio


def run(
        model: "Text",
        endpoint: "Text",
        connector: "Text" = None,
        credentials: "Text"= None,
        **kwargs: "Dict[Text, Any]"
)-> "NoReturn":
    """Runs a sasa model

    :param model: Path to model archive
    :param endpoint: Path to endpoint file
    :param connector: connector which should be use
    :param credentials: path to channel credentials file
    :param kwargs: Additional arguments which are passed to 'sasa.core.run.serve_application'
    :return:
    """
    import sasa.core.run
    from sasa.core.utils import AvailableEndpoints
    from sasa.shared.utils.cli import print_warning
    import sasa.shared.utils.common
    from sasa.shared.constants import DOCS_BASE_URL

    _endpoints = AvailableEndpoints.read_endpoints(endpoint)

    if not connector and not credentials:
        connector = 'rest'
        print_warning()

    kwargs = sasa.shared.utils.common.minimal_kwargs(
        kwargs, sasa.core.run.serve_application
    )
    sasa.core.run.serve_application()



def train():
    pass


def test():
    pass