import unittest
import time
from .TwitchXml import *


class TwitchTestAgent(TwitchAgentMixIn, TestAgent):
    pass

class TestTwitchAgentMixIn(unittest.TestCase):
    def test_attributes(self):
        # Create an instance of your class (e.g., TwitchAgent)
        instance = TwitchAgent(**{'channel':'', 'name': '', 'token_file': ''})
        
        # Check if the instance inherits from TwitchAgentMixIn
        self.assertTrue(issubclass(type(instance), TwitchAgentMixIn))

        # Check if the instance has the 'channel', 'name', and 'token_file' attributes
        self.assertTrue(hasattr(instance, 'channel'))
        self.assertTrue(hasattr(instance, 'name'))
        self.assertTrue(hasattr(instance, 'token_file'))

class TestTwitchMod(unittest.TestCase):
    def test_attributes(self):
        # Create an instance of your class (e.g., TwitchMod)
        instance = TwitchMod(**{'channel':'', 'name': '', 'token_file': ''})
        
        # Check if the instance inherits from AgentInterface (or any other base class it might inherit from)
        self.assertTrue(issubclass(type(instance), AgentInterface))

        # Check if the instance has the required attributes or methods
        self.assertTrue(hasattr(instance, 'context'))
        self.assertTrue(hasattr(instance.context, 'interval_mean'))
        self.assertTrue(hasattr(instance.context, 'interval_std'))
        self.assertTrue(hasattr(instance, 'execute'))
        self.assertTrue(hasattr(instance, 'channel'))
        self.assertTrue(hasattr(instance, 'name'))
        self.assertTrue(hasattr(instance, 'token_file'))
        
class TestAsyncParser(unittest.TestCase):
    
    def test_parser(self):
        """
        Test the twitch functionality of the AsyncConvo parser by 
        having an agent send a message and then comparing it with 
        the feed message. After that an audience member message is simulated 
        by having an agent send a message without a moderator
        """
        with open('./examples/test_twitch.xml') as f:
            xml_convo = f.read()
            
        parser = AsyncConvo(xml_convo, db_path='test_chat.db', agent_classes=[TwitchTestAgent])
        twitch_mod = parser.get_agent_by_role("Moderator")
        twitch_mod.context.interval_std = 1
        twitch_mod.context.mean = 15
        parser_result = self.run_parser(parser, twitch_mod)
        
        self.assertTrue(twitch_mod.thread_id == twitch_mod.children[0].thread_id)
        
         # confirm parser_result is in mod children
        self.assertTrue(parser_result[2] in [a.name for a in twitch_mod.children])
        
        # Create mock twitch user by using one of the parser's extra agents.
        mock_twitch_user = twitch_mod.children.pop(0)
        parser.queue = [twitch_mod, twitch_mod.children]
        mock_twitch_user.test_message = f"This is a test message from mock user {mock_twitch_user.role}"
        mock_twitch_user.send_message(mock_twitch_user.test_message)
        feed_result = self.run_parser(parser, twitch_mod)
        
        
        # confirm both thread_ids are the same as mods
        self.assertTrue(twitch_mod.thread_id == self.feed.thread_id)
        
        # confirm feed_result msg id is different from parser result
        self.assertTrue(parser_result[0] != feed_result[0])
        
        # confirm feed_result sender is not a child of twitch_mod
        self.assertFalse(feed_result[2] in twitch_mod.children)
        
        conn = sqlite3.connect('test_chat.db')
        cursor = conn.cursor()        
        cursor.execute(f'SELECT * FROM MESSAGES WHERE content LIKE "{mock_twitch_user.test_message}%" ORDER BY timestamp')
        self.assertTrue(len(cursor.fetchall()) > 0)
        
       
    def run_parser(self, parser, twitch_mod):
        
        t1 = threading.Thread(target=self.feed_thread, args=(twitch_mod,))
        t2 = threading.Thread(target=self.chat_loop, args=(parser,))
        t1.start()
        t2.start()
        time.sleep(30)
        print("exiting...")
        parser.context.exit = True
        row = self.get_last_msg(twitch_mod.db_path)
        return row
    
    def get_last_msg(self, db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Messages ORDER BY timestamp DESC LIMIT 1;
        ''')
        row = cursor.fetchall()[0]
        return row        
    
    def feed_thread(self, twitch_mod):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot_names = [agent.name for agent in twitch_mod.children]
        self.feed = TwitchFeed((twitch_mod.channel, twitch_mod.username, twitch_mod.token_file), thread_id=twitch_mod.thread_id,
                          bot_names=bot_names, db_path=twitch_mod.db_path)
        loop.run_until_complete(self.feed.start())
        time.sleep(30)
        loop.run_until_complete(self.feed.close())        
    
    def chat_loop(self, parser):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(parser.run_async())
        

    
                

if __name__ == "__main__":
    unittest.main()    
        