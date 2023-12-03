import twitchio
import random
import time
import numpy as np
import inspect
import asyncio
import threading
import sqlite3
from ConvoXml import AgentInterface, OpenAIAgent, ConvoXmlParser, TestAgent


class TwitchBotInterface(twitchio.Client):
    def __init__(self, channel, username, token_file, agent):      
        self.config = (self, channel, username, token_file)
        self.username = username
        self.channel_name = channel
        self.agent = agent
      
        with open(token_file, "r") as f:
            oauth_token = f.read().strip()
        super().__init__(oauth_token, initial_channels=[channel])
      

    async def get_twitch_channel(self, channel=None):
        channel = channel or self.channel_name
        await self.connect()
        return twitchio.Channel(name=channel, websocket=self._connection)
  
    async def send_twitch_message(self, message, username=None, channel=None):
        channel_obj = await self.get_twitch_channel(channel)
        if len(message) > 500:
            message = message[:500]
        await channel_obj.send(message)
      
    
class TwitchMod(AgentInterface):
    def __init__(self, **params):
        super().__init__(**params)
        self.context.interval_mean = 15
        self.context.interval_std = 5
        
        
    async def handle_feed(self):
        
    
            
        if not hasattr(self, 'feed'):            
            ft = threading.Thread(target=start_feed)
            ft.start()            
  
    async def execute(self):

        
        # Generate a random integer based on a mean interval length in seconds and a standard deviation
        random_seconds = np.random.normal(self.context.interval_mean, self.context.interval_std)
  
        # Convert the random seconds to an integer
        random_seconds_int = int(random_seconds)
        time.sleep(random_seconds_int)
  
        if self.children:
            # Randomly selecting a child agent to execute next
            next_agent = random.choice(self.children)
            print(f"{self.role} chose {next_agent.role}.")
            return next_agent.name

class TwitchAgentMixIn:
    """
    A mix-in that enables twitch messaging for any Agent subclass.
    The mix-in requires the channel and token_file attributes to be set via an agent's params and it 
    uses the name attribute for the bot's username.

    Example:
    class TwitchAgent(TwitchAgentMixIn, PalmAgent):
        pass
    """
    async def execute(self):
        self.role = self.name
        self.connection = sqlite3.connect(self.db_path)
        agent_bot = TwitchBotInterface(self.channel, self.name, self.token_file, self)
        response = self.send_message()
        await agent_bot.send_twitch_message(response)
        return response

class TwitchAgent(TwitchAgentMixIn, OpenAIAgent):
    pass

#TODO Convert convo history to basic sqlite commands
class TwitchFeed(twitchio.Client):
    def __init__(self, config, thread_id, bot_names, db_path):
        channel, username, token_file = config
        self.username = username
        with open(token_file, "r") as f:
            oauth_token = f.read().strip()
        super().__init__(oauth_token, initial_channels=[channel])
        self.channel_name = channel
        self.bot_names = bot_names
        self.thread_id = thread_id
        self.started = False
        self.db_path = db_path

    async def start(self):
        self.started = True
        await super().start()

    async def event_message(self, message):
        if message.author.name in self.bot_names:
            print('This is a message from an agent', message.author.name)

        elif message.author:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            cursor.execute(f"INSERT INTO Messages (thread_id, sender, content) VALUES (?, ?, ?)", 
                           (self.thread_id, message.author.name, message.content)
            )
            connection.commit()      
            print(f"Twitch Message added to thread: {self.thread_id} {message.author}: {message.content}")


class AsyncConvo(ConvoXmlParser):
    
    def __init__(self, *args, **kwargs):
        self.register_agent_class(TwitchAgent)
        self.register_agent_class(TwitchMod)
        super().__init__(*args, **kwargs)
        
        
  
    async def handle_agent_execution(self, agent):
        if inspect.iscoroutinefunction(agent.execute):
              return await agent.execute()
        else:
              return agent.execute()

    async def handle_branch(self, result, action_list):
        results = []
        for agent in action_list:
            if result in agent.role:
                new_result = await self.handle_agent_execution(agent)
                return new_result        
    
    async def run_async(self):
        queue = self.queue
        self.context.exit = False        
        while not self.context.exit:
            result = None
            for action in queue:
                if type(action) == list and result != None:
                    result = await self.handle_branch(result, action)
                else:
                    result = await self.handle_agent_execution(action)
                    
        
                    
    def setup_database(self, db_path=None):
        db_path = db_path or self.db_path
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Create a lock for database access
        db_lock = threading.Lock()

        try:
            # Acquire the lock before database access
            with db_lock:
                # Create the Messages table
                cursor.execute('''CREATE TABLE IF NOT EXISTS Messages (
                                  message_id INTEGER PRIMARY KEY,
                                  thread_id TEXT,
                                  sender TEXT,
                                  content TEXT,
                                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

                # Inserting some test data
                cursor.execute("INSERT INTO Messages (thread_id, sender, content) VALUES (?, ?, ?)", ('thread1', 'agent1', 'Test message 1'))
                cursor.execute("INSERT INTO Messages (thread_id, sender, content) VALUES (?, ?, ?)", ('thread1', 'agent2', 'Test message 2'))
                cursor.execute("INSERT INTO Messages (thread_id, sender, content) VALUES (?, ?, ?)", ('thread2', 'agent3', 'Test message 3'))

            # Commit the changes to the database
            connection.commit()

        except sqlite3.Error as e:
            # Handle the SQLite error here
            print("SQLite error:", e)

        finally:
            # Close the database connection in the finally block
            connection.close()

        return connection

async def main():
    with open('twitch.xml') as f:
        xml_convo = f.read()
    parser = AsyncConvo(xml_convo)
    
    def feed_thread(twitch_mod):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_names = [agent.name for agent in twitch_mod.children]
        feed = TwitchFeed((twitch_mod.channel, twitch_mod.username, twitch_mod.token_file), thread_id=twitch_mod.thread_id,
                          bot_names=bot_names, db_path=twitch_mod.db_path)
        loop.run_until_complete(feed.start())
    
    def chat_loop(parser):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(parser.run_async())

    t1 = threading.Thread(target=feed_thread, args=(parser.get_agent_by_role("Moderator"),))
    t2 = threading.Thread(target=chat_loop, args=(parser,))
#     asyncio.run(parser.run_async())
    t1.start()
    t2.start()
  

if __name__ == "__main__":
    await main()