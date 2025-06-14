from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def register(bot):
    from database import get_user_videos, delete_video

    @bot.message_handler(commands=["videos"])
    def handle_videos(message):
        videos = get_user_videos(message.from_user.id)
        if not videos:
            bot.send_message(message.chat.id, "You haven't submitted any videos yet.")
            return
        for v in videos:
            markup = InlineKeyboardMarkup()
            markup.row(InlineKeyboardButton("❌ Delete", callback_data=f"delete_video_{v[0]}"))
            txt = (
                f"<b>Title:</b> {v[2]}\n"
                f"<b>Duration:</b> {v[4]}s\n"
                f"<b>Actions:</b> {v[6]}\n"
                f"<b>Status:</b> {v[9]}"
            )
            bot.send_photo(message.chat.id, v[3], caption=txt, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_video_"))
    def delete_video_cb(call):
        vid = int(call.data.replace("delete_video_", ""))
        delete_video(vid, call.from_user.id)
        bot.answer_callback_query(call.id, "Video removed.")
        bot.delete_message(call.message.chat.id, call.message.message_id)