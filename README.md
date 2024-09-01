<h1> PyObs Hub  </h1>
PyObsHub is an attempt to write tsomethign that combines a semi-hiarchical map of avaiulable astronomical instruments (camera, spectrometers, etc) with a set of scheduled and ad-hoc requests sunbmitted by users and scheduled by the server. 
It is intended for use by a single person over their kit of a single telescope. an astronomy club or society over multiple sets of kit or globally by an umlimited set of users across multiple time zones. 

It is inspired by : 
<ul>
<li>https://github.com/WorldWideTelescope/pywwt</li>
<li>https://github.com/lgrcia/prose</li>
<li>https://github.com/panoptes/POCS</li>
<li>https://github.com/larrylart/Unimap</li>
</ul>


<h2>Design </h2>
The system wil look something like this. 
<img src="multi site server system.png">
The GUi is the client to access and register instruments and observations. 
The server does all the hardwork of running the dynamic schedule or schedules and operating the remote instruments. 
The server implemetns the Alpaca and Indi remote protocols for ASCOM and INDI device control 

Next steps
<ul>
  <li> Add Config CRUD through the GUI including saving and restoration at the server via A REST interface. </li>
  <li> Add graph display of objects to Server config tab in gui client. </li>
  <li>add object types panels to GUI for saving at server. </li>
  <li>Identify widgets for observation viewing and potentially processing</li>
  <li>Add HL script to define instrument processes at sites for operatoin of instruments.Support override attachable to specific sites.</li>
  <li>Add server peering to share observation requests amnd expose instruments </li>
  <li> Add user oauth2 token support for role based access against trusted peer servers. </li>
  <li> Add certificate support for server API over SSL.</li>
    
</ul>

<h2>Licensing </h2>
Free to copy and re-use - I have. 
All re-use must include acknowledgement of source and a copy of the source. 

