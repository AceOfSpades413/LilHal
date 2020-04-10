import discord
from discord.ext import commands
import random

client = commands.Bot(command_prefix='!')

tFile = open("token.txt", "r")
TOKEN = tFile.readline().strip("\n")
