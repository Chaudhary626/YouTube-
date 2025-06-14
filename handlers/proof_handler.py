def register(bot):
    from database import get_task_for_user, submit_proof

    @bot.message_handler(commands=["proof"])
    def proof_prompt(message):
        task = get_task_for_user(message.from_user.id)
        if not task:
            bot.send_message(message.chat.id, "You don't have an active task assigned. Use /match to get one.")
            return
        bot.send_message(message.chat.id, "Upload your <b>screen recording</b> as video or file to prove you helped.")

    @bot.message_handler(content_types=['video', 'document'])
    def receive_proof(message):
        task = get_task_for_user(message.from_user.id)
        if not task:
            return
        file_id = message.video.file_id if message.video else message.document.file_id
        submit_proof(task[0], file_id)
        bot.send_message(message.chat.id, "Proof received! Now wait for the video owner to verify it using /verify.")