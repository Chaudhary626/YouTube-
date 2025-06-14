def register(bot):
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        from database import add_user
        add_user(message.from_user.id, message.from_user.username)
        bot.send_message(
            message.chat.id,
            "<b>Welcome to the YouTube Growth Exchange Bot!</b>\n\n"
            "Grow your channel by helping others. For every video you want help with, "
            "you must help someone else first, and upload proof. All engagement is manually verified.\n\n"
            "<b>Rules:</b>\n"
            "• Only real engagement, no fake/bot views\n"
            "• Upload screen recordings as proof\n"
            "• 5-video submission limit\n"
            "• Use /submit to add a video\n"
            "• Use /match when ready to help others\n"
            "• Use /proof to submit your proof\n"
            "• Use /verify to check proofs for your videos\n"
            "• Use /report for invalid proofs\n"
            "\n<b>Ready?</b> Submit your video with /submit"
        )