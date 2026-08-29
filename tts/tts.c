#include <espeak-ng/speak_lib.h>
#include <stdio.h>

int main(void) {
    espeak_AUDIO_OUTPUT output = AUDIO_OUTPUT_SYNCH_PLAYBACK;
    char *path = NULL;
    void* user_data = NULL;
    unsigned int *identifier = NULL;
    
    int buflength = 500, options = 0;
    unsigned int position = 0, position_type = 0, end_position = 0;
    unsigned int flags = espeakCHARS_AUTO;

    espeak_Initialize(output, buflength, path, options);

    espeak_SetVoiceByName("hi");

    char text[] = "नमस्ते, यह एक ऑफ़लाइन टेक्स्ट टू स्पीच परीक्षण है।";

    printf("बोल रहा है: %s\n", text);
    
    espeak_Synth(text, buflength, position, position_type, end_position, flags, identifier, user_data);
    
    espeak_Synchronize();

    printf("समाप्त\n");
    return 0;
}

