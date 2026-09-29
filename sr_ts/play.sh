#!/bin/bash

MODE=$1
FILE_BASE=$2

if [ "$MODE" == "record" ]; then
    echo "🎤 Recording started... Press [Enter] to STOP recording."
    
    # 1. Start the recording process in the background
    rec -q -c 1 -r 16000 "$FILE_BASE.wav" 2>/dev/null &
    REC_PID=$!
    
    # Fallback to arecord if rec tool isn't running
    if ! kill -0 $REC_PID 2>/dev/null; then
        arecord -q -f S16_LE -r 16000 -c 1 "$FILE_BASE.wav" 2>/dev/null &
        REC_PID=$!
    fi

    # 2. Block the script here and wait specifically for the user to hit [Enter]
    read -r

    # 3. Kill the background recording process instantly once Enter is pressed
    kill $REC_PID 2>/dev/null
    wait $REC_PID 2>/dev/null
    echo "🛑 Recording stopped."

elif [ "$MODE" == "play" ]; then
    echo "🔊 Playing response..."
    play -q "$FILE_BASE.mp3" 2>/dev/null || mpg123 -q "$FILE_BASE.mp3" || afplay "$FILE_BASE.mp3"
fi

