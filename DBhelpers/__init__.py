from .DBbaseline import getAllUsers
from .DBcreateTables import (
    handle_tables,
    newTableClass,
    newTableConnectionData,
    newTableDocuments,
    newTableIPs,
    newTablePersonalData,
    newTableUsers,
    )
from .DBinsertTables import (
    insertNewClass,
    insertNewConnectionData,
    insertNewDocument,
    insertNewIP,
    insertNewPersonalData,
    insertNewUser,
    )
from .DBselectTables import (
    get_user_profile,
    get_user_quiz,
    getDataFromCellNumber,
    getDataFromEmail,
    getDataFromIPcreated,
    getDataFromNIF,
    getUserIdFromEmail,
    getHashFromEmail,
    getEmailFromUsername,
    )
from .DBupdateTables import (refresh_last_login_and_ip)

from .DBloadQuiz import (
    loadQanswers,
    loadQaulas,
    loadQcsvFiles,
    loadQlinks,
    loadQtemas,
    )

# from .DBmodifyTables import updateValue

__all__ = [
    "getAllUsers",
    "handle_tables",
    "newTableClass",
    "newTableConnectionData",
    "newTableDocuments",
    "newTableIPs",
    "newTablePersonalData",
    "newTableUsers",
    "insertNewClass",
    "insertNewConnectionData",
    "insertNewDocument",
    "insertNewIP",
    "insertNewPersonalData",
    "insertNewUser",
    "get_user_profile",
    "getDataFromCellNumber",
    "getDataFromEmail",
    "getDataFromIPcreated",
    "getDataFromNIF",
    "getUserIdFromEmail",
    "refresh_last_login_and_ip",
    "getHashFromEmail",
    "getEmailFromUsername",
    "get_user_quiz",
    "loadQanswers",
    "loadQaulas",
    "loadQcsvFiles",
    "loadQlinks",
    "loadQtemas",
]