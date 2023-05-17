# Meshtastic_File_Transfer
System which can be used to send arbitrary binary data files over Meshtastic of a size up to 
59kb at a rate of about 50 bytes/s which is about as fast as a room full of people on morse code.

This method of communication can be used by any platform and makes use of a relatively simple but 
reliable communication protocol as described below.
(Sender[S:] and Receiver[R:])

| Packet Type                                       | Content Description                                              |
|---------------------------------------------------|------------------------------------------------------------------|
| S: Initial Req.                                   | text: !fcom,file:r"file_name",packets:(# Packets),id:(id)        |
| R: Accept Transfer                                | Data: bytes(f, c, o, m, (file_id), 1)                            |
| S: Send data in chunks                            | Data: bytes((file_id), (Packet_Index), 232 bytes max payload...) |
| S: Finished Transmitting                          | Data: bytes(f, c, o, m, (file_id), 2)                            |
| R: (If packets missing) Req. Retransmission       | Data: bytes(f, c, o, m, (file_id), 3, missing packet ids...)     |
| R: (If packets are all present) Transfer Finished | Data: bytes(f, c, o, m, (file_id), 4)                            |
| Finished Transmitting                             | NONE                                                             |

Note that Req. Retransmission packets should just cause the sender to send the missing packets then another Finished 
transmitting packet. This cycle will repeat until a com packet is missed or all the data packets are received.

Also, the file ID number must never be byte(f) or 102 in base 10.
#Instructions:Main_2way.py
- Plug in 2 Radios into a computer
- Type in the File name under 59kb in size locate in the "Files" Folder
- Run Main_2way.py
- Make sure the number of radios is 2 in the console as this may take a while to be the case
- Progress Bar should show up and begin filling if everything is working properly
