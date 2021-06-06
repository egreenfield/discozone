import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { Server, Dance } from './model/Server';
import { Card, Table } from 'evergreen-ui';
import { DateTime } from 'luxon';

interface AppProps {
  server:Server;
}

function formatTime(t:string):string {
 // return DateTime.fromISO(t).toLocaleString(DateTime.DATETIME_SHORT)
  return DateTime.fromFormat(t,"yyyy-MM-dd HH:mm:ss",{ zone: "utc" }).setZone("local").toLocaleString(DateTime.DATETIME_SHORT)
}
function formatSong(s:string):string {
  let re = new RegExp("(.*\/)+([^\/\.]*)\.wav")
  let results = s.match(re);
  if (results && results.length >= 2)
    return results[2];
  else
    return s;
}

function App({server}: AppProps) {
  // Create the count state.
  const [count, setCount] = useState(0);
  const [dances, setDances] = useState([] as Array<Dance>);
  const [selectedDance, setSelectedDance] = useState(undefined as (Dance | undefined));
  // Create the counter (+1 every second).

  const dancesChanged = ()=> {setDances(server.dances)};

  useEffect(() => {
    server.addEventListener(Server.DANCES_CHANGED_EVENT,dancesChanged)
    server.load()
    return ()=>{server.removeEventListener(Server.DANCES_CHANGED_EVENT,dancesChanged)}
  }, [server])

  let loadingImage = (dances.length == 0)? <img src={logo} className="App-logo" alt="logo" /> : undefined;
  let sourceElt = (selectedDance != undefined)? <source src={"http://disco-videos.s3-website-us-west-2.amazonaws.com/"+selectedDance.videofile} type="video/mp4" />:undefined;
  // Return the App component.

  return (
    <div className="App" >
      <Card
        is="section"
        id="header"
        background="tint2"
        border="muted"
        marginLeft={12}
        marginY={24}
        paddingTop={12}
        paddingX={40}
      />
      <Card
        is="section"
        id="list"
        background="tint2"
        border="muted"
        marginLeft={12}
        marginY={24}
        paddingTop={12}
        paddingX={40}
        paddingBottom={12}
      >
      <Table className="danceTable" display="flex" flexDirection="column" >
        <Table.Head>
          <Table.TextHeaderCell>Time</Table.TextHeaderCell>
          <Table.TextHeaderCell>ID</Table.TextHeaderCell>
          <Table.TextHeaderCell>Song</Table.TextHeaderCell>
          <Table.TextHeaderCell>Comments</Table.TextHeaderCell>
        </Table.Head>
        <Table.VirtualBody flex="1 1 auto">
          {dances.map((dance) => (
            <Table.Row key={dance.id} isSelectable onSelect={() => {setSelectedDance(dance);return true;}}>
              <Table.TextCell>{formatTime(dance.time)}</Table.TextCell>
              <Table.TextCell>{dance.id}</Table.TextCell>
              <Table.TextCell>{formatSong(dance.song)}</Table.TextCell>
              <Table.TextCell>{dance.comments}</Table.TextCell>
              {/* <Table.TextCell>{profile.lastActivity}</Table.TextCell>
              <Table.TextCell isNumber>{profile.ltv}</Table.TextCell> */}
            </Table.Row>
          ))}
        </Table.VirtualBody>
      </Table>
      </Card>
      <Card
        is="section"
        id="details"
        background="tint2"
        border="muted"
        marginLeft={12}
        marginY={24}
        paddingTop={12}
        paddingX={40}
      >
        <video width="100%" controls>
          {sourceElt}
        </video>
      </Card>

  </div>
  );

}

export default App;
