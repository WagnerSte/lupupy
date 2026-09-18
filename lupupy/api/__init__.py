"""The panel's web API, in two generations.

lupupy.api.current serves the XT1 Plus, XT2, XT3 and XT4, which share the
API the manufacturer documents. lupupy.api.legacy serves the first XT1,
which speaks an API of its own. Each has its facade, one method per REST
action, and a helper that turns the answers into what the library needs.

connect() picks the generation from the model the user configured. Nothing
else outside lupupy.api.legacy knows about the first XT1.
"""

from lupupy.api.current.helper import LupusecApi
from lupupy.api.current.undocumented_api import UndocumentedApi
from lupupy.api.data_models import LupusecModel, LupusecModelType
from lupupy.api.legacy.helper import LegacyLupusecApi
from lupupy.api.legacy.undocumented_legacy_api import UndocumentedLegacyApi


def connect(
    username: str, password: str, ip_address: str, model: LupusecModel
) -> "LupusecApi":
    """Connect to a panel with the helper for the model the user configured.

    Nothing is asked of the panel to find out which it is: the user knows,
    and a guess would only be wrong in the cases that matter.
    """
    if model.generation is LupusecModelType.XT1_Legacy:
        return LegacyLupusecApi(
            UndocumentedLegacyApi(username, password, ip_address), model
        )
    return LupusecApi(UndocumentedApi(username, password, ip_address), model)
