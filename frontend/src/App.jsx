import React, { useState, useEffect } from "react"
import Login from './Login/Login'

function App() {

  const [data, setData] = useState(Object);

  useEffect(() => {
    const getData = async () => {
      try {
        const token = localStorage.getItem('authToken');
        const options = {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
        const response = await fetch('http://localhost:8000/api/users/me', options);
        if(!response.ok){
          throw new Error('Unauthorized or network error');
        }
        const result = await response.json();
        console.log(result);
        setData(result);
      } catch (error){
        console.error('Error', error)
      }
    }
    getData(); 
  }, [])

  return(
    <>
      <Login/>
      <p>{data.username}</p>
    </>

  );
}

export default App
