
This script provides a way to create Twitch chatbots using [ConvoXML](https://github.com/BlaiseLabs/ConvoXML) for conversation modeling and TwitchIO for interacting with the Twitch chat.

## Prerequisites

Before using this script, make sure you have the following in place:

- Python environment with necessary packages installed (see `requirements.txt`).
- Twitch account and access to a Twitch channel where you want to deploy the bot.
- API tokens for the Twitch accounts and bots you intend to use.

## Getting Started

1. Clone or download the repository to your local machine.

2. Modify the `twitch.xml` file to define your conversation model. You can specify roles, actions, and triggers in the XML file to control the chatbot's behavior.

3. Update the `token_file` paths in the XML file to point to the correct API token files for your Twitch accounts and bots.

4. Run the main script to start your Twitch chatbot. Here's how to run it:

   ```bash
   python main_script.py
   ```

## Understanding the Script


           +---------------------------------------------------+
           |                                                   |
           |             Twitch Chat Script with                |
           |           ConvoXML and TwitchIO Bot               |
           |                                                   |
           +-------------------+-------------------------------+
                               |
                               |
    +--------------------------v--------------------------+
    |                                                       |
    |                Twitch Channel (Twitch Chat)            |
    |                                                       |
    | +--------------+  +--------------+  +--------------+   |
    | |   Viewer 1  |  |   Viewer 2  |  |   Viewer 3  |   |
    | |              |  |              |  |              |   |
    | |              |  |              |  |              |   |
    | +--------------+  +--------------+  +--------------+   |
    |                                                       |
    +---------------------------|---------------------------+
                                |
                                | Twitch Messages
                                |
    +---------------------------v---------------------------+
    |                                                       |
    |                   TwitchFeed (TwitchIO Bot)           |
    |                                                       |
    | +---------------------------------------------------+ |
    | |                       TwitchIO                      | |
    | |                                                   | |
    | |  +-------------+  +-------------+  +-------------+ | |
    | |  |   Agent 1  |  |   Agent 2  |  |   Agent 3  | | |
    | |  |             |  |             |  |             | | |
    | |  |             |  |             |  |             | | |
    | |  +-------------+  +-------------+  +-------------+ | |
    | |                                                   | |
    | +---------------------------------------------------+ |
    |                                                       |
    +---------------------------|---------------------------+
                                |
                                | Chatbot Actions and Messages
                                |
    +---------------------------v---------------------------+
    |                                                       |
    |      AsyncConvo (ConvoXML Conversation Engine)        |
    |                                                       |
    | +---------------------------------------------------+ |
    | |                ConvoXmlParser                     | |
    | |                                                   | |
    | |  +-------------+  +-------------+  +-------------+ | |
    | |  |   Agent 1  |  |   Agent 2  |  |   Agent 3  | | |
    | |  |             |  |             |  |             | | |
    | |  |             |  |             |  |             | | |
    | |  +-------------+  +-------------+  +-------------+ | |
    | |                                                   | |
    | +---------------------------------------------------+ |
    |                                                       |
    +-------------------------------------------------------+



- `twitch.xml`: This file defines the conversation model using ConvoXML. It specifies roles, actions, and triggers for your Twitch chatbot.

- `TwitchBotInterface`: This class extends the TwitchIO `Client` and handles Twitch chat interactions. It sends and receives messages from the Twitch channel.

- `TwitchMod`: This class represents the Moderator role in the conversation. It decides the next action based on predefined triggers and intervals.

- `TwitchAgentMixIn` and `TwitchAgent`: These classes enable Twitch messaging for any Agent subclass. You can use the `TwitchAgent` class to create your chatbot agents, extending it with custom logic as needed.

- `TwitchFeed`: This class handles incoming Twitch chat messages and stores them in an SQLite database. It also manages communication between chatbots and the Twitch channel.

- `AsyncConvo`: This class extends the ConvoXmlParser and handles the asynchronous execution of chatbot actions based on the conversation model defined in `twitch.xml`.

## Customizing Your Chatbot

To customize your Twitch chatbot, you can:

- Modify the conversation model in `twitch.xml` to define different roles, actions, and triggers for your chatbot interactions.

- Create custom chatbot agents by extending the `TwitchAgent` class and implementing the `execute` method with your custom logic.

- Adjust the intervals and behavior of the Moderator role in the `TwitchMod` class to control when chatbot actions occur.

## License

Copyright (c) 2023 Blaiselabs

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Acknowledgments

- [TwitchIO](https://github.com/TwitchIO/TwitchIO): The Python library used for interacting with Twitch chat.

- [ConvoXML](https://github.com/TwitchIO/BlaiseLabs/ConvoXML): The ConvoXML framework for modeling conversations.

## Contact

If you have any questions or need assistance, feel free to reach out to [Your Contact Information].

Happy bot building!