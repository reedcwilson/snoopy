from ctypes import windll
import win32ts
import win32con
import win32process


def run_as_cur_user(process, args):
    session_id = windll.kernel32.WTSGetActiveConsoleSessionId()
    token = win32ts.WTSQueryUserToken(session_id)
    win32process.CreateProcessAsUser(
        token,
        process,
        args,
        None,
        None,
        True,
        win32con.NORMAL_PRIORITY_CLASS,
        None,
        None,
        win32process.STARTUPINFO())
