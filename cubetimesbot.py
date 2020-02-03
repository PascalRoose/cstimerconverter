#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- style: pep-8 -*-
#
# ** Cube Times Bot **
# This bot can convert CsTimer files to Cube Timer (Android App by Mateus Fiereck) files.
#
# - Author: PascalRoose
# - Repo: https://github.com/PascalRoose/cubetimesbot.git
#

import logging
import os
import json
import datetime
import math

from dateutil.relativedelta import *

from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from dotenv import load_dotenv

# Enable logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()


# Convert milliseconds to minutes: MM:ss.mmm
def calc_time(ms):
    # Calculate the amount of minutes (60 sec x 1000 ms)
    minutes = math.floor(ms / (60 * 1000))
    # Calculate the amount of seconds
    seconds = math.floor((ms % (60 * 1000)) / 1000)
    # Get the modulo (left over)
    milliseconds = ms % 1000

    # Make sure minutes exists of 2 numbers. If there's only one number stick a zero in front
    if minutes < 10:
        minutes = '0' + str(minutes)
    # Make sure seconds exists of 2 numbers. If there's only one number stick a zero in front
    if seconds < 10:
        seconds = '0' + str(seconds)
    # Make sure milliseconds exists of 3 numbers. If there's only one number stick two zeros in front
    if milliseconds < 10:
        milliseconds = '00' + str(milliseconds)
    # Make sure milliseconds exists of 3 numbers. If there are only two number stick one zeros in front
    elif milliseconds < 100:
        milliseconds = '0' + str(milliseconds)

    # Return the right format using fstring
    return f'{minutes}:{seconds}.{milliseconds}'


def convert_times(inputdata):
    output_data = ''
    # Loop through all session check if the key is in the json object
    # Start with 1 so that the key is 'session1'. Add one every loop, so next loop key is 'session2'.
    sessions = [key for key in inputdata.keys() if "session" in key]
    for session in sessions:
        # Each session is an array of solves. Loop through the solves
        solves = inputdata[session]
        for solve in solves:
            time_solved = calc_time(solve[0][1])
            scramble = solve[1]

            # If there are more than 3 items in the solve array, this means there is an epoch time present
            if len(solve) > 3:
                epoch = solve[3]
                # Convert the epoch time to format 'YYYY-mm-dd HH:MM'
                timestamp = datetime.datetime.fromtimestamp(epoch)
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M', )
            # If there's no epoch time in the solve, we set the time to the current time
            else:
                # Convert the current time minus 3 months to format 'YYYY-mm-dd HH:MM'
                timestamp = datetime.datetime.now() - relativedelta(months=3)
                timestamp = timestamp.strftime('%Y-%m-%d %H:%M')
            # Create a new record (line) with fstring
            new_data_record = \
                f'{os.getenv("PREFIX")};{time_solved};{scramble};{timestamp};{os.getenv("POSTFIX")};\n'
            # Write the new record to the output data
            output_data += new_data_record
    return output_data


def get_inputdata(inputfile, filename):
    # Make sure the path to the input folder exists
    os.makedirs(os.getenv("INPUT_FOLDER"), exist_ok=True)
    # Create a filepath with the input folder and the filename
    filepath = os.path.join(os.getenv("INPUT_FOLDER"), filename)
    # Download the file
    inputfile.download(filepath)

    # Extract the data from the file. Open the file in readmode (r)
    with open(filepath, "r") as inputfile:
        inputdata = json.load(inputfile)
        inputfile.close()

    # Return the input data we extracted from the file
    return inputdata


def create_outputfile(outputdata, filename):
    # Create a new filename with the prefix 'converted-'
    filename = 'converted-' + filename
    # Make sure the path to the output folder exists
    os.makedirs(os.getenv("OUTPUT_FOLDER"), exist_ok=True)
    # Create a filepath with the input folder and the filename
    filepath = os.path.join(os.getenv("OUTPUT_FOLDER"), filename)

    # Create and write the output file (w+)
    with open(filepath, "w+") as outputfile:
        outputfile.write(outputdata)
        outputfile.close()

    # Return only the filepath
    return filepath


def process_times(update, _context):
    filename = update.message.document.file_name
    logger.info(filename)
    inputfile = update.message.document.get_file()
    inputdata = get_inputdata(inputfile, filename)

    outputdata = convert_times(inputdata)
    outputfile = create_outputfile(outputdata, filename)

    update.message.reply_document(open(outputfile, 'rb'))


def process_incorrectmessage(update, _context):
    if update.message.chat.type == 'private':
        update.message.reply_text(os.getenv('INCORRECT_MESSAGE'), parse_mode='Markdown')


# Send a message to users that start or simply type 'start' in private
def command_start(update, _context):
    if update.message.chat.type == 'private':
        update.message.reply_text(os.getenv('START_MESSAGE'), parse_mode='Markdown')


# Log Errors caused by Updates.
def error(update, _context):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater with the bottoken saved in .env
    updater = Updater(os.getenv('TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Handlers: what triggers the bot and how should it respond
    dp.add_handler(CommandHandler('start', command_start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), process_times))
    dp.add_handler(MessageHandler(~ Filters.document.mime_type("text/plain"), process_incorrectmessage))
    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
