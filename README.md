<h1> PyObs Hub  </h1>
PyObsHub is an attempt to write tsomethign that combines a semi-hiarchical map of avaiulable astronomical instruments (camera, spectrometers, etc) with a set of scheduled and ad-hoc requests sunbmitted by users and scheduled by the server. 
It is intended for use by a single person over their kit of a single telescope. an astronomy club or society over multiple sets of kit or globally by an umlimited set of users across multiple time zones. 

It is inspired by : 
https://github.com/WorldWideTelescope/pywwt
https://github.com/lgrcia/prose
https://github.com/panoptes/POCS
https://github.com/larrylart/Unimap


<h2>Design </h2>
somewhat like this : 
<img src=./"multi site server system.png">
The GUi is the client to access and register instruments and observations. 
The server does all the hardwork of running the dynamic schedule or schedules and operating the remote instruments. 
The server implemetns the Alpaca and Indi remote protocols for ASCOM and INDI device control 

<h2>Licensing </h2>
Free to copy and re-use - I have. 
All re-use must include acknowledgement of source and a copy of the source. 

