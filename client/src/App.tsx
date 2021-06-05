import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { Server, Video } from './model/Server';
import { Pane } from 'evergreen-ui';

interface AppProps {
  server:Server;
}

function App({server}: AppProps) {
  // Create the count state.
  const [count, setCount] = useState(0);
  const [videos, setVideos] = useState([] as Array<Video>);
  // Create the counter (+1 every second).

  const videosChanged = ()=> {setVideos(server.videos)};

  useEffect(() => {
    server.addEventListener(Server.VIDEOS_CHANGED_EVENT,videosChanged)
    server.load()
    return ()=>{server.removeEventListener(Server.VIDEOS_CHANGED_EVENT,videosChanged)}
  }, [server])

  let loadingImage = (videos.length == 0)? <img src={logo} className="App-logo" alt="logo" /> : undefined;

  // Return the App component.
  return (
    <div className="App">
      <header className="App-header">
      <Pane
        is="section"
        ref={(ref) => console.log(ref)}
        background="tint2"
        border="muted"
        marginLeft={12}
        marginY={24}
        paddingTop={12}
        paddingX={40}
        width={120}
        height={120}
        cursor="help"
        onClick={() => alert('Works just like expected')}
      />
      </header>
    </div>
  );
}

export default App;
