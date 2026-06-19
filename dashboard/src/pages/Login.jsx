import { useState } from "react";
import api from "../services/api";

function Login({ onLogin }) {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = () => {
        api.post("/login", {
            username,
            password
        }).then((res) => {
            localStorage.setItem("token", res.data.access_token);
            onLogin();
        }).catch(() => {
            alert("Login failed");
        });
    };

    return (
        <div>
            <h2>Login</h2>

            <input placeholder="username" onChange={(e) => setUsername(e.target.value)} />
            <input placeholder="password" type="password" onChange={(e) => setPassword(e.target.value)} />

            <button onClick={handleLogin}>Login</button>
        </div>
    );
}

export default Login;