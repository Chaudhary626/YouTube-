from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def register(bot):
    from database import assign_video_to_user, get_task_for_user, unassign_task

    @bot.message_handler(commands=["match"])
    def handle_match(message):
        if get_task_for_user(message.from_user.id):
            bot.send_message(message.chat.id, "You already have a task assigned. Complete it before getting a new one.")
            return
        vid = assign_video_to_user(message.from_user.id)
        if not vid:
            bot.send_message(message.chat.id, "No available tasks right now. Try again later!")
            return
        txt = (
            f"<b>Title:</b> {vid[2]}\n"
            f"<b>Duration:</b> {vid[4]}s\n"
            f"<b>Actions:</b> {vid[6]}\n"
            f"<b>Instructions:</b> {vid[8]}\n"
        )
        if vid[7] == "link":
            txt += f"<b>Link:</b> {vid[5]}"
        else:
            txt += "<b>Find this video manually by title/thumbnail.</b>"
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("❌ Not now", callback_data="unassign_task"))
        bot.send_photo(message.chat.id, vid[3], caption=txt, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data == "unassign_task")
    def unassign(call):
        unassign_task(call.from_user.id)
        bot.send_message(call.message.chat.id, "Task unassigned. Use /match when ready again.")
        bot.delete_message(call.message.chat.id, call.message.message_id)