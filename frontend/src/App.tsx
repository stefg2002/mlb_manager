// import { useState, useEffect } from "react"
// import Login from './Login/Login.tsx'
import router from './router'
import { RouterProvider } from "@tanstack/react-router";

function App() {
  
  return(
    <>
      <RouterProvider router={router}/>
    </>
  );
  
}

export default App
