# Chatbot
Speech and Language Processing Lab 4

## Instructions to run:
```pip install -r Packages.txt (to get dependencies in)```

```cd src``` 

```python chatbot.py irc.freenode.net "#Channel_Name_Here" Bot_Nickname_Here```


## How it works

You can wait for the bot to reach out to you, or reach out to it
when you want. You can also ask for travel recommendations by asking 
questions similar to the form "Where should I visit?". The bot will
ask clarifying information about when you want to travel, and what
temperature you'd prefer. 

### added to project
- irc_socket.py to connect us and allow us to interact w/ IRC server
- chatbot.py, with core chatbot features
- Packages.txt, the dependency file
- travelRecs.py, with web scraping for travel recommendations


