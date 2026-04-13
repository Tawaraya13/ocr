import ctypes
import ctypes.util
import logging
import subprocess
import sys
from typing import Any, cast

from PySide6 import QtWidgets


from screenshot import models
from screenshot.main import get_available_handlers

try:
    from ocr.screenshot.handlers import dbus_portal

except ImportError:
    dbus_portal = cast(Any, None)


logger = logging.getLogger(__name__)



def _dbus_portal_has_screenshot_permission(
    request_portal_dialog: type[QtWidgets.QDialog],
) -> bool:
    if not dbus_portal:
        raise ModuleNotFoundError(
            "Portal permission requested, but dbus_portal could not been imported!"
        )
    result = []
    try:
        result = dbus_portal.capture()
    except (PermissionError, TimeoutError) as exc:
        logger.warning("Screenshot permissions on Wayland seem missing.", exc_info=exc)

    if len(result) > 0:
        return True

    logger.info("Trying to request permissions via dialog.")
    permissions_granted = request_portal_dialog(dbus_portal.capture()).exec()
    if not permissions_granted:
        logger.warning("Requesting screenshot permissions on Wayland failed!")
        return False

    return True


def has_screenshot_permission(request_portal_dialog: type[QtWidgets.QDialog]) -> bool:
    """Check and ask for screenshot permissions.

    Args:
        request_portal_dialog: Qt Dialog which takes as init arg a callable which
            queries dbus portal for screenshot. The dialog should return True, if
            screenshots could be retrieved or False if not.

    Returns:
        If a handler with screenshot permissions was found.
    """
    logger.debug("Checking screenshot permission")

    if sys.platform == "win32":
        return True

    if sys.platform == "darwin":
        return _macos_has_screenshot_permission()

    handlers = get_available_handlers()
    primary_handler = handlers[0] if handlers else None
    if not primary_handler:
        raise RuntimeError(
            "Could not identify a screenshot method for this system configuration."
        )

    if primary_handler == models.Handler.DBUS_PORTAL:
        return _dbus_portal_has_screenshot_permission(request_portal_dialog)

    return True
