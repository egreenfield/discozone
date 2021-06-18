import './App.css';

import {
  Button,
  Card,
  CaretDownIcon,
  CircleIcon,
  DeleteIcon,
  Dialog,
  EditIcon,
  Group,
  IconButton,
  LinkIcon,
  StarIcon,
  Switch,
  SymbolCircleIcon,
  Table,
  TextInput,
  toaster,
} from 'evergreen-ui';
import { DateTime } from 'luxon';
import React, { SyntheticEvent, useEffect, useState } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';

import { Action, ActionMenu } from './ActionMenu';
import logo from './discoball.svg';
import { Dance, Server } from './model/Server';
import stu from './stu.png';
import useQueryParam from './useQueryParam';


interface AppProps {
  server:Server;
}

function makeDate(t:string):DateTime {
  return DateTime.fromFormat(t,"yyyy-MM-dd HH:mm:ss",{ zone: "utc" }).setZone("local");
}
function formatTime(t:DateTime):string {
  return t.toLocaleString(DateTime.TIME_SIMPLE)
}
function formatDateAsDay(t:DateTime):string {
  return t.toFormat("EEE MMMM d")
}
function formatDateAsTime(t:string):string {
  return formatTime(makeDate(t));
}

const songs = [
  "DiscoInferno.mp3",
  "freakout.mp3",
  "Funkytown.mp3",
  "IWillSurvive.mp3",
  "PlayThatFunky.mp3",
  "September.mp3",
  "unknown.mp3",
  "wearefamily.mp3",
  "ymca.mp3"
]
function getAudioFile(songname:string):string {

  let result = "";
    if(songname == null || songname == undefined || songname == "") {
      let idx = Math.floor(Math.random() * songs.length)
      let randomSong = songs[idx];
      result = `/audio/${randomSong}`;
    } else {
      result = `/audio/${formatSong(songname)}.mp3`;
    }
    return result;
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


const kFilterAll = "all";
const kFilterFavorited = "favorite";
const kFilterRejected = "rejected";
const kFilterUnwatched = "unwatched";

const MARK_REVIEWED_DELAY = 3000;
const FAST_PLAYBACK_SPEED = 5;


function App({server}: AppProps) {
  // Create the count state.
  const [dances, setDances] = useState([] as Array<Dance>);
  const [selectedDance, _setSelectedDance] = useState(undefined as (Dance | undefined));
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [editingComment, setEditingComment] = useState(false);
  const [filter,setFilter] = useQueryParam("filter",kFilterAll)
  const [canEdit,setCanEdit] = useQueryParam("edit","false")
  const [showDeleteConfirmation, setShowDeleteConfirmation] = React.useState(false)

  // Create the counter (+1 every second).
  const dancesChanged = ()=> {console.log("dances changed");  setDances(server.dances)};

  const startEditingComment = () => {
    if(canEdit == "true")
      setEditingComment(true)
  }

  const copyLink = async () => {
    if(selectedDance == undefined)
      return;

    let url = "http://disco-videos.s3-website-us-west-2.amazonaws.com/"+selectedDance.videofile;
    await navigator.clipboard.writeText(url);
    toaster.notify("link copied to clipboard");
  }

  let reviewTimerID:number | undefined = undefined;
  const startReviewTimer = (d:Dance) => {
    reviewTimerID = setTimeout(()=>{
      console.log(`+++ REVIEW TIMER ${reviewTimerID} FIRED`)
      setSelectedDance(server.markDanceReviewed(d));
    },MARK_REVIEWED_DELAY)
    console.log(`... REVIEW TIMER ${reviewTimerID} SET`)
  }
  const stopReviewTimer = () => {
    clearTimeout(reviewTimerID);
    console.log(`--- REVIEW TIMER ${reviewTimerID} CLEARED`)
  }

  const setSelectedDance = (d:Dance | undefined) => {
    if (d != selectedDance) {
      stopReviewTimer();
      if(d && d.reviewed == 0) {
        //startReviewTimer(d)
        setSelectedDance(server.markDanceReviewed(d));
      }
    }
    _setSelectedDance(d)
  }

  const markCurrentFavorite = () => {
    if(canEdit != "true") return;
    if (selectedDance) {
      setSelectedDance(server.setFavorite(selectedDance,selectedDance.favorite > 0? 0:1));
    }
  }

  const markCurrentRejected = () => {
    if(canEdit != "true") return;
    if (selectedDance) {
      setSelectedDance(server.setFavorite(selectedDance,selectedDance.favorite < 0? 0:-1));
    }
  }

  const refresh = () => {
    server.reload();
    setFilter(kFilterAll);
    setSelectedDance(undefined);
  }
  const deleteRejected = () => {
    if(canEdit != "true") return;
    server.deleteRejected();
    setFilter(kFilterAll);
    setSelectedDance(undefined);
  }

  const unmarkCurrent = () => {
    if(canEdit != "true") return;
    if (selectedDance) {
      setSelectedDance(server.setFavorite(selectedDance,0));
    }
  }


  useEffect(() => {
    server.addEventListener(Server.DANCES_CHANGED_EVENT,dancesChanged)
    server.load()
    return ()=>{server.removeEventListener(Server.DANCES_CHANGED_EVENT,dancesChanged)}
  }, [server])

  useHotkeys('f', markCurrentFavorite,{
      keydown:true
    },[selectedDance]
  );

  useHotkeys('x', markCurrentRejected,{
      keydown:true
    },[selectedDance]
  );


  const confirmDeleteRejected = () => {
    setFilter(kFilterRejected);
    setShowDeleteConfirmation(true);
  }

  const processAction = (action:Action) => {
    switch(action) {
      case Action.ShowAll: setFilter(kFilterAll); break;
      case Action.ShowFavorite: setFilter(kFilterFavorited); break;
      case Action.ShowRejected: setFilter(kFilterRejected); break;
      case Action.ShowUnwatched: setFilter(kFilterUnwatched); break;
      case Action.Refresh: refresh(); break;
      case Action.DeleteRejected: confirmDeleteRejected(); break;
    }
  }

  useHotkeys('j', () => {
      let nextIndex = 0;
      if (selectedDance) {
        nextIndex = selectedDance.__index+1;
      }
      if(nextIndex >= server.dances.length)
        return;
      let newSelectedDance = server.dances[nextIndex];
      setSelectedDance(newSelectedDance);
    },{
      keydown:true
    },[selectedDance]
  );

  useHotkeys('k', () => {
      if (selectedDance) {
        let nextIndex = selectedDance.__index-1;
        if(nextIndex < 0)
          return;
        let newSelectedDance = server.dances[nextIndex];
        setSelectedDance(newSelectedDance);
      }
    },{
      keydown:true
    },[selectedDance]
  );

  useHotkeys('r', () => {
      refresh()
    },{
      keydown:true
    }
  );

  // if(selectedDance != undefined && selectedDance.reviewed == 0) {
  //   setSelectedDance(server.markDanceReviewed(selectedDance));
  // }

  function applyDanceFilter(dances:Dance[],filter:string):Dance[] {
    switch(filter) {
      case kFilterFavorited:
        return dances.filter(d=>d == selectedDance || d.favorite > 0)
      case kFilterRejected:
        return dances.filter(d=>d == selectedDance || d.favorite < 0)
      case kFilterUnwatched:
          return dances.filter(d=>d == selectedDance || d.reviewed == 0)
      case kFilterAll:
      default:
        return dances;
    }

  }
  let audioPlayer:HTMLAudioElement | null = null;
  const onVideoPlaying = (e:SyntheticEvent<HTMLVideoElement,Event>) => {
    if(audioPlayer == null)
      return;
    audioPlayer.currentTime = e.currentTarget.currentTime;
    audioPlayer.play();
  }
  const onVideoStopped = (e:SyntheticEvent<HTMLVideoElement,Event>) => {
    console.log("VIDEO STOPPED");
    audioPlayer && audioPlayer.pause();
  }



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
          <Table.Row key={dance.id} isSelectable isSelected={selectedDance && (selectedDance.id == dance.id)} isHighlighted={selectedDance && (selectedDance.id == dance.id)}
          backgroundColor={dance.reviewed? "#FFFFFF":"#F5F5FA"}
          onSelect={() => {setSelectedDance(dance);return true;}}>
            <Table.TextCell flexBasis={42} flexShrink={0} flexGrow={0}>{
              dance.favorite > 0  ?   <StarIcon />          :
              dance.favorite < 0  ?   <DeleteIcon />        :
              dance.reviewed == 0 ?   <SymbolCircleIcon />  :
                                      undefined
            }</Table.TextCell>
            <Table.TextCell>{formatDateAsTime(dance.time)}</Table.TextCell>
            <Table.TextCell>{formatSong(dance.song)}</Table.TextCell>
            <Table.TextCell>{dance.comments}</Table.TextCell>
          </Table.Row>
        );
      } else {
        let date = row.date!;
        return (
          <Table.Row key={date.toLocaleString()} backgroundColor="#858585" height={30} color="#FFFFFF"
          textTransform="uppercase"
          fontWeight={800}
          >
            <Table.TextCell><span style={{color:"#FFFFFF"}}>{formatDateAsDay(date)}</span></Table.TextCell>
            <Table.TextCell></Table.TextCell>
            <Table.TextCell></Table.TextCell>
          </Table.Row>
        );
      }
    })
    return tags;
  }


  let danceTableContent =   (dances.length == 0)? (<img className="loadingImage" src={logo} width={60} height={60} />): (
    <Table className="danceTable" display="flex" flexDirection="column" >
      <Table.Head>
        <Table.TextHeaderCell flexBasis={42} flexShrink={0} flexGrow={0} ><StarIcon /></Table.TextHeaderCell>
        <Table.TextHeaderCell>Time</Table.TextHeaderCell>
        <Table.TextHeaderCell>Song</Table.TextHeaderCell>
        <Table.TextHeaderCell>Comments</Table.TextHeaderCell>
      </Table.Head>
      <Table.VirtualBody flex="1 1 auto">
        {makeRows(applyDanceFilter(dances,filter))}
      </Table.VirtualBody>
    </Table>
  )
  let videoSourceElt = (selectedDance != undefined)? <source src={"http://disco-videos.s3-website-us-west-2.amazonaws.com/"+selectedDance.videofile} type="video/mp4" />:undefined;
  let audioUrl = (selectedDance? getAudioFile(selectedDance.song):"nosong");
  let audioSourceElt = (selectedDance != undefined)?<source src={audioUrl} />:undefined;
  // Return the App component.
  return (
    <div className="App" >
      <Card
        is="section"
        id="header"
        background="tint2"
        border="muted"
        marginLeft={12}
        marginY={12}
        paddingTop={12}
        marginRight={12}
        paddingBottom={12}
        paddingX={40}
        textAlign="left"
        color="#696f8c"
        textTransform="uppercase"
        fontWeight={800}
        display="flex"
        flexDirection="row"
        alignItems="center"

      >
        <img src={stu} />
        <div style={{marginLeft:15, fontSize:56 }}>Disco Stu</div>
        <div style={{flex: "1 0 auto"}} />
        <ActionMenu server={server} onSelect={processAction} />
        <Dialog
          isShown={showDeleteConfirmation}
          title="The Party's Over"
          intent="danger"
          onCloseComplete={() => {setShowDeleteConfirmation(false)}}
          onConfirm={(close)=> { close(); deleteRejected()}}
          confirmLabel="Yup"
          cancelLabel="Nope"
          minHeightContent={10}
          hasClose={false}
        >
          Last Chance: Delete rejected dances?
        </Dialog>
      </Card>
      <Card
        is="section"
        id="list"
        background="tint2"
        border="muted"
        marginLeft={12}
        marginY={12}
        marginTop={0}
        paddingTop={12}
        paddingX={40}
        paddingBottom={12}
      >
        {danceTableContent}

      </Card>
      <Card
        is="section"
        id="details"
        background="tint2"
        border="muted"
        marginLeft={12}
        marginBottom={12}
        marginTop={0}
        paddingTop={12}
        marginRight={12}
        paddingX={40}
      >
        <div id="videoToolbar">
          <Switch checked={playbackSpeed > 1} onChange={(e)=> setPlaybackSpeed(e.target.checked? FAST_PLAYBACK_SPEED:1)} />&nbsp;&nbsp;speed up
        </div>
        <audio
          ref={(ref) => audioPlayer = ref}
          key={audioUrl + (selectedDance? selectedDance.id:"")}
          >
          {audioSourceElt}
        </audio>
        <video id="playback" width="100%"
          ref={(ref) => ref && (ref.playbackRate = playbackSpeed)}
          onPlay={onVideoPlaying} onPause={onVideoStopped}
          controls autoPlay key={(selectedDance && selectedDance.videofile) || "none"}>
          {videoSourceElt}
        </video>
        <div id="danceProperties">
          {editingComment?
            <TextInput value={selectedDance? selectedDance.comments:""} />:
            <div>{selectedDance? selectedDance.comments:""}</div>
          }
          <IconButton marginY={8} marginRight={12} icon={EditIcon} onClick={() => startEditingComment()} />
          <Group marginY={8}>
          <IconButton disabled={selectedDance == undefined} icon={StarIcon} isActive={selectedDance && selectedDance.favorite == 1} onClick={markCurrentFavorite}/>
          <IconButton disabled={selectedDance == undefined} icon={CircleIcon} isActive={selectedDance && selectedDance.favorite == 0} onClick={unmarkCurrent}/>
          <IconButton disabled={selectedDance == undefined} icon={DeleteIcon} isActive={selectedDance && selectedDance.favorite == -1} onClick={markCurrentRejected}/>

          </Group>
        </div>
        <div id="danceControls">
          <IconButton marginY={8} marginRight={12} icon={LinkIcon} onClick={() => copyLink()} />
          <Button marginY={8} marginRight={12} iconAfter={CaretDownIcon}>
            Download
          </Button>
        </div>
      </Card>

  </div>
  );

}

export default App;
