import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { Server, Dance } from './model/Server';
import { Card, Table } from 'evergreen-ui';
import { DateTime } from 'luxon';

interface AppProps {
  server:Server;
}

function makeDate(t:string):DateTime {
  return DateTime.fromFormat(t,"yyyy-MM-dd HH:mm:ss",{ zone: "utc" }).setZone("local");
}
function formatTime(t:DateTime):string {
 // return DateTime.fromISO(t).toLocaleString(DateTime.DATETIME_SHORT)
  return t.toLocaleString(DateTime.TIME_SIMPLE)
}
function formatDateAsDay(t:DateTime):string {
  return t.toFormat("EEE MMMM d")
}
function formatDateAsTime(t:string):string {
  return formatTime(makeDate(t));
}

function formatSong(s:string):string {
  let re = new RegExp("(.*\/)+([^\/\.]*)\.wav")
  let results = s.match(re);
  if (results && results.length >= 2)
    return results[2];
  else
    return s;
}


interface rowDance {
  type:string;
  dance?:Dance;
  date?:DateTime;
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


  function makeRows(dances:Dance[]) {
    let prevDate:DateTime|null = null;
    let rows = dances.reduce((rows,dance)=>{
      let danceDT = makeDate(dance.time)
      let danceDay = danceDT.set({hour:0,second:0,minute:0,millisecond:0})
      if (prevDate == null || prevDate < danceDay || prevDate > danceDay) {
        rows.push({type:"day",date:danceDay});
        prevDate = danceDay;
      }
      rows.push({type:"dance",dance:dance});
      return rows;
    },[] as Array<rowDance>)
    let tags = rows.map(row => {
      if(row.type == "dance") {
        let dance = row.dance!;
        return (
          <Table.Row key={dance.id} isSelectable onSelect={() => {setSelectedDance(dance);return true;}}>
            <Table.TextCell>{formatDateAsTime(dance.time)}</Table.TextCell>
            <Table.TextCell>{formatSong(dance.song)}</Table.TextCell>
            <Table.TextCell>{dance.comments}</Table.TextCell>
          </Table.Row>
        );
      } else {
        let date = row.date!;
        return (
          <Table.Row key={date.toLocaleString()} intent="warning"
          textTransform="uppercase"
          fontWeight={800}
          >
            <Table.TextCell>{formatDateAsDay(date)}</Table.TextCell>
            <Table.TextCell></Table.TextCell>
            <Table.TextCell></Table.TextCell>
          </Table.Row>
        );  
      }
    })
    return tags;
  }

  
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
        paddingBottom={12}
        paddingX={40}
        textAlign="left"
        color="#696f8c"
        textTransform="uppercase"
        fontWeight={800}
      >
        Disco Stu
      </Card>
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
          <Table.TextHeaderCell>Song</Table.TextHeaderCell>
          <Table.TextHeaderCell>Comments</Table.TextHeaderCell>
        </Table.Head>
        <Table.VirtualBody flex="1 1 auto">
          {makeRows(dances)}
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
