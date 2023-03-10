import importlib
import re
import time
from platform import python_version as y
from sys import argv
from typing import Optional

from pyrogram import __version__ as pyrover
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram import __version__ as telever
from telegram.error import (
    BadRequest,
    ChatMigrated,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.ext.dispatcher import DispatcherHandlerStop, run_async
from telegram.utils.helpers import escape_markdown
from telethon import __version__ as tlhver

import FallenRobot.modules.sql.users_sql as sql
from FallenRobot import (
    BOT_NAME,
    BOT_USERNAME,
    CERT_PATH,
    DONATION_LINK,
    LOGGER,
    OWNER_ID,
    PORT,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    URL,
    WEBHOOK,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
)

# needed to dynamically load modules
# NOTE: Module order is not guaranteed, specify that in the config file!
from FallenRobot.modules import ALL_MODULES
from FallenRobot.modules.helper_funcs.chat_status import is_user_admin
from FallenRobot.modules.helper_funcs.misc import paginate_modules


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


PM_START_TEXT = """
เน ๐๐ ๐๐./๐๐๐๐ {} ๐ 

            ๐น๐๐๐ฅ๐๐จ๐ฆ๐ ๐๐๐ซ๐๐น

โง ๐?๐ฌ๐ฆ๐๐๐ {} ๐

โป แดสแด แดแดsแด แดฉแดแดกแดสาแดส แดแดสแดษขสแดแด ษขสแดแดแดฉ แดแดษดแดษขแดแดแดษดแด สแดแด แดกษชแดส sแดแดแด แดแดกแดsแดแดแด แดษดแด แดsแดาแดส าแดแดแดแดสแดs.

๐๐ ๐๐๐ ๐๐๐ ๐๐๐๐ ๐๐ ๐๐ ๐๐๐๐๐ ๐๐๐๐๐๐๐ ๐๐๐๐๐๐
โโโโโโโโโโโโโโโโโโโโ
โฃโ [MISS ROSE ROBOT](https://t.me/miss_rose_robot) ๐น
โฃโ [TG MANAGER ROBOT](https://t.me/tg_manager_robot) ๐ซ
โฃโ [THE KANISHKA BOT](https://t.me/the_kanishka_bot) ๐ฅ
โฃโ ๐๐๐๐๐ ๐๐๐ ๐๐๐ 
โโโโโโโโโโโโโโโโโโโโ

โคออออโข๐๐๐จ๐ฐ๐๐ซ๐๐ ๐๐ฒ โโ๐[@THE_VIP_BOY](https://t.me/the_vip_boy)โฆโอ๐ฎ๐ณ๐

เน *แดสษชแดแด แดษด แดสแด ๐๐๐ ๐๐๐๐๐๐๐๐ สแดแดแดแดษด* .
"""

buttons = [
    [
        InlineKeyboardButton(
            text="๐๏ธ๐๐๐๐๐ ๐๐๐๐ & ๐๐๐ ๐๐๐๐๐๏ธ",
            url=f"https://t.me/TG_MANAGER_ROBOT?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="๐ฅต๐๐๐ ๐๐๐๐๐๐๐๐๐ฅต", callback_data="help_back"),
    ],
    [
        InlineKeyboardButton(text="โก๐๐๐๐โก", url=f"https://t.me/Tg_Friendss"),
        InlineKeyboardButton(text="๐ฅ๐๐๐๐ ๐๐๐ฅ", url=f"https://t.me/THE_VIP_BOY"),
        InlineKeyboardButton(text="๐ซ๐๐๐๐๐ซ", url=f"https://t.me/vip_creators"),
    ],
    [
        InlineKeyboardButton(
            text="๐ฅณ๐๐๐ ๐๐๐๐/๐๐๐๐๐๐๐คฉ",
            url=f"https://github.com/THE-VIP-BOY-OP/VIP-ROBOT",
        ),
    ],
]

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

HELP_STRINGS = f"""
*ยป {BOT_NAME} แดxแดสแดsษชแด?แด ๊ฐแดแดแดแดสแดs*

๐๐๐ ๐๐๐๐ ๐๐ ๐๐ ๐๐๐๐๐ โช [๐ฅใTG FRIENDSใ๐ฅ](https://t.me/TG_FRIENDSS)
                   
โคออออโข๐๐๐จ๐ฐ๐๐ซ๐๐ ๐๐ฒ โโ๐[@THE_VIP_BOY](https://t.me/the_vip_boy)โฆโอ๐ฎ๐ณ๐
"""
	          

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []
CHAT_SETTINGS = {}
USER_SETTINGS = {}

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("FallenRobot.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module


# do not async
def send_help(chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    dispatcher.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )


@run_async
def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))
    if update.effective_chat.type == "private":
        if len(args) >= 1:
            if args[0].lower() == "help":
                send_help(update.effective_chat.id, HELP_STRINGS)
            elif args[0].lower().startswith("ghelp_"):
                mod = args[0].lower().split("_", 1)[1]
                if not HELPABLE.get(mod, False):
                    return
                send_help(
                    update.effective_chat.id,
                    HELPABLE[mod].__help__,
                    InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text="โ", callback_data="help_back")]]
                    ),
                )

            elif args[0].lower().startswith("stngs_"):
                match = re.match("stngs_(.*)", args[0].lower())
                chat = dispatcher.bot.getChat(match.group(1))

                if is_user_admin(chat, update.effective_user.id):
                    send_settings(match.group(1), update.effective_user.id, False)
                else:
                    send_settings(match.group(1), update.effective_user.id, True)

            elif args[0][1:].isdigit() and "rules" in IMPORTED:
                IMPORTED["rules"].send_rules(update, args[0], from_pm=True)

        else:
            first_name = update.effective_user.first_name
            update.effective_message.reply_sticker(
                "CAADBQAD8wcAAnSt4FePem-s4NJDjwI"
            )
            update.effective_message.reply_text(
                PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN,
                timeout=60,
            )
    else:
        update.effective_message.reply_photo(
            START_IMG,
            caption="ษช แดแด แดสษชแด?แด สแดสส !\n<b>ษช แดษชแดษด'แด sสแดแดแด sษชษดแดแดโ:</b> <code>{}</code>".format(
                uptime
            ),
            parse_mode=ParseMode.HTML,
        )


def error_handler(update, context):
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    message = (
        "An exception was raised while handling an update\n"
        "<pre>update = {}</pre>\n\n"
        "<pre>{}</pre>"
    ).format(
        html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False)),
        html.escape(tb),
    )

    if len(message) >= 4096:
        message = message[:4096]
    # Finally, send the message
    context.bot.send_message(chat_id=OWNER_ID, text=message, parse_mode=ParseMode.HTML)


# for test purposes
def error_callback(update: Update, context: CallbackContext):
    error = context.error
    try:
        raise error
    except Unauthorized:
        print("no nono1")
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("no nono2")
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut:
        print("no nono3")
        # handle slow connection problems
    except NetworkError:
        print("no nono4")
        # handle other connection problems
    except ChatMigrated as err:
        print("no nono5")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def help_button(update, context):
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)

    print(query.message.chat.id)

    try:
        if mod_match:
            module = mod_match.group(1)
            text = (
                "ยป *แดแด?แดษชสแดสสแด แดแดแดแดแดษดแดs ๊ฐแดสโโ* *{}* :\n".format(
                    HELPABLE[module].__mod_name__
                )
                + HELPABLE[module].__help__
            )
            query.message.edit_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="โ", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(curr_page - 1, HELPABLE, "help")
                ),
            )

        elif next_match:
            next_page = int(next_match.group(1))
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELPABLE, "help")
                ),
            )

        elif back_match:
            query.message.edit_text(
                text=HELP_STRINGS,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELPABLE, "help")
                ),
            )

        context.bot.answer_callback_query(query.id)

    except BadRequest:
        pass


@run_async
def Fallen_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "fallen_":
        uptime = get_readable_time((time.time() - StartTime))
        query.message.edit_text(
            text=f"*สแดส,*๐ฅ\n  *แดสษชs ษชs {BOT_NAME}*"
            "\n*แด แดแดแดกแดส๊ฐแดส ษขสแดแดแด แดแดษดแดษขแดแดแดษดแด สแดแด สแดษชสแด แดแด สแดสแด สแดแด แดแดษดแดษขแด สแดแดส ษขสแดแดแด แดแด๊ฑษชสส แดษดแด แดแด แดสแดแดแดแดแด สแดแดส ษขสแดแดแด ๊ฐสแดแด ๊ฑแดแดแดแดแดส๊ฑ แดษดแด ๊ฑแดแดแดแดแดส๊ฑ.*"
            "\n*แดกสษชแดแดแดษด ษชษด แดฉสแดสแดษด แดกษชแดส sวซสแดสแดสแดแดส แดษดแด แดแดษดษขแดแดส แดs แดแดแดแดสแดsแด.*"
            "\n\nโโโโโโโโโโโโโโโโโโโโ"
            f"\n*โป แดแดฉแดษชแดแด ยป* {uptime}"
            f"\n*โป แดsแดสs ยป* {sql.num_users()}"
            f"\n*โป แดสแดแดs ยป* {sql.num_chats()}"
            "\nโโโโโโโโโโโโโโโโโโโโ"
            "\n\nโฒ  ษช แดแดษด สแด๊ฑแดสษชแดแด แด๊ฑแดส๊ฑ."
            "\nโฒ  ษช สแดแด?แด แดษด แดแดแด?แดษดแดแดแด แดษดแดษช-๊ฐสแดแดแด ๊ฑส๊ฑแดแดแด."
            "\nโฒ  ษช แดแดษด ษขสแดแดแด แด๊ฑแดส๊ฑ แดกษชแดส แดแด๊ฑแดแดแดษชแดขแดสสแด แดกแดสแดแดแดแด แดแด๊ฑ๊ฑแดษขแด๊ฑ แดษดแด แดแด?แดษด ๊ฑแดแด แด ษขสแดแดแด'๊ฑ สแดสแด๊ฑ."
            "\nโฒ  ษช แดแดษด แดกแดสษด แด๊ฑแดส๊ฑ แดษดแดษชส แดสแดส สแดแดแดส แดแดx แดกแดสษด๊ฑ, แดกษชแดส แดแดแดส แดสแดแดแด๊ฐษชษดแดแด แดแดแดษชแดษด๊ฑ ๊ฑแดแดส แด๊ฑ สแดษด, แดแดแดแด, แดษชแดแด, แดแดแด."
            "\nโฒ  ษช สแดแด?แด แด ษดแดแดแด แดแดแดแดษชษดษข ๊ฑส๊ฑแดแดแด, สสแดแดแดสษช๊ฑแด๊ฑ, แดษดแด แดแด?แดษด แดสแดแดแดแดแดสแดษชษดแดแด สแดแดสษชแด๊ฑ แดษด แดแดสแดแดษชษด แดแดสแดกแดสแด๊ฑ."
            f"\n\nโป แดสษชแดแด แดษด แดสแด สแดแดแดแดษดs ษขษชแด?แดษด สแดสแดแดก าแดส ษขแดแดแดษชษดษข สแดsษชแด สแดสแดฉ แดษดแด ษชษดาแด แดสแดแดแด {BOT_NAME}.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="sแดแดฉแดฉแดสแด", callback_data="fallen_support"
                        ),
                        InlineKeyboardButton(
                            text="แดแดแดแดแดษดแดs", callback_data="help_back"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="แดแดแด?แดสแดแดฉแดส", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="sแดแดสแดแด",
                            callback_data="source_",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="โ", callback_data="fallen_back"),
                    ],
                ]
            ),
        )
    elif query.data == "fallen_support":
        query.message.edit_text(
            text="*เน แดสษชแดแด แดษด แดสแด สแดแดแดแดษดs ษขษชแด?แดษด สแดสแดแดก แดแด ษขแดแด สแดสแดฉ แดษดแด แดแดสแด ษชษดาแดสแดแดแดษชแดษด แดสแดแดแด แดแด.*"
            f"\n\nษชา สแดแด าแดแดษดแด แดษดส สแดษข ษชษด {BOT_NAME} แดส ษชา สแดแด แดกแดษดษดแด ษขษชแด?แด าแดแดแดสแดแดแด แดสแดแดแด แดสแด {BOT_NAME}, แดฉสแดแดsแด สแดแดฉแดสแด ษชแด แดแด sแดแดฉแดฉแดสแด แดสแดแด.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="sแดแดฉแดฉแดสแด", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="แดแดฉแดแดแดแดs", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="แดแดแด?แดสแดแดฉแดส", url=f"tg://user?id={OWNER_ID}"
                        ),
                        InlineKeyboardButton(
                            text="ษขษชแดสแดส",
                            callback_data="https://github.com/TheAnonymous2005",
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="โ", callback_data="fallen_"),
                    ],
                ]
            ),
        )
    elif query.data == "fallen_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )


@run_async
def Source_about_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "source_":
        query.message.edit_text(
            text=f"""
*สแดส,
 แดสษชs ษชs {BOT_NAME},
แดษด แดแดฉแดษด sแดแดสแดแด แดแดสแดษขสแดแด ษขสแดแดแดฉ แดแดษดแดษขแดแดแดษดแด สแดแด.*

แดกสษชแดแดแดษด ษชษด แดฉสแดสแดษด แดกษชแดส แดสแด สแดสแดฉ แดา : [แดแดสแดแดสแดษด](https://github.com/LonamiWebs/Telethon)
[แดฉสสแดษขสแดแด](https://github.com/pyrogram/pyrogram)
[แดฉสแดสแดษด-แดแดสแดษขสแดแด-สแดแด](https://github.com/python-telegram-bot/python-telegram-bot)
แดษดแด แดsษชษดษข [sวซสแดสแดสแดแดส](https://www.sqlalchemy.org) แดษดแด [แดแดษดษขแด](https://cloud.mongodb.com) แดs แดแดแดแดสแดsแด.


*สแดสแด ษชs แดส sแดแดสแดแด แดแดแดแด :* [ษขษชแดสแดส](https://github.com/TheAnonymous2005/FallenRobot)


{BOT_NAME} ษชs สษชแดแดษดsแดแด แดษดแดแดส แดสแด [แดษชแด สษชแดแดษดsแด](https://github.com/TheAnonymous2005/FallenRobot/blob/master/LICENSE).
ยฉ 2022 - 2023 [@แดแดแด?ษชสsสแดแดแด?แดษดแดา](https://t.me/{SUPPORT_CHAT}), แดสส สษชษขสแดs สแดsแดสแด?แดแด.
""",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="โ", callback_data="source_back")]]
            ),
        )
    elif query.data == "source_back":
        first_name = update.effective_user.first_name
        query.message.edit_text(
            PM_START_TEXT.format(escape_markdown(first_name), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
            disable_web_page_preview=False,
        )


@run_async
def get_help(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    args = update.effective_message.text.split(None, 1)

    # ONLY send help in PM
    if chat.type != chat.PRIVATE:
        if len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
            module = args[1].lower()
            update.effective_message.reply_text(
                f"Contact me in PM to get help of {module.capitalize()}",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="สแดสแดโ",
                                url="t.me/{}?start=ghelp_{}".format(
                                    context.bot.username, module
                                ),
                            )
                        ]
                    ]
                ),
            )
            return
        update.effective_message.reply_text(
            "ยป แดสแดแดsแด แดษด แดแดฉแดษชแดษด าแดส ษขแดแดแดษชษดษข สแดสแดฉ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="แดแดฉแดษด ษชษด แดฉสษชแด?แดแดแด",
                            url="https://t.me/{}?start=help".format(
                                context.bot.username
                            ),
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="แดแดฉแดษด สแดสแด",
                            callback_data="help_back",
                        )
                    ],
                ]
            ),
        )
        return

    elif len(args) >= 2 and any(args[1].lower() == x for x in HELPABLE):
        module = args[1].lower()
        text = (
            "Here is the available help for the *{}* module:\n".format(
                HELPABLE[module].__mod_name__
            )
            + HELPABLE[module].__help__
        )
        send_help(
            chat.id,
            text,
            InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="โ", callback_data="help_back")]]
            ),
        )

    else:
        send_help(chat.id, HELP_STRINGS)


def send_settings(chat_id, user_id, user=False):
    if user:
        if USER_SETTINGS:
            settings = "\n\n".join(
                "*{}*:\n{}".format(mod.__mod_name__, mod.__user_settings__(user_id))
                for mod in USER_SETTINGS.values()
            )
            dispatcher.bot.send_message(
                user_id,
                "These are your current settings:" + "\n\n" + settings,
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any user specific settings available :'(",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if CHAT_SETTINGS:
            chat_name = dispatcher.bot.getChat(chat_id).title
            dispatcher.bot.send_message(
                user_id,
                text="Which module would you like to check {}'s settings for?".format(
                    chat_name
                ),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )
        else:
            dispatcher.bot.send_message(
                user_id,
                "Seems like there aren't any chat settings available :'(\nSend this "
                "in a group chat you're admin in to find its current settings!",
                parse_mode=ParseMode.MARKDOWN,
            )


@run_async
def settings_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = update.effective_user
    bot = context.bot
    mod_match = re.match(r"stngs_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"stngs_prev\((.+?),(.+?)\)", query.data)
    next_match = re.match(r"stngs_next\((.+?),(.+?)\)", query.data)
    back_match = re.match(r"stngs_back\((.+?)\)", query.data)
    try:
        if mod_match:
            chat_id = mod_match.group(1)
            module = mod_match.group(2)
            chat = bot.get_chat(chat_id)
            text = "*{}* has the following settings for the *{}* module:\n\n".format(
                escape_markdown(chat.title), CHAT_SETTINGS[module].__mod_name__
            ) + CHAT_SETTINGS[module].__chat_settings__(chat_id, user.id)
            query.message.reply_text(
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="โ",
                                callback_data="stngs_back({})".format(chat_id),
                            )
                        ]
                    ]
                ),
            )

        elif prev_match:
            chat_id = prev_match.group(1)
            curr_page = int(prev_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        curr_page - 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif next_match:
            chat_id = next_match.group(1)
            next_page = int(next_match.group(2))
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                "Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(chat.title),
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(
                        next_page + 1, CHAT_SETTINGS, "stngs", chat=chat_id
                    )
                ),
            )

        elif back_match:
            chat_id = back_match.group(1)
            chat = bot.get_chat(chat_id)
            query.message.reply_text(
                text="Hi there! There are quite a few settings for {} - go ahead and pick what "
                "you're interested in.".format(escape_markdown(chat.title)),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, CHAT_SETTINGS, "stngs", chat=chat_id)
                ),
            )

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
    except BadRequest as excp:
        if excp.message not in [
            "Message is not modified",
            "Query_id_invalid",
            "Message can't be deleted",
        ]:
            LOGGER.exception("Exception in settings buttons. %s", str(query.data))


@run_async
def get_settings(update: Update, context: CallbackContext):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]

    # ONLY send settings in PM
    if chat.type != chat.PRIVATE:
        if is_user_admin(chat, user.id):
            text = "Click here to get this chat's settings, as well as yours."
            msg.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sแดแดแดษชษดษขsโ",
                                url="t.me/{}?start=stngs_{}".format(
                                    context.bot.username, chat.id
                                ),
                            )
                        ]
                    ]
                ),
            )
        else:
            text = "Click here to check your settings."

    else:
        send_settings(chat.id, user.id, True)


@run_async
def donate(update: Update, context: CallbackContext):
    user = update.effective_message.from_user
    chat = update.effective_chat  # type: Optional[Chat]
    bot = context.bot
    if chat.type == "private":
        update.effective_message.reply_text(
            DONATE_STRING, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True
        )

        if OWNER_ID != 1356469075 and DONATION_LINK:
            update.effective_message.reply_text(
                f"ยป แดสแด แดแดแด?แดสแดแดฉแดส แดา {BOT_NAME} sแดสแดแด แดแดแดแด ษชs [แดษดแดษดสแดแดแดs](https://t.me/anonymous_was_bot)."
                f"\n\nสแดแด สแดแด แดแดษด แดสsแด แดแดษดแดแดแด แดแด แดสแด แดฉแดสsแดษด แดแดสสแดษดแดสส สแดษดษดษชษดษข แดแด : [สแดสแด]({DONATION_LINK})",
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

    else:
        try:
            bot.send_message(
                user.id,
                DONATE_STRING,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True,
            )

            update.effective_message.reply_text(
                "I've PM'ed you about donating to my creator!"
            )
        except Unauthorized:
            update.effective_message.reply_text(
                "Contact me in PM first to get donation information."
            )


def migrate_chats(update: Update, context: CallbackContext):
    msg = update.effective_message  # type: Optional[Message]
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    LOGGER.info("Migrating from %s, to %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    LOGGER.info("Successfully migrated!")
    raise DispatcherHandlerStop


def main():

    if SUPPORT_CHAT is not None and isinstance(SUPPORT_CHAT, str):
        try:
            dispatcher.bot.send_photo(
                f"@{SUPPORT_CHAT}",
                photo=START_IMG,
                caption=f"""
ใค๐ฅ {BOT_NAME} ษชs แดสษชแด?แด สแดสส...

โโขโโโโโโงโโฆโโงโโโโโโขโ
ใคโ **แดสแดสแดษด :** `{y()}`
ใคโ **สษชสสแดสส :** `{telever}`
ใคโ **แดแดสแดแดสแดษด :** `{tlhver}`
ใคโ **แดฉสสแดษขสแดแด :** `{pyrover}`
โโขโโโโโโงโโฆโโงโโโโโโขโ""",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(
                f"Bot isn't able to send message to @{SUPPORT_CHAT}, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)

    start_handler = CommandHandler("start", start)

    help_handler = CommandHandler("help", get_help)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_.*")

    settings_handler = CommandHandler("settings", get_settings)
    settings_callback_handler = CallbackQueryHandler(settings_button, pattern=r"stngs_")

    about_callback_handler = CallbackQueryHandler(
        Fallen_about_callback, pattern=r"fallen_"
    )
    source_callback_handler = CallbackQueryHandler(
        Source_about_callback, pattern=r"source_"
    )

    donate_handler = CommandHandler("donate", donate)
    migrate_handler = MessageHandler(Filters.status_update.migrate, migrate_chats)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(about_callback_handler)
    dispatcher.add_handler(source_callback_handler)
    dispatcher.add_handler(settings_handler)
    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(settings_callback_handler)
    dispatcher.add_handler(migrate_handler)
    dispatcher.add_handler(donate_handler)

    dispatcher.add_error_handler(error_callback)

    if WEBHOOK:
        LOGGER.info("Using webhooks.")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)

        if CERT_PATH:
            updater.bot.set_webhook(url=URL + TOKEN, certificate=open(CERT_PATH, "rb"))
        else:
            updater.bot.set_webhook(url=URL + TOKEN)

    else:
        LOGGER.info("Using long polling.")
        updater.start_polling(timeout=15, read_latency=4, clean=True)

    if len(argv) not in (1, 3, 4):
        telethn.disconnect()
    else:
        telethn.run_until_disconnected()

    updater.idle()


if __name__ == "__main__":
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    telethn.start(bot_token=TOKEN)
    pbot.start()
    main()
