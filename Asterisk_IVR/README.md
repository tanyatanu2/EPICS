# Asterisk IVR Prototype

This project contains the Asterisk-based IVR prototype developed as part of the EPICS health referral system.

## Current Implementation

- Asterisk 18.10.0 installed on Ubuntu 22.04
- SIP endpoint configured using PJSIP
- Linphone used as the SIP client on Android
- IVR extension `1000` configured
- DTMF-based menu implemented
- Option 1 plays a confirmation message
- Option 2 plays a goodbye message
- Option 3 provides a working echo test
- IVR successfully tested through a mobile SIP client

## IVR Flow

```text
Call 1000
    |
    v
Welcome / Menu
    |
    +---- Press 1 ----> Confirmation message
    |
    +---- Press 2 ----> Goodbye message
    |
    +---- Press 3 ----> Echo Test
