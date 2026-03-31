import { createFileRoute } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { useEffect, useState } from 'react';

export const Route = createFileRoute('/')({
  component: RouteComponent,
})

function RouteComponent() {
  const [data, setData] = useState({
      id: 0,
      username: "",
      email: ""
    });
  
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
        {/* <Login/> */}
        <h1 className="text-red-500 text-4xl">Welcome {data.username}</h1>
        <TanStackRouterDevtools/>
      </>
    );
}
