import database
import bot

if __name__ == '__main__':
    server_info = database.get_server_info()
    
    client = bot.BotClient(server_info)
    client.run(server_info['bot_token'])