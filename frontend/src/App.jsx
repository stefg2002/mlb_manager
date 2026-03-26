import React, { useState, useEffect } from "react"
import Login from './Login/Login'

function App() {

  const [items, setItems] = useState({});
  const [dataIsLoaded, setDataIsLoaded] = useState(false);

  // useEffect(() => {
  //   fetch("http://localhost:8000/api/users/me", {
  //     method: 'GET',
  //     headers: {
  //       'Content-Type': 'application/json',
  //       'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzc0NDgyNzk3fQ.gzeGg4ZW3znqvCHIFMFUrFJ3LkDhEmk5BpBLmeKCXTM'
  //     }
  //   })
  //   .then((res) => res.json())
  //   .then((json) => {
  //     setItems(json);
  //     setDataIsLoaded(true);
  //   })
  // }, []);

  return(
    <>
      <Login/>
    </>

  );
}

export default App
