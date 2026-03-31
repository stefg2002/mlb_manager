import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { useState, type ChangeEvent } from 'react';

export const Route = createFileRoute('/login')({
  component: RouteComponent,
})

function RouteComponent() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const [loginError, setLoginError] = useState(false);
    const [noLogin, setNoLogin] = useState(false);

    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const navigate = useNavigate({ from: '/login' })

    const sendData = async () => {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        };
        if (username != "" && password !=""){
            setNoLogin(false);
            try {
                const response = await fetch("http://localhost:8000/api/users/token", requestOptions);
                if(response.status === 403){
                    setLoginError(true);
                } else{
                    setLoginError(false);
                }
                if(response.ok){
                    const token = await response.json();
                    localStorage.setItem('authToken', token.access_token);
                    navigate({ to: '/'})
                }
            } catch (error){
                console.error('Error:', error);
            }
        } else {
            setNoLogin(true);
        }    
    };

    const usernameChange = (event: ChangeEvent<HTMLInputElement>) => {
        setUsername(event.target.value);
    };

    const passwordChange = (event: ChangeEvent<HTMLInputElement>) => {
        setPassword(event.target.value);
    };

    const LoginButton = () => {
        return(
            <button onClick={sendData} className="flex justify-center items-center cursor-pointer pt-1 pb-1 pl-2 pr-2 mt-2 ml-20 bg-red-400 hover:bg-red-700 text-white rounded-[25px] text-[25px]">
                LOGIN
            </button>
        );
    };
    
    const LoginErrorMessage = () => {
        if(loginError){
            return(
                <p className="text-red-500 ml-7">Invalid username or password</p>
            );
        }
        if (noLogin){
            return(
                <p className="text-red-500 ml-7">Please enter a username or password</p>
            );
        }
    }

    return(
        <>
            <input className="border border-black ml-10 mt-5" onChange={usernameChange} value={username}/>
            <input type="password" className="border border-black ml-10 mt-5" onChange={passwordChange} value={password}/>
            <LoginErrorMessage/>
            <LoginButton />
            <TanStackRouterDevtools/>
        </>
        
    );
}
