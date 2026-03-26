import { useState } from 'react'

function Login(){
    
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const sendData = async () => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        };

        try {
            const response = await fetch("http://localhost:8000/api/users/token", requestOptions);
            const data = await response.json();
            console.log(data);
        } catch (error){
            console.error('Error:', error);
        }

    };

    const click = () => {
        if(username != "" && password !=""){
            
        }
        else{
            alert("Please enter a value");
        }
    };

    const usernameChange = (event) => {
        setUsername(event.target.value);
    };

    const passwordChange = (event) => {
        setPassword(event.target.value);
    };

    const LoginButton = () => {
        return(
            <button onClick={sendData} className="flex justify-center items-center cursor-pointer m-10 bg-red-400 hover:bg-red-700 text-white rounded-[25px] text-[50px]">
                LOGIN
            </button>
        );
    };
    
    return(
        <>
            <input className="border border-black ml-10 mt-5" onChange={usernameChange} value={username}/>
            <input type="password" className="border border-black ml-10 mt-5" onChange={passwordChange} value={password}/>
            <LoginButton />
        </>
        
    );

}

export default Login