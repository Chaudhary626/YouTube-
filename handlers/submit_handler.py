from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def register(bot):
    from config import MAX_VIDEOS
    from database import user_video_count, insert_video

    user_states = {}

    @bot.message_handler(commands=['submit'])
    def handle_submit(message):
        if user_video_count(message.from_user.id) >= MAX_VIDEOS:
            bot.send_message(message.chat.id, "You have reached the maximum of 5 videos. Use /videos to remove one before submitting a new video.")
            return
        user_states[message.from_user.id] = {}
        bot.send_message(message.chat.id, "Send your <b>video thumbnail URL</b>:")
        bot.register_next_step_handler(message, get_thumbnail)

    def get_thumbnail(message):
        user_states[message.from_user.id]['thumbnail'] = message.text.strip()
        bot.send_message(message.chat.id, "Send your <b>video title</b>:")
        bot.register_next_step_handler(message, get_title)

    def get_title(message):
        user_states[message.from_user.id]['title'] = message.text.strip()
        bot.send_message(message.chat.id, "Send your <b>video duration in seconds</b> (max 300):")
        bot.register_next_step_handler(message, get_duration)

    def get_duration(message):
        try:
            duration = int(message.text.strip())
            if duration > 300 or duration <= 0:
                raise ValueError
            user_states[message.from_user.id]['duration'] = duration
        except:
            bot.send_message(message.chat.id, "Invalid duration. Please send a number ≤ 300.")
            bot.register_next_step_handler(message, get_duration)
            return
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔗 Direct Link", callback_data="submit_method_link"),
            InlineKeyboardButton("🔍 Manual Search", callback_data="submit_method_manual")
        )
        bot.send_message(message.chat.id, "Choose how others should find your video:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("submit_method_"))
    def choose_method(call):
        method = call.data.replace("submit_method_", "")
        user_states[call.from_user.id]['method'] = method
        if method == "link":
            bot.send_message(call.message.chat.id, "Send your <b>YouTube video link</b>:")
            bot.register_next_step_handler(call.message, get_link)
        else:
            user_states[call.from_user.id]['link'] = ""
            ask_actions(call.message)

    def get_link(message):
        user_states[message.from_user.id]['link'] = message.text.strip()
        ask_actions(message)

    def ask_actions(message):
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("👍 Like", callback_data="action_like"),
            InlineKeyboardButton("💬 Comment", callback_data="action_comment"),
            InlineKeyboardButton("🔔 Subscribe", callback_data="action_subscribe"),
            InlineKeyboardButton("🔗 Share", callback_data="action_share")
        )
        markup.row(InlineKeyboardButton("Done selecting actions", callback_data="actions_done"))
        user_states[message.from_user.id]['actions'] = []
        bot.send_message(message.chat.id, "Select all actions you want others to do (click as many as needed, then click Done):", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("action_"))
    def select_action(call):
        action = call.data.replace("action_", "")
        acts = user_states[call.from_user.id].setdefault('actions', [])
        if action not in acts:
            acts.append(action)
        bot.answer_callback_query(call.id, f"Added: {action.capitalize()}")

    @bot.callback_query_handler(func=lambda call: call.data == "actions_done")
    def finish_actions(call):
        actions = user_states[call.from_user.id].get('actions', [])
        if not actions:
            bot.answer_callback_query(call.id, "Select at least one action!")
            return
        bot.send_message(call.message.chat.id, "Write specific <b>instructions for users</b> (e.g. what to comment):")
        bot.register_next_step_handler(call.message, get_instructions)

    def get_instructions(message):
        user_states[message.from_user.id]['instructions'] = message.text.strip()
        data = user_states[message.from_user.id]
        insert_video(
            message.from_user.id,
            data['title'],
            data['thumbnail'],
            data['duration'],
            data['link'],
            ",".join(data['actions']),
            data['method'],
            data['instructions']
        )
        bot.send_message(message.chat.id, "✅ Video submitted!\n\nTo get engagement, you must first help another YouTuber. Use /match when ready.")
        user_states.pop(message.from_user.id, None)