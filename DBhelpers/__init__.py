from .DBbaseline import (
    setup_mysql_database,
    get_mysql_connection,
)
from .DBcreateTables import (
    create_tables,
    newTableClass,
    newTableConnectionData,
    newTableDocuments,
    newTableIPs,
    newTablePersonalData,
    newTableUsers,
    newTableResults,
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
    get_user_profile_tier1,
    get_user_profile_tier2,
    get_user_quiz,
    getDataFromCellNumber,
    getDataFromEmail,
    getDataFromIPcreated,
    getDataFromNIF,
    getUserIdFromEmail,
    getHashFromEmail,
    getEmailFromUsername,
    getQuestionFromQid,
    getQuestionIDsForYear,
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
    "setup_mysql_database",
    "create_tables",
    "newTableClass",
    "newTableConnectionData",
    "newTableDocuments",
    "newTableIPs",
    "newTablePersonalData",
    "newTableUsers",
    "newTableResults",
    "insertNewClass",
    "insertNewConnectionData",
    "insertNewDocument",
    "insertNewIP",
    "insertNewPersonalData",
    "insertNewUser",
    "get_user_profile_tier1",
    "get_user_profile_tier2",
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
    "getQuestionFromQid",
    "getQuestionIDsForYear",
    "get_mysql_connection",
]