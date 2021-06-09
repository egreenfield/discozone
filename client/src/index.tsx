import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';
import { Server } from './model/Server';


let server = new Server("https://api.twofish.studio/")
server.load()
ReactDOM.render(
  <React.StrictMode>
    <App server={server}/>
  </React.StrictMode>,
  document.getElementById('root'),
);

// Hot Module Replacement (HMR) - Remove this snippet to remove HMR.
// Learn more: https://snowpack.dev/concepts/hot-module-replacement
if (import.meta.hot) {
  import.meta.hot.accept();
}
