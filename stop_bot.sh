#!/bin/bash

ps aux | grep bot.py | grep -v grep | awk '{ print $2; }' | xargs kill -${2:-'TERM'}
