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
              // store token
            const token = res.data.access_token;
            
            localStorage.setItem("token", token);

            // store expiry time (200 minutes)
            const expiresAt = Date.now() + 200 * 60 * 1000;
            localStorage.setItem("expiresAt", expiresAt);

             // auto logout timer
            setTimeout(() => {
                localStorage.removeItem("token");
                localStorage.removeItem("expiresAt");
                window.location.href = "/"; // force back to login
            }, 200 * 60 * 1000);



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