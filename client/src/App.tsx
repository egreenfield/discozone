import React, { useState, useEffect } from 'react';
import logo from './logo.svg';
import './App.css';
import { Server, Video } from './model/Server';

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
        {loadingImage}
      </header>
    </div>
  );
}

export default App;
