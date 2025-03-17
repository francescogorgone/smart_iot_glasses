# Smart_IoT_Glasses
Object detection glasses created for Smart Internet of Things Devices course at uni

![botpic](https://github.com/user-attachments/assets/a87932e0-2a5a-4d84-9fe6-9948478c2aa8)

## Problem adressed

In the world, 253 million people live with visual impairments, of which 36 million are completely blind (Lancet Global Heart, 2017). The inability or limited capacity to orient oneself visually poses a significant challenge for many individuals worldwide. These individuals are often compelled to rely on a companion to alert them to potential dangers, or at the very least, to use a traditional aid such as a white cane.

## Objective

The aim of this project is to assist visually impaired individuals in navigating their environment by developing a system that enhances their safety during movement. By using a wearable device—such as a pair of glasses—it is possible to receive audio notifications about objects encountered along the way without the need for a companion or conventional aid.


## Proposed solution

The project involves using a Raspberry Pi connected to a webcam or camera sensor, along with a pair of earphones. Using the SSD MobileNet object detection model trained on the COCO dataset (over 330,000 images) (Microsoft, 2014), the glasses can associate the detected object with one of 80 object categories (called “classes”).
At this point, it is necessary to communicate what has been detected. For this purpose, eSpeak was used (eSpeak, 2007), a text-to-speech (TTS) program, a voice synthesis software capable of converting the detected information into words that the user can hear via the earphones connected to the Raspberry Pi. This communication is fundamental to inform the user about the type of object detected and its location. In order to understand where the object is located spatially, the frame (i.e. what the sensor or webcam captures) has been divided into 9 specifically renamed sections.

<img width="1316" alt="stopsign" src="https://github.com/user-attachments/assets/7e98b520-abaf-4d90-83c8-c27d7f89aa4f" />

In this case, the user will hear the TTS communicate the following via the earphones:

### “Stop sign detected with confidence 83% in position top center”

For the prototyping process, it was decided to use the English language to manage communications, but this can be easily modified according to the needs of the individual user by changing the text strings within the code.

Furthermore, the possibility of sharing this information with a potential companion via a Telegram bot message has also been provided.

<img width="195" alt="commands" src="https://github.com/user-attachments/assets/940a8b5c-a6e5-45e0-89ef-36056e0251c7" />

Through the /start command the bot will begin to periodically inform the user (the time interval between one message and the next can be modified from the respective file) with the exact same information that is
communicated via TTS since the latter and the bot have access to the same text file in which the readings are transcribed. With the /stop command, however, the bot will notify the user and interrupt communications.

<img width="631" alt=" bot_chat" src="https://github.com/user-attachments/assets/999edfb4-493b-4e5d-ab1f-7a9f985c0003" />

If the model fails to associate the identified object with a class, no class will be communicated to the user via TTS, but the presence of an object will still be indicated. The bot, however, will signal the presence of such an object with question marks:

<img width="359" alt="unknown_class" src="https://github.com/user-attachments/assets/d72366b7-b0c5-4b46-b512-13f38b4ce7d0" />

