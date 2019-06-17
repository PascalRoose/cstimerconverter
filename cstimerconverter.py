import sys
import os
import json
import datetime
import math

from dateutil.relativedelta import *

prefix = '3x3x3'
# midfix = '\\\",\\\"\\\",15'
postfix = 'no;no;no;1538321593773'


# Convert milliseconds to minutes: MM:ss.mmm
def calc_time(ms):
    # Calculate the amount of seconds. Round down (floor) to leave out the decimals
    seconds = math.floor(ms / 1000)
    # Get the modulo (left over)
    milliseconds = ms % 1000

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
    return f'00:{seconds}.{milliseconds}'


def main():
    # Check if there are exactly 3 arguments. Name of this script, input file, output file
    if len(sys.argv) != 3:
        raise Exception('Exactly 2 arguments must be provided: input file and output file. \n'
                        'Example: python3 cstimerconverter.py input.txt output.txt')

    # Check if the input file exists
    if not os.path.isfile(sys.argv[1]):
        raise FileExistsError(f'File "{sys.argv[1]}" does not exist. Make sure you use the correct arguments.\n'
                              f'Example: python3 cstimerconverter.py input.txt output.txt')

    # Load in the input file. Store in old_data as json object
    with open(sys.argv[1]) as input_file:
        old_data = json.load(input_file)
        input_file.close()

    with open(sys.argv[2], 'w+') as output_file:
        # Loop through all session check if the key is in the json object
        # Start with 1 so that the key is 'session1'. Add one every loop, so next loop key is 'session2'.
        session_id = 1
        while 'session' + str(session_id) in old_data:
            session_name = 'session' + str(session_id)
            # Each session is an array of solves. Loop through the solves
            solves = old_data[session_name]
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
                new_data_record = f'{prefix};{time_solved};{scramble};{timestamp};{postfix};\n'
                # Write the new record to the output file
                output_file.write(new_data_record)
            # Next session (+1)
            session_id += 1
        output_file.close()


if __name__ == '__main__':
    main()
