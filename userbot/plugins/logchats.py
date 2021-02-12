# pm and tagged messages logger for catuserbot by @mrconfused (@sandy1709)
import asyncio

from telethon import events

from . import BOTLOG, BOTLOG_CHATID, LOGS
from .sql_helper import no_log_pms_sql


class LOG_CHATS:
    def __init__(self):
        self.RECENT_USER = None
        self.NEWPM = None
        self.COUNT = 0


LOG_CHATS_ = LOG_CHATS()


@bot.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def monito_p_m_s(event):
    if not Config.PM_LOGGR_BOT_API_ID:
        return
    sender = await event.get_sender()
    if Config.NO_LOG_P_M_S and not sender.bot:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id) and chat.id != 777000:
            if LOG_CHATS.RECENT_USER != chat.id:
                LOG_CHATS.RECENT_USER = chat.id
                if LOG_CHATS.NEWPM:
                    if LOG_CHATS.COUNT > 1:
                        await LOG_CHATS.NEWPM.edit(
                            LOG_CHATS.NEWPM.text.replace(
                                "new message", f"{LOG_CHATS.COUNT} messages"
                            )
                        )
                    else:
                        await LOG_CHATS.NEWPM.edit(
                            LOG_CHATS.NEWPM.text.replace(
                                "new message", f"{LOG_CHATS.COUNT} message"
                            )
                        )
                    LOG_CHATS.COUNT = 0
                LOG_CHATS.NEWPM = await event.client.send_message(
                    Config.PM_LOGGR_BOT_API_ID,
                    f"👤{_format.mentionuser(sender.first_name , sender.id)} has sent a new message \nId : `{chat.id}`",
                )
            try:
                if event.message:
                    await event.client.forward_messages(
                        Config.PM_LOGGR_BOT_API_ID, event.message, silent=True
                    )
                LOG_CHATS.COUNT += 1
            except Exception as e:
                LOGS.warn(str(e))


@bot.on(events.NewMessage(incoming=True, func=lambda e: e.mentioned))
async def log_tagged_messages(event):
    hmm = await event.get_chat()
    from .afk import AFK_
    if (
        (no_log_pms_sql.is_approved(hmm.id))
        or (not Config.PM_LOGGR_BOT_API_ID)
        or ("on" in AFK_.USERAFK_ON)
        or (await event.get_sender() and (await event.get_sender()).bot)):
        return
    full = None
    try:
        full = await event.client.get_entity(event.message.from_id)
    except Exception as e:
        LOGS.info(str(e))
    messaget = media_type(event)
    resalt = f"#TAGS \n<b>Group : </b><code>{hmm.title}</code>"
    if full is not None:
        resalt += (
            f"\n<b>From : </b> 👤{_format.htmlmentionuser(full.first_name , full.id)}"
        )
    if messaget is not None:
        resalt += f"\n<b>Message type : </b><code>{messaget}</code>"
    else:
        resalt += f"\n<b>Message : </b>{event.message.message}"
    resalt += f"\n<b>Message link: </b><a href = 'https://t.me/c/{hmm.id}/{event.message.id}'> link</a>"
    if not event.is_private:
        await event.client.send_message(
            Config.PM_LOGGR_BOT_API_ID,
            resalt,
            parse_mode="html",
            link_preview=False,
        )


@bot.on(admin_cmd(outgoing=True, pattern=r"save(?: |$)(.*)"))
async def log(log_text):
    if BOTLOG:
        if log_text.reply_to_msg_id:
            reply_msg = await log_text.get_reply_message()
            await reply_msg.forward_to(BOTLOG_CHATID)
        elif log_text.pattern_match.group(1):
            user = f"#LOG / Chat ID: {log_text.chat_id}\n\n"
            textx = user + log_text.pattern_match.group(1)
            await log_text.client.send_message(BOTLOG_CHATID, textx)
        else:
            await log_text.edit("`What am I supposed to log?`")
            return
        await log_text.edit("`Logged Successfully`")
    else:
        await log_text.edit("`This feature requires Logging to be enabled!`")
    await asyncio.sleep(2)
    await log_text.delete()


@bot.on(admin_cmd(pattern="log$"))
async def set_no_log_p_m(event):
    if Config.PM_LOGGR_BOT_API_ID is not None:
        chat = await event.get_chat()
        if no_log_pms_sql.is_approved(chat.id):
            no_log_pms_sql.disapprove(chat.id)
            await edit_delete(
                event, "`logging of messages from this group has been started`", 5
            )


@bot.on(admin_cmd(pattern="nolog$"))
async def set_no_log_p_m(event):
    if Config.PM_LOGGR_BOT_API_ID is not None:
        chat = await event.get_chat()
        if not no_log_pms_sql.is_approved(chat.id):
            no_log_pms_sql.approve(chat.id)
            await edit_delete(
                event, "`Logging of messages from this chat has been stopped`", 5
            )


CMD_HELP.update(
    {
        "logchats": "**Plugin : **`logchats`\
        \n\n•  **Syntax : **`.save`\
        \n•  **Function : **__Saves tagged message in private group .__\
        \n\n•  **Syntax : **`.log`\
        \n•  **Function : **__By default will log all private chat messages if you use .nolog and want to log again then you need to use this__\
        \n\n•  **Syntax : **`.nolog`\
        \n•  **Function : **__Stops logging from a private chat or group where you used__"
    }
)
