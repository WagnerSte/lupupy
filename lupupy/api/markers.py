"""The marker for REST actions the manufacturer does not document.

Used by the facades of both generations, lupupy.api.current and
lupupy.api.legacy.
"""

def undocumented(source: str):
    """Mark a call the manufacturer's specification does not describe.

    source says where the knowledge came from, so a reader can weigh it.
    """

    def decorate(method):
        method.undocumented_source = source
        return method

    return decorate
